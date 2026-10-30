"""Characterisation tests for hooks/upstream-behind.py, on local repositories standing in for GitHub.

    python -m pytest tests/test_upstream_behind.py
"""
import importlib.util
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'upstream-behind.py')
spec = importlib.util.spec_from_file_location('upstream_behind', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def git(cwd, *args):
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com',
                    '-c', 'commit.gpgsign=false', *args],
                   cwd=cwd, check=True, capture_output=True)


def commit(repo, message):
    git(repo, 'commit', '-q', '--allow-empty', '-m', message)


def setup(tmp_path):
    """An upstream repository on main and a project whose vendor/fork is a clone of it."""
    upstream = tmp_path / 'upstream'
    upstream.mkdir()
    git(upstream, 'init', '-q', '-b', 'main')
    commit(upstream, 'v1')
    root = tmp_path / 'project'
    (root / 'vendor').mkdir(parents=True)
    git(root / 'vendor', 'clone', '-q', str(upstream), 'fork')
    vendored = [('vendor/fork', str(upstream), 'main')]
    return upstream, root, vendored


def test_a_fork_that_contains_upstream_main_passes(tmp_path):
    upstream, root, vendored = setup(tmp_path)
    commit(root / 'vendor' / 'fork', 'a local rule')
    assert hook.notice(str(root), vendored) is None


def test_a_fork_behind_upstream_main_is_named_with_the_count(tmp_path):
    upstream, root, vendored = setup(tmp_path)
    commit(root / 'vendor' / 'fork', 'a local rule')
    commit(upstream, 'v2')
    commit(upstream, 'v3')
    message = hook.notice(str(root), vendored)
    assert 'vendor/fork' in message and '2 commits behind' in message
    assert 'A vendored plugin installs the commit its submodule records' in message


def test_an_unreachable_upstream_passes(tmp_path):
    upstream, root, vendored = setup(tmp_path)
    assert hook.notice(str(root), [('vendor/fork', str(tmp_path / 'none'), 'main')]) is None


def test_a_submodule_not_checked_out_passes(tmp_path):
    upstream, root, vendored = setup(tmp_path)
    assert hook.notice(str(root), [('vendor/absent', str(upstream), 'main')]) is None


def test_the_process_answers_in_the_session_start_schema(tmp_path):
    run = subprocess.run([sys.executable, HOOK], input=b'{}', capture_output=True,
                         env={**os.environ, 'CLAUDE_PROJECT_DIR': str(tmp_path)})
    assert run.returncode == 0 and run.stdout == b''
    out = hook.output('vendor/fork is 1 commit behind')
    assert out['hookSpecificOutput']['hookEventName'] == 'SessionStart'
    assert out['hookSpecificOutput']['additionalContext'] == 'vendor/fork is 1 commit behind'
    json.dumps(out)
