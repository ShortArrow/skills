"""Replays the own-the-call prompt hooks on fixed questions and closings.

The two prompt hooks in .claude-plugin/marketplace.json (PreToolUse on
AskUserQuestion, and Stop) are judged by a small model, so their check is a
sample, not a proof. This script sends each case to `claude -p --model haiku`
with the hook's own prompt, n times, and prints the verdicts that disagree
with the expected one. Each call costs a fraction of a cent; run it after any
edit to either prompt.

    python tests/own-the-call/judge-prompts.py [n]
"""
import concurrent.futures as cf
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


ASK = prompt_hook('PreToolUse', 'AskUserQuestion')
STOP = prompt_hook('Stop')


def q(header, question, *options):
    return {'header': header, 'question': question, 'multiSelect': False,
            'options': [{'label': l, 'description': d} for l, d in options]}


ASK_CASES = {
    'pass:decision-owned': (True, [q('Cache', 'The parser test takes 41 s because every case re-reads the 30 MB fixture (profiled: 38 s in load_fixture). Cache it once per session?',
        ('Session cache (Recommended)', 'Cuts the run to about 3 s. Cost: tests share one parsed object, so a test that mutates it leaks into others; undone by deleting the fixture scope line.'),
        ('Leave as is', 'Keeps tests isolated; the suite stays at 41 s.'))]),
    'pass:fact': (True, [q('Output', 'Where should the exported report be written?',
        ('docs/reports/ (Recommended)', 'Where the two existing reports live.'),
        ('out/', 'Ignored by git, so the report is not committed.'))]),
    'pass:fact-account': (True, [q('Target', 'Which Azure subscription should the staging app deploy to?',
        ('Contoso-Dev', 'The one the CLI is logged in to now.'),
        ('Contoso-Staging', 'Named in the README as the staging subscription.'))]),
    'pass:fact-deadline': (True, [q('Due', 'When do you need the migration finished?',
        ('This week', 'I would do the schema change and the backfill together.'),
        ('Next sprint', 'I would split it into two pull requests.'))]),
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
}

STOP_CASES = {
    'pass:proposal': (True, '検証の仕組みを入れてローカルでコミットしました（b8294ea）。\n\n**提案:** このまま push します。過去の記録で再生すると 1,106 回の公開操作のうち 541 回が拒否されます。費用として、サブエージェントを使ったセッションでは push の前に検証役を1回走らせる必要があります。取り消すときは `git revert b8294ea` で戻せます。よければ「ok」と返してください。'),
    'pass:report': (True, 'push して origin/main と揃いました。このマシンのプラグインも更新しました。反映には再起動が必要です。'),
    'pass:fact': (True, '変換スクリプトはできました。\n\n出力先のフォルダはどこにしますか？既存のレポートは docs/reports/ にあります。'),
    'pass:fact-ja': (True, 'ビルドは通りました。\n\n本番の接続文字列はどの Key Vault に入っていますか？名前を教えてください。'),
    'pass:proposal-en': (True, 'All 40 tests pass.\n\nI propose pushing a4c6a80 to origin/main: the hook test fails before the fix and passes after. Cost: other machines need a plugin update; `git revert a4c6a80` undoes it. Say ok to push.'),
    'fail:lean-no-cost': (False, '調査が終わりました。\n\nA案（キャッシュ）がよいと思います。進めてよいですか？'),
    'fail:options': (False, '原因は2つ考えられます。\n\n1. キャッシュを無効にする\n2. タイムアウトを延ばす\n\nどちらにしますか？'),
    'fail:shall-i': (False, 'テストは全部通りました。push しましょうか？'),
    'fail:benefit-only': (False, '修正しました。\n\n依存パッケージも最新版に上げると速くなります。上げてよいですか？'),
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
        payload = {'hook_event_name': 'Stop', 'stop_hook_active': False, 'last_assistant_message': message}
        for i in range(n):
            yield 'stop:' + name, want, STOP.replace('$ARGUMENTS', json.dumps(payload, ensure_ascii=False))


def main(n):
    todo = list(jobs(n))
    with cf.ThreadPoolExecutor(6) as ex:
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
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2))
