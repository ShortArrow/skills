"""Characterisation tests for hooks/wait-stop.py.

    python -m pytest tests/test_wait_stop.py
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'wait-stop.py')
spec = importlib.util.spec_from_file_location('wait_stop', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
verdict = hook.verdict


def prompt(text):
    return {'type': 'user', 'message': {'role': 'user', 'content': text}}


def use(use_id, name='Bash', **inp):
    return {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': use_id, 'name': name, 'input': inp}]}}


def result(use_id, text):
    return {'type': 'user', 'message': {'role': 'user', 'content': [
        {'type': 'tool_result', 'tool_use_id': use_id, 'content': text}]}}


def started(use_id, task_id):
    return [use(use_id, command='gh pr checks 7 --watch', run_in_background=True),
            result(use_id, f'Command running in background with ID: {task_id}. Output is being written to: x')]


def notified(use_id, task_id, status='completed'):
    return prompt(f'<task-notification>\n<task-id>{task_id}</task-id>\n<tool-use-id>{use_id}</tool-use-id>\n'
                  f'<status>{status}</status>\n</task-notification>')


def stop(message, entries, active=False):
    return verdict({'stop_hook_active': active, 'last_assistant_message': message}, entries)


PUSHED = [prompt('push して')]


def test_blocks_a_wait_on_ci_with_nothing_running():
    out = stop('push しました。\n\nCI の結果を待っています。', PUSHED)
    assert out['decision'] == 'block'
    assert 'timed-wait' in out['reason']


def test_blocks_a_promise_to_act_when_ci_passes():
    assert stop('PR #12 を出しました。CI が通ったらマージします。', PUSHED)


def test_blocks_english_waits():
    assert stop('Pushed.\n\nWaiting for CI.', PUSHED)
    assert stop('Once the checks pass, I will merge it.', PUSHED)


def test_a_background_watcher_still_running_lets_the_turn_end():
    assert stop('CI の結果を待っています。', PUSHED + started('u1', 'b1')) is None


def test_a_watcher_that_already_reported_does_not():
    entries = PUSHED + started('u1', 'b1') + [notified('u1', 'b1')]
    assert stop('まだ pending でした。CI の結果を待っています。', entries)


def test_a_killed_watcher_does_not():
    entries = PUSHED + started('u1', 'b1') + [notified('u1', 'b1', 'killed')]
    assert stop('CI が終わったら結果を見ます。', entries)


def test_a_background_subagent_or_a_scheduled_wakeup_lets_the_turn_end():
    agent = [use('u2', 'Agent', description='Run e2e', run_in_background=True),
             result('u2', 'Async agent launched successfully.')]
    assert stop('E2E が終わったらマージします。', PUSHED + agent) is None
    assert stop('CI を待っています。', PUSHED + [use('u3', 'ScheduleWakeup', delaySeconds=600)]) is None


def test_a_command_moved_to_the_background_by_its_timeout_counts_as_running():
    moved = [use('u4', command='gh run watch 9'),
             result('u4', 'Command did not complete within its 120s timeout and was moved to the background (ID: b4).')]
    assert stop('CI の結果を待っています。', PUSHED + moved) is None
    assert stop('CI の結果を待っています。', PUSHED + moved + [notified('u4', 'b4')])


def test_a_subagent_resumed_by_a_message_counts_until_it_hands_back():
    agent = [use('u5', 'Agent', description='Run e2e', run_in_background=True),
             result('u5', 'Async agent launched successfully.\nagentId: a5 (internal ID)'),
             notified('u5', 'a5')]
    resumed = agent + [use('u6', 'SendMessage', to='a5', message='one more scenario')]
    assert stop('サブエージェントの E2E が終わるのを待っています。', PUSHED + agent)
    assert stop('サブエージェントの E2E が終わるのを待っています。', PUSHED + resumed) is None
    handed_back = resumed + [prompt('<agent-message from="a5">[Subagent hand-back] done</agent-message>')]
    assert stop('サブエージェントの E2E が終わるのを待っています。', handed_back)


def test_a_status_word_that_is_not_a_wait_passes():
    assert stop('残りは、ビルドが止まるときの例外と、`rtt.ps1` の待ち時間です。', PUSHED) is None
    assert stop('次にやることは実データ経路検証で、実機の可用性待ちです。', PUSHED) is None
    assert stop('- #240：あなたのレビュー待ち\n- #239：3 つの決定待ち', PUSHED) is None
    assert stop('CI の完了を待っていた待機コマンドは、メモリ不足で止まりました。CI は終わっていました。', PUSHED) is None
    assert stop('そのセッションがまだリリースを待っているなら、この 2 点を送ります。', PUSHED) is None
    assert stop('残りは、CI で 1 度落ちた `Feature` の、5 秒待ちに頼る不安定なテストを直す。', PUSHED) is None


def test_a_subagent_still_waiting_on_its_own_work_counts_as_running():
    agent = [use('u7', 'Agent', description='Verify: e2e', run_in_background=True),
             result('u7', 'Async agent launched successfully.\nagentId: a7'),
             prompt('<task-notification>\n<task-id>a7</task-id>\n<tool-use-id>u7</tool-use-id>\n<status>completed</status>\n'
                    '<summary>Agent "Verify: e2e" is waiting on its own background work</summary>\n</task-notification>')]
    assert stop('反証役のテストが終わるのを待っています。', PUSHED + agent) is None


def test_a_task_started_long_before_the_turn_is_taken_as_gone():
    old = [dict(e, timestamp='2026-10-01T00:00:00Z') for e in started('u8', 'b8')]
    entries = old + [dict(prompt('push して'), timestamp='2026-10-14T21:00:00Z')]
    assert stop('CI の結果を待っています。', entries)


def test_a_wakeup_from_an_earlier_turn_does_not_count():
    entries = [use('u3', 'ScheduleWakeup', delaySeconds=600)] + PUSHED
    assert stop('CI を待っています。', entries)


def test_a_wait_on_the_user_is_not_this_hooks():
    assert stop('鍵を作り終わったら教えてください。', PUSHED) is None
    assert stop('ADR を Accepted にする件は、お返事を待っています。', PUSHED) is None
    assert stop('Let me know when the review is done.', PUSHED) is None


def test_reads_only_the_closing_and_skips_quotes():
    assert stop('CI を待っています。\n\nマージしました。', PUSHED) is None
    assert stop('止める言い回しは「CI の結果を待っています」です。', PUSHED) is None


def test_a_plain_report_passes():
    assert stop('テストはすべて通りました。', PUSHED) is None


def test_blocks_once_per_stop():
    assert stop('CI を待っています。', PUSHED, active=True) is None


def test_process_reads_the_transcript_and_fails_open(tmp_path):
    transcript = tmp_path / 's.jsonl'
    transcript.write_text('\n'.join(json.dumps(e) for e in PUSHED), encoding='utf-8')
    payload = {'transcript_path': str(transcript), 'last_assistant_message': 'CI を待っています。'}
    run = lambda p: subprocess.run([sys.executable, HOOK], input=json.dumps(p).encode('utf-8'),
                                   capture_output=True).stdout.decode('utf-8')
    assert json.loads(run(payload))['decision'] == 'block'
    payload['transcript_path'] = str(tmp_path / 'none.jsonl')
    assert run(payload) == ''


def test_blocks_a_handoff_whose_machine_work_starts_after_the_user_acts():
    """An approval the user alone can give, with a deployment behind it that nothing will watch.

    Releasing gitreant 0.4.0 ended here: the GitHub Release was published, the run
    sat on the release environment, and the turn told the user to approve it. The
    crates.io publish and the APT registry pickup both happen after that click, and
    no watcher was left for either, so "done" arrived before the release was out.
    """
    assert stop('次は、run 42350967813 で `release` 環境を承認して crates.io に公開してください。', PUSHED)
    assert stop('リリースのワークフローは、まだ release 環境の承認待ちです。承認すると公開が始まります。', PUSHED)
    assert stop('The run is waiting for approval in the release environment.', PUSHED)


def test_a_wait_on_the_user_alone_is_still_not_this_hooks():
    """The existing boundary holds: nothing machine-side follows these."""
    assert stop('鍵を作り終わったら教えてください。', PUSHED) is None
    assert stop('どちらにするか決まったら指示をください。', PUSHED) is None


def test_a_gated_handoff_is_told_not_to_poll_the_gate():
    """The advice differs by class: a watcher on CI, a declared fallback on a human gate.

    Starting `gh run watch` on a run parked for approval spins until the user clicks,
    which is why blocked-on-input gets its own reason.
    """
    gated = stop('`release` 環境を承認してください。承認すると公開が始まります。', PUSHED)
    assert 'blocked-on-input' in gated['reason']
    assert 'gh run watch' not in gated['reason']

    plain = stop('CI の結果を待っています。', PUSHED)
    assert 'gh run watch' in plain['reason']
    assert 'blocked-on-input' not in plain['reason']


def test_the_gate_advice_makes_the_watcher_conditional_on_where_the_work_runs():
    """The advice must not demand a watcher for work this session performs itself.

    Releasing razorshell 0.0.10 stalled on that demand: the turn asked for one
    `gh api` POST, and the closing was sent back six consecutive times for
    lacking a wakeup or a watcher. There was nothing to watch — the session is
    the actor and the reply is the resume — so no rewrite could pass.

    The hook cannot tell a local command from a remote deploy, and the same
    reason serves both, so it states the condition instead of asserting either:
    a watcher is owed only where the work proceeds without this session. The
    three substrings below are that condition's load-bearing clauses; matching
    them pins the wording, not the behaviour, because the verdict is unchanged.
    """
    gated = stop('`release` 環境を承認してください。承認すると公開が始まります。', PUSHED)
    assert 'this hook cannot tell' in gated['reason']
    assert 'one command this session runs itself' in gated['reason']
    assert 'Only work that proceeds without this session owes a watcher' in gated['reason']


def test_blocks_a_report_of_success_when_the_watcher_failed_or_was_killed():
    """A notification arriving is not the job succeeding; the status says which.

    This repository's own history holds the case: a background command named
    "Push, open draft PR and wait for CI" ended with status failed, exit code 1.
    Reading only "a notification came back" turns a dead watcher into a green CI.
    """
    for status in ('failed', 'killed'):
        entries = PUSHED + started('u1', 'b1') + [notified('u1', 'b1', status)]
        assert stop('CI はすべて通りました。マージできます。', entries), status
        assert stop('watcher が終了したので、CI は完了したものとみなします。', entries), status
        assert stop('The checks are green, so I merged it.', entries), status


def test_a_completed_watcher_lets_a_report_of_success_through():
    entries = PUSHED + started('u1', 'b1') + [notified('u1', 'b1', 'completed')]
    assert stop('CI はすべて通りました。マージできます。', entries) is None


def test_blocks_a_wait_on_work_running_outside_this_session():
    """A job started elsewhere has no background command here, so pending() sees nothing.

    The APT registry pickup after the gitreant 0.4.0 release is the case: the turn
    said it would happen within the hour and left no one watching.
    """
    assert stop('gh workflow run で pkg 側のワークフローを起動しました。', PUSHED)
    assert stop('APT レジストリは1時間以内に取り込むはずです。', PUSHED)
    assert stop('Cloudflare へのデプロイが進行中です。', PUSHED)
    assert stop('The deploy is in progress on Cloudflare.', PUSHED)


def test_remote_work_already_observed_is_a_report_and_passes():
    """The boundary for 'elsewhere': a promise about remote state blocks, a reading of it does not."""
    for message in ('デプロイが完了しました。すべて反映済みです。',
                    'レジストリに反映されたことを確認しました。',
                    'crates.io への公開が完了しました。',
                    'ワークフローの設定ファイルを直しました。',
                    'The deployment finished successfully.'):
        assert stop(message, PUSHED) is None, message


def test_each_class_gets_its_own_advice():
    """Four classes, four reasons: polling a human gate, a dead watcher and remote state differ."""
    broke = PUSHED + started('u1', 'b1') + [notified('u1', 'b1', 'failed')]
    assert 'never observed' in stop('CI はすべて通りました。', broke)['reason']
    assert 'has no keeper' in stop('Cloudflare へのデプロイが進行中です。', PUSHED)['reason']
    assert 'blocked-on-input' in stop('`release` 環境を承認してください。承認すると公開が始まります。', PUSHED)['reason']
    assert 'gh run watch' in stop('CI の結果を待っています。', PUSHED)['reason']


def test_blocks_a_command_handed_over_without_the_form_that_returns_its_output():
    """Asking the user to run a command, with no `!`, costs them the output twice.

    Measured over this machine's transcripts: of 159 such requests, 106 offered the
    `!` form and 53 did not. Where it was offered the output came back in the
    conversation; where it was not, the user ran it in another window and either
    pasted the output by hand or said only that it was done, leaving the agent to
    assume a result it never saw.
    """
    assert stop('次のコマンドを実行してください。\n\n```\nnpx wrangler login\n```', PUSHED)
    assert stop('`npm run deploy` を実行してください。', PUSHED)
    assert stop('Please run `gh auth login` and tell me when it is done.', PUSHED)


def test_a_command_offered_with_the_bang_form_passes():
    """With `!` the output lands in the conversation, so the next turn continues on evidence."""
    assert stop('次を実行してください。\n\n```\n! npx wrangler login\n```', PUSHED) is None
    assert stop('`! npm run deploy` を実行してください。', PUSHED) is None
    assert stop('先頭に `!` を付けて `gh auth login` を実行してください。', PUSHED) is None


def compacted(trigger='auto'):
    """The two entries Claude Code writes at a compaction: the metadata, then the summary."""
    return [{'type': 'system', 'compactMetadata': {'trigger': trigger, 'preTokens': 200896,
                                                   'postTokens': 9652, 'cumulativeDroppedTokens': 401840}},
            {'type': 'user', 'isCompactSummary': True, 'isVisibleInTranscriptOnly': True,
             'message': {'role': 'user', 'content': 'Summary: the earlier work is condensed here.'}}]


def test_blocks_a_label_whose_meaning_the_compaction_dropped():
    """A commitment carried across a compaction by a bare label is an obligation whose
    content no longer exists. Measured here: after a compaction this session carried
    "situations 5/7/10/12" through four consecutive closings while unable to say what
    the twelve were — only references to the enumeration survived it."""
    after = PUSHED + compacted()
    assert stop('未着手: situations 5/7/10/12 が残っています。', after)
    assert stop('残りは situation 7 と 10 です。', after)
    assert stop('Still open: items 5/7/10/12 from the earlier enumeration.', after)


def test_a_label_defined_in_the_same_turn_passes():
    """The failure is the lost referent, not the numbering. A label the closing itself
    explains needs no earlier context to act on."""
    after = PUSHED + compacted()
    assert stop('未着手: situation 7（レビュー返信が返らない待ち）が残っています。', after) is None
    assert stop('Still open: item 5, the review reply that never returns.', after) is None
    assert stop('situation 7 とは、レビュー返信が返らない待ちのことです。', after) is None
    assert stop('- situations 5/7/10/12 — レビュー/issue返信待ち', after) is None


def test_measured_against_this_session_s_own_closings():
    """Scored on 2026-11-10 against the four closings that carried "situations 5/7/10/12"
    after a compaction, and eight legitimate closings from the same session: three of the
    four blocked, no false positives.

    The fourth carries its own gloss ("— レビュー/issue返信待ち") and is a correct pass, not
    a miss. Japanese `は、` is deliberately not read as a definition: it marks a topic, so
    it introduces a remark about the label as readily as a gloss of it, and a miss is the
    cheaper error for a check that sends turns back.
    """
    after = PUSHED + compacted()
    blocked = [
        'situations 5/7/10/12 は未着手です。',
        '残りの未着手: permissions.allow の352件、Dependabot #62、situations 5/7/10/12。',
        'このうち situations 5/7/10/12 は、今日書いた待ちの規則と直接つながる領域です。',
    ]
    assert all(stop(s, after) for s in blocked)
    passes = [
        'push 完了: 83147fc..60a5bc8。51 skills / 0 errors。',
        'Dependabot #62 が残っています。',
        'PR #185 と #190 をマージしました。',
        'テスト11モジュール全PASS、portability 51 passed。',
        '3通送りました。どれも返信待ちではありません。',
    ]
    assert not any(stop(s, after) for s in passes)


def test_a_label_before_any_compaction_passes():
    """Without a compaction the defining content is still in the transcript."""
    assert stop('未着手: situations 5/7/10/12 が残っています。', PUSHED) is None
