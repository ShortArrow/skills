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
