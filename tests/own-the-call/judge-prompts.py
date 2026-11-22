"""Replays the own-the-call judges on fixed questions and closings.

The prompt hook on AskUserQuestion in .claude-plugin/marketplace.json and the
Stop hook hooks/own-the-call-judge.py are judged by a small model, so their
check is a sample, not a proof. This script sends each case to
`claude -p --model haiku` with the judge's own prompt (for Stop, the prompt
file with only the closing the hook would cut), n times, and prints the
verdicts that disagree with the expected one. Each call costs a fraction of a
cent; run it after any edit to either prompt.

    python tests/own-the-call/judge-prompts.py [n] [case-regex]

JUDGE_WORKERS sets how many judges run at once (default 6).
"""
import concurrent.futures as cf
import importlib.util
import json
import os
import re
import subprocess
import sys

MARKETPLACE = os.path.join(os.path.dirname(__file__), '..', '..', '.claude-plugin', 'marketplace.json')


def prompt_hook(event, matcher=None):
    with open(MARKETPLACE, encoding='utf-8') as f:
        plugins = json.load(f)['plugins']
    for plugin in plugins:
        for group in (plugin.get('hooks') or {}).get(event, []):
            if group.get('matcher') == matcher:
                for hook in group['hooks']:
                    if hook['type'] == 'prompt':
                        return hook['prompt']
    raise LookupError(event)


def stop_judge():
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'hooks', 'own-the-call-judge.py')
    spec = importlib.util.spec_from_file_location('own_the_call_judge', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ASK = prompt_hook('PreToolUse', 'AskUserQuestion')
STOP_JUDGE = stop_judge()
with open(STOP_JUDGE.PROMPT_FILE, encoding='utf-8') as f:
    STOP = f.read()


def q(header, question, *options):
    return {'header': header, 'question': question, 'multiSelect': False,
            'options': [{'label': l, 'description': d} for l, d in options]}


GROUND_ORG = 'Why ask: a push to the company organisation.'
GROUND_FACT = 'Why ask: a fact only the user holds.'

ASK_CASES = {
    'pass:org-push-owned': (True, [q('Push', "The parser fix is committed (c0ffee1); its test failed before and passes after. Push it to contoso/payments, the company organisation's repository? " + GROUND_ORG,
        ('Push (Recommended)', 'CI there runs on it and the team sees it. Cost: it is visible to the whole organisation; git revert c0ffee1 undoes the change, not the visibility.'),
        ('Wait', 'The fix stays local; the team keeps hitting the parser crash until it lands.'))]),
    'pass:fact-account': (True, [q('Target', 'Which Azure subscription should the staging app deploy to? ' + GROUND_FACT,
        ('Contoso-Dev', 'The one the CLI is logged in to now.'),
        ('Contoso-QA', 'Also in az account list; no file in the repository names either.'))]),
    'pass:fact-deadline': (True, [q('Due', 'When do you need the migration finished? ' + GROUND_FACT,
        ('This week', 'I would do the schema change and the backfill together.'),
        ('Next sprint', 'I would split it into two pull requests.'))]),
    'pass:outward-text': (True, [q('PR body', 'The pull request body is in pr-body.md (shown above). Post it to the upstream project as written? Why ask: text that leaves for other readers.',
        ('Post it (Recommended)', 'Follows the project template in full. Cost: maintainers read it as is; it can be edited later but notifications go out once.'),
        ('Hold', 'Nothing is posted; the maintainers wait on the fix with no description.'))]),
    'pass:irreversible': (True, [q('Drop', 'The old analytics table has had no reads for 90 days (query log). Drop it from the production database? Why ask: an action that cannot be undone.',
        ('Drop (Recommended)', 'Frees 40 GB. Cost: no backup covers it after the 30-day retention, so the data is gone for good.'),
        ('Keep', 'The storage cost stays.'))]),
    'pass:ux-security': (True, [q('Session', 'Sessions now last 30 days (auth/config.py:12), and the incident log shows two stolen cookies replayed a week after theft. Shorten them to 24 hours? Why ask: a trade-off between UX and security.',
        ('24 hours (Recommended)', 'A stolen cookie is good for a day, not a month. Cost: users sign in daily; changing the constant back undoes it.'),
        ('Keep 30 days', 'Fewer sign-ins; a stolen cookie stays usable for a month.'))]),
    'pass:on-hold': (True, [q('Rename', 'Last week you put the module rename on hold until you had asked the other maintainer; the two callers that blocked it were removed today in 3f2a1b0. Rename it now (six imports change)? Why ask: a matter the user put on hold.',
        ('Rename now (Recommended)', 'Six imports change; one revert undoes it.'),
        ('Keep holding', 'The old name stays and new code keeps importing it.'))]),
    'fail:evidence-no-pick': (False, [q('Fix', 'The crash is a null Logger in OrderService (stack trace line 42). How should I fix it?',
        ('Inject ILogger', 'Constructor injection.'),
        ('Null check', 'Guard before each call.'))]),
    'fail:no-pick': (False, [q('Approach', 'Which approach do you prefer for the retry logic?',
        ('Exponential backoff', 'Standard approach.'),
        ('Fixed delay', 'Simpler.'))]),
    'fail:benefit-only': (False, [q('Upgrade', 'Upgrade EF Core to 10.0?',
        ('Upgrade (Recommended)', 'Newer features and better performance.'),
        ('Stay', 'Keep the current version.'))]),
    'fail:continue-requested': (False, [q('Continue', 'You asked me to fix all three failing tests. I fixed the first one. Should I continue with the other two?',
        ('Continue (Recommended)', 'Fix the remaining two tests.'),
        ('Stop here', 'Leave them failing.'))]),
    'fail:bundled-decisions': (False, [
        q('Push', 'The new test failed before the fix and passes after (pytest: 41 passed). Push c0ffee1 to contoso/payments? ' + GROUND_ORG,
          ('Push (Recommended)', 'Other machines need a plugin update; git revert c0ffee1 undoes it.'), ('Wait', 'The fix stays local.')),
        q('Drop', 'The old analytics table has had no reads for 90 days. Drop it? Why ask: an action that cannot be undone.',
          ('Drop (Recommended)', 'Frees 40 GB; the data is gone for good.'), ('Keep', 'Storage cost stays.'))]),
    'pass:bundled-facts': (True, [
        q('Target', 'Which Azure subscription should it deploy to? ' + GROUND_FACT,
          ('Contoso-Dev', 'Logged in now.'), ('Contoso-Staging', 'Named in the README.')),
        q('Due', 'When do you need it? ' + GROUND_FACT,
          ('This week', 'One pull request.'), ('Next sprint', 'Two pull requests.'))]),
    'fail:public-push-no-ground': (False, [q('Push', 'The guard fix is committed (5d1e2f0); its two new tests failed before and pass after. Push it to ShortArrow/skills on GitHub, a public repository?',
        ('Push (Recommended)', 'Other machines pick it up at their next session. Cost: it is public at once; git revert 5d1e2f0 undoes the change, not what was seen.'),
        ('Wait', 'The fix stays local and the other machines keep the fail-open guard.'))]),
    'pass:public-push-outward': (True, [q('Push', 'The guard fix is committed (5d1e2f0); its two new tests failed before and pass after. Push it to ShortArrow/skills on GitHub, a public repository? Why ask: something that goes out (a push).',
        ('Push (Recommended)', 'Other machines pick it up at their next session. Cost: it is public at once; git revert 5d1e2f0 undoes the change, not what was seen.'),
        ('Wait', 'The fix stays local and the other machines keep the fail-open guard.'))]),
    'fail:no-ground-line': (False, [q('Target', 'Which Azure subscription should the staging app deploy to?',
        ('Contoso-Dev', 'The one the CLI is logged in to now.'),
        ('Contoso-Staging', 'Named in the README as the staging subscription.'))]),
    'fail:ground-outside-six': (False, [q('Cache', 'load_fixture takes 38 of the 41 s (profiled). Cache it once per session? Why ask: to be safe, since it changes the test setup.',
        ('Cache (Recommended)', 'Cuts the run to about 3 s. Cost: a mutation leaks between tests; deleting the scope line undoes it.'),
        ('Leave as is', 'Stays at 41 s.'))]),
    'fail:mislabel-restart': (False, [q('Restart', 'The plugin update needs a new session to load. Restart the session now? Why ask: an action that cannot be undone.',
        ('Restart (Recommended)', 'Loads the new hooks; the conversation resumes with --resume.'),
        ('Later', 'The old hooks stay until the next start.'))]),
    'fail:mislabel-mod-copy': (False, [q('Mod', 'Copy my status-line mod into ~/.claude/mods so it loads in every project? ' + GROUND_FACT,
        ('Copy (Recommended)', 'One file; deleting it undoes it.'),
        ('Keep it local', 'Only this project loads it.'))]),
    'fail:mislabel-filename': (False, [q('Name', 'What should the new helper script be called? ' + GROUND_FACT,
        ('sync-mods.py (Recommended)', 'Matches the verb-noun names beside it in scripts/.'),
        ('mods.py', 'Shorter.'))]),
    'fail:folder-agent-can-pick': (False, [q('Output', 'Where should the exported report be written? ' + GROUND_FACT,
        ('docs/reports/ (Recommended)', 'Where the two existing reports live.'),
        ('out/', 'Ignored by git, so the report is not committed.'))]),
}

LONG_BODY = '\n\n'.join(f'{i}. 修正 {i} を入れました。テストは修正前に落ち、修正後に通りました。対象は hooks/x{i}.py です。' * 2
                        for i in range(1, 12))

STOP_CASES = {
    'pass:proposal': (True, '検証の仕組みを入れてローカルでコミットしました（b8294ea）。\n\n**提案:** 会社の org の contoso/payments に push します。過去の記録で再生すると 1,106 回の公開操作のうち 541 回が拒否されます。費用として、サブエージェントを使ったセッションでは push の前に検証役を1回走らせる必要があります。取り消すときは `git revert b8294ea` で戻せます。\n聞く根拠：会社の org への push。\nよければ「ok」と返してください。'),
    'pass:report': (True, 'push して origin/main と揃いました。このマシンのプラグインも更新しました。反映には再起動が必要です。'),
    'pass:fact-ja': (True, 'ビルドは通りました。\n\n本番の接続文字列はどの Key Vault に入っていますか？名前を教えてください。\n聞く根拠：ユーザーしか知らない事実。'),
    'pass:proposal-en': (True, "All 40 tests pass.\n\nI propose pushing a4c6a80 to contoso/payments, the company organisation's repository: the hook test fails before the fix and passes after. Cost: other machines need a plugin update; `git revert a4c6a80` undoes it.\nWhy ask: a push to the company organisation.\nSay ok to push."),
    'pass:decided-and-reported': (True, 'キャッシュを入れました。load_fixture の 38 秒が 0.4 秒になり、スイートは 41 秒から 3 秒です。テスト間で同じオブジェクトを共有するので、書き換えるテストが出たらスコープの 1 行を消せば戻ります。'),
    'pass:long-closing': (True, LONG_BODY + '\n\n**提案:** 以上をまとめた c0ffee1 を会社の org の contoso/payments に push します。テストは全件通りました。費用として、他のマシンはプラグインの更新が必要で、`git revert c0ffee1` で戻せます。\n聞く根拠：会社の org への push。\nよければ「ok」と返してください。'),
    'fail:lean-no-cost': (False, '調査が終わりました。\n\nA案（キャッシュ）がよいと思います。進めてよいですか？'),
    'fail:options': (False, '原因は2つ考えられます。\n\n1. キャッシュを無効にする\n2. タイムアウトを延ばす\n\nどちらにしますか？'),
    'fail:shall-i': (False, 'テストは全部通りました。push しましょうか？'),
    'fail:benefit-only': (False, '修正しました。\n\n依存パッケージも最新版に上げると速くなります。上げてよいですか？'),
    'fail:bundled': (False, '3件対応しました。\n\n提案が3つあります。\n1. c0ffee1 を contoso/payments に push します。追加テストは修正前に落ち、修正後に通りました。他のマシンはプラグイン更新が必要で、`git revert c0ffee1` で戻せます。\n2. 本番の古い分析テーブルを削除します。90 日読まれていません。消すと戻せません。\n3. セッションの有効期限を 30 日から 24 時間に縮めます。盗まれた cookie の有効期間が短くなり、利用者は毎日サインインします。\n\n聞く根拠：会社の org への push、元に戻せない操作、UX とセキュリティのかね合い。\nよければ ok と返してください。'),
    'pass:one-ask-then-next': (True, '修正をコミットしました（c0ffee1）。\n\n**提案:** 会社の org の contoso/payments に push します。追加したテストは修正前に落ち、修正後に通りました。費用として、他のマシンはプラグインの更新が必要です。`git revert c0ffee1` で戻せます。\n聞く根拠：会社の org への push。\nよければ「ok」と返してください。\n\nREADME の古い記述は、push の後に別に提案します。'),
    'fail:public-push-no-ground': (False, 'guard の修正をコミットしました（5d1e2f0）。\n\n**提案:** 公開リポジトリ ShortArrow/skills に push します。追加した 2 件のテストは修正前に落ち、修正後に通りました。費用として、push した時点で公開され、`git revert 5d1e2f0` で変更は戻せても見られた事実は戻りません。\nよければ「ok」と返してください。'),
    'pass:public-push-outward': (True, 'guard の修正をコミットしました（5d1e2f0）。\n\n**提案:** 公開リポジトリ ShortArrow/skills に push します。追加した 2 件のテストは修正前に落ち、修正後に通りました。費用として、push した時点で公開され、`git revert 5d1e2f0` で変更は戻せても見られた事実は戻りません。\n聞く根拠：外に出るもの（push）。\nよければ「ok」と返してください。'),
    'fail:no-ground-line': (False, 'ビルドは通りました。\n\n本番の接続文字列はどの Key Vault に入っていますか？名前を教えてください。'),
    'fail:ground-outside-six': (False, 'キャッシュの案ができました。\n\n**提案:** load_fixture をセッション単位でキャッシュします。38 秒が 0.4 秒になります。費用として、テスト間でオブジェクトを共有します。スコープの 1 行を消せば戻ります。\n聞く根拠：念のため。\nよければ「ok」と返してください。'),
    'fail:mislabel-restart': (False, 'プラグインを更新しました。\n\n**提案:** 新しいフックを読み込むため、セッションを再起動します。会話は --resume で戻れます。\n聞く根拠：元に戻せない操作。\nよければ「ok」と返してください。'),
    'fail:mislabel-mod-copy': (False, 'status line の mod ができました。\n\n**提案:** この mod を ~/.claude/mods に写して、全プロジェクトで読み込ませます。ファイル 1 つで、消せば戻ります。\n聞く根拠：ユーザーしか知らない事実。\nよければ「ok」と返してください。'),
    'fail:mislabel-filename': (False, 'スクリプトの中身はできました。\n\nファイル名はどうしますか？ scripts/ の隣は sync-*.py の形なので、sync-mods.py を考えています。\n聞く根拠：ユーザーしか知らない事実。'),
    'fail:folder-agent-can-pick': (False, '変換スクリプトはできました。\n\n出力先のフォルダはどこにしますか？既存のレポートは docs/reports/ にあります。'),
}


def judge(prompt):
    run = subprocess.run(['claude', '-p', '--model', 'haiku', '--tools', '', '--disable-slash-commands', '--strict-mcp-config',
                          '--system-prompt', 'You evaluate hook conditions. Respond with one JSON object only.',
                          prompt], capture_output=True, text=True, encoding='utf-8', timeout=180)
    m = re.search(r'\{.*\}', run.stdout, re.S)
    try:
        return json.loads(m.group(0))
    except Exception:
        return {'ok': None, 'raw': run.stdout[-300:] + run.stderr[-300:]}


def jobs(n):
    for name, (want, questions) in ASK_CASES.items():
        payload = {'hook_event_name': 'PreToolUse', 'tool_name': 'AskUserQuestion', 'tool_input': {'questions': questions}}
        for i in range(n):
            yield 'ask:' + name, want, ASK.replace('$ARGUMENTS', json.dumps(payload, ensure_ascii=False))
    for name, (want, message) in STOP_CASES.items():
        for i in range(n):
            yield 'stop:' + name, want, STOP.replace('$CLOSING', STOP_JUDGE.closing(message))


def main(n, only=''):
    todo = [j for j in jobs(n) if re.search(only, j[0])]
    with cf.ThreadPoolExecutor(int(os.environ.get('JUDGE_WORKERS', '6'))) as ex:
        results = list(ex.map(lambda j: (j[0], j[1], judge(j[2])), todo))
    wrong = 0
    for name, want, got in results:
        ok = got.get('ok')
        wrong += ok != want
        mark = 'right' if ok == want else 'WRONG'
        print(f'{mark:5} {name:32} ok={ok} {got.get("reason", got.get("raw", ""))[:160]}')
    print(f'{len(results) - wrong}/{len(results)} right')
    return 1 if wrong else 0


if __name__ == '__main__':
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2, sys.argv[2] if len(sys.argv) > 2 else ''))
