"""Install the private-names pre-push hook into one clone.

    python install.py [CLONE]    CLONE defaults to the current directory

The hook, repo-names.py and words.txt are copied into the clone's hooks
directory (`<git-common-dir>/hooks`), which git never pushes, so the
clone's history and its remote gain nothing. Run it again to refresh a copy it
wrote. It changes nothing and exits 1 where the copy would never run or a hook
it did not write would be lost: the clone's own config sets core.hooksPath; a
global core.hooksPath has no pre-push that calls the clone's `hooks/pre-push`;
or a pre-push it did not write is already there.
"""
import os
import shutil
import subprocess
import sys

MARK = '# guard-private-names'
CHAIN = 'hooks/pre-push'
HOOK = f"""#!/bin/sh
{MARK}: refuses a push that names a repository kept private.
PY=$(command -v python || command -v python3)
exec "$PY" "$(dirname "$0")/repo-names.py" "$@"
"""
COPIED = ('repo-names.py', 'words.txt')
HERE = os.path.dirname(os.path.abspath(__file__))


def _git(clone, *args):
    """stdout of git in clone, or None when git fails."""
    proc = subprocess.run(['git', '-C', clone, *args], capture_output=True, text=True, encoding='utf-8')
    return proc.stdout.strip() if proc.returncode == 0 else None


def _ours(path):
    try:
        with open(path, encoding='utf-8') as handle:
            return MARK in handle.read()
    except (OSError, UnicodeDecodeError):
        return False


def _hooks_path_stop(clone):
    """Why core.hooksPath keeps a hook in the clone's hooks directory from running, or None."""
    own = _git(clone, 'config', '--local', 'core.hooksPath') or _git(clone, 'config', '--worktree', 'core.hooksPath')
    if own:
        return f"the clone's own config sets core.hooksPath to {own}, so git never reads its hooks directory"
    shared = _git(clone, 'config', 'core.hooksPath')
    if not shared:
        return None
    shared_dir = os.path.expanduser(shared)
    if not os.path.isabs(shared_dir):
        shared_dir = os.path.join(_git(clone, 'rev-parse', '--show-toplevel') or clone, shared_dir)
    path = os.path.join(shared_dir, 'pre-push')
    try:
        with open(path, encoding='utf-8') as handle:
            calls = CHAIN in handle.read()
    except (OSError, UnicodeDecodeError):
        calls = False
    if not calls:
        return f"the global core.hooksPath {shared} has no pre-push that calls the clone's {CHAIN}"
    print(f"install: the global pre-push in {shared} calls the clone's {CHAIN}; the hook runs from there.")
    return None


def install(clone):
    """0 when the hook is in place; 1, with the reason on stderr, when nothing was changed."""
    common = _git(clone, 'rev-parse', '--git-common-dir')
    if common is None:
        print(f'install: {clone} is not a git clone; nothing changed.', file=sys.stderr)
        return 1
    stop = _hooks_path_stop(clone)
    if stop:
        print(f'install: {stop}; nothing changed. Add the call to repo-names.py to the pre-push that path runs.',
              file=sys.stderr)
        return 1
    hooks = os.path.join(common if os.path.isabs(common) else os.path.join(clone, common), 'hooks')
    pre_push = os.path.join(hooks, 'pre-push')
    if os.path.exists(pre_push) and not _ours(pre_push):
        print(f'install: {pre_push} is a hook this did not write; nothing changed. '
              'Add the call to repo-names.py to it.', file=sys.stderr)
        return 1
    os.makedirs(hooks, exist_ok=True)
    for name in COPIED:
        shutil.copyfile(os.path.join(HERE, name), os.path.join(hooks, name))
    with open(pre_push, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(HOOK)
    os.chmod(pre_push, 0o755)
    print(f'install: pre-push installed in {hooks}')
    return 0


if __name__ == '__main__':
    sys.exit(install(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()))
