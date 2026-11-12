"""SessionStart hook: a vendored fork that has fallen behind its upstream's main.

vendor/yomiyasu tracks nanaism/yomiyasu on the fork's own branch, and nothing in
this repository fetches the upstream, so the fork fell twelve commits behind,
Windows fixes among them, before anyone looked. At the start of a session in this
repository the hook asks GitHub for the upstream's main and, when the fork's HEAD
does not contain it, puts the count and the procedure into the session.

Prints the SessionStart output or nothing. A submodule not checked out, an
unreachable upstream or a git error passes in silence: the hook is a reminder,
not a gate.
"""
import json
import os
import subprocess
import sys

VENDORED = [('vendor/yomiyasu', 'https://github.com/nanaism/yomiyasu.git', 'main')]
TIMEOUT = 15

NOTICE = (
    '{path} is {count} commit{s} behind {url} {branch} ({sha}): the fork\'s HEAD does not contain it. '
    'Tell the user, and when they agree merge upstream {branch} into the fork\'s branch inside {path}, '
    'keeping the fork\'s own changes, then ship it as docs/CONTRIBUTING.md says under '
    '"A vendored plugin installs the commit its submodule records".'
)


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)


def behind(cwd, url, branch):
    """The upstream branch's sha and how many of its commits the fork's HEAD lacks, or None."""
    remote = git(cwd, 'ls-remote', url, f'refs/heads/{branch}')
    sha = remote.stdout.split()[0] if remote.returncode == 0 and remote.stdout.strip() else None
    if not sha or git(cwd, 'merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0:
        return None
    if git(cwd, 'fetch', '-q', url, branch).returncode != 0:
        return None
    count = git(cwd, 'rev-list', '--count', 'HEAD..FETCH_HEAD')
    return (sha, int(count.stdout)) if count.returncode == 0 else None


def notice(root, vendored=VENDORED):
    """One line per vendored fork behind its upstream, or None when every fork is current."""
    lines = []
    for path, url, branch in vendored:
        cwd = os.path.join(root, path)
        if not os.path.exists(os.path.join(cwd, '.git')):
            continue
        found = behind(cwd, url, branch)
        if found:
            sha, count = found
            lines.append(NOTICE.format(path=path, count=count, s='' if count == 1 else 's',
                                       url=url, branch=branch, sha=sha[:7]))
    return '\n'.join(lines) or None


def output(message):
    return {'systemMessage': message,
            'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': message}}


def main():
    root = os.environ.get('CLAUDE_PROJECT_DIR') or os.path.join(os.path.dirname(__file__), '..')
    try:
        message = notice(root)
    except (OSError, ValueError, subprocess.SubprocessError):
        return
    if message:
        sys.stdout.buffer.write(json.dumps(output(message), ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
