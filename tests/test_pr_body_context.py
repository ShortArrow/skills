"""hooks/pr-body-context.sh injects the pull request body rule before a body is
posted, the review reply rule before a reply is posted, and nothing otherwise.

    python -m pytest tests/test_pr_body_context.py
    python tests/test_pr_body_context.py
"""
import json
import os
import shutil
import subprocess

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'pr-body-context.sh')
GIT_BASH = os.path.join(os.environ.get('ProgramFiles', 'C:/Program Files'), 'Git', 'bin', 'bash.exe')

BODY = 'A pull request body is about to be posted'
REPLY = 'A comment on a pull request or an issue is about to be posted'


def shell():
    """The bash Claude Code runs hooks with: Git Bash on Windows, where `bash` may be WSL's."""
    git_bash = os.environ.get('CLAUDE_CODE_GIT_BASH_PATH') or GIT_BASH
    return git_bash if os.name == 'nt' and os.path.exists(git_bash) else shutil.which('bash')


def injected(command):
    """The additionalContext the hook returns for a Bash call running `command`, or '' for none."""
    payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': command}})
    run = subprocess.run([shell(), SCRIPT], input=payload, capture_output=True, text=True, encoding='utf-8')
    assert run.returncode == 0, run.stderr
    if not run.stdout.strip():
        return ''
    return json.loads(run.stdout)['hookSpecificOutput']['additionalContext']


def test_a_body_command_gets_the_body_rule():
    for command in ('gh pr create --draft --title "fix: x" --body "y"',
                    'gh pr edit 42 --body-file body.md'):
        assert injected(command).startswith(BODY), command


def test_a_reply_command_gets_the_reply_rule():
    for command in ('gh pr comment 42 --body-file reply.md',
                    'gh pr review 42 --comment --body "see above"',
                    'gh api repos/o/r/pulls/42/comments -f body=x -F in_reply_to=1001',
                    'gh api repos/o/r/pulls/comments/1001/replies -f body=x',
                    'gh api -X POST repos/o/r/pulls/42/reviews -f body=x',
                    'gh api repos/o/r/issues/42/comments -f body=x',
                    "gh api graphql -f query='mutation { addPullRequestReviewComment(input: {}) { clientMutationId } }'",
                    "gh api graphql -f query='mutation { addComment(input: {}) { clientMutationId } }'"):
        assert injected(command).startswith(REPLY), command


def test_a_command_that_posts_nothing_gets_nothing():
    for command in ('gh pr view 42',
                    'gh pr review 42 --approve',
                    'gh pr list',
                    'gh api repos/o/r/pulls/42',
                    'gh api repos/o/r/pulls/42/comments',
                    'gh api repos/o/r/issues/42/comments --paginate',
                    "gh api graphql -f query='query { viewer { login } }'",
                    'git status'):
        assert injected(command) == '', command


if __name__ == '__main__':
    failed = 0
    for name, test in list(globals().items()):
        if name.startswith('test_') and callable(test):
            try:
                test()
                print('ok  ', name)
            except AssertionError as error:
                failed += 1
                print('FAIL', name, error)
    raise SystemExit(1 if failed else 0)
