"""Tests for skills/guard-private-names/scripts/install.py, written before it exists.

The installer copies the pre-push hook into a clone's own hooks directory,
which git never pushes. It stops without changing anything where a hook it did
not write would be shadowed or overwritten.
"""
import contextlib
import importlib.util
import os
import pathlib
import subprocess
import tempfile

SCRIPTS = os.path.join(os.path.dirname(__file__), '..', 'skills', 'guard-private-names', 'scripts')
spec = importlib.util.spec_from_file_location('install', os.path.join(SCRIPTS, 'install.py'))
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)

INSTALLED = ('pre-push', 'repo-names.py', 'words.txt')


ISOLATING = ('GIT_CONFIG_GLOBAL', 'GIT_CONFIG_NOSYSTEM')


@contextlib.contextmanager
def isolated(tmp_path):
    """Point git at an empty global config for the block, so this machine's hooksPath does not leak in.

    The config and any global hooks live in a directory of their own, outside the clone and removed afterwards.
    """
    saved = {k: os.environ.get(k) for k in ISOLATING}
    outside = tempfile.TemporaryDirectory()
    empty = os.path.join(outside.name, 'gitconfig')
    open(empty, 'w', encoding='utf-8').close()
    os.environ['GIT_CONFIG_GLOBAL'] = empty
    os.environ['GIT_CONFIG_NOSYSTEM'] = '1'
    try:
        yield
    finally:
        outside.cleanup()
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def repo(path):
    git(path, 'init', '-q', '-b', 'main')
    return path


def hooks(path):
    return path / '.git' / 'hooks'


def test_a_clean_clone_gets_the_hook_and_what_it_runs(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        assert install.install(str(r)) == 0
        for name in INSTALLED:
            assert (hooks(r) / name).is_file()
        assert (hooks(r) / 'words.txt').read_bytes() == open(os.path.join(SCRIPTS, 'words.txt'), 'rb').read()
        assert 'repo-names.py' in (hooks(r) / 'pre-push').read_text(encoding='utf-8')


def test_the_hook_is_not_tracked(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        install.install(str(r))
        assert git(r, 'status', '--porcelain') == ''


def test_a_set_hooks_path_stops_it_unchanged(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        git(r, 'config', 'core.hooksPath', '.husky')
        assert install.install(str(r)) != 0
        for name in INSTALLED:
            assert not (hooks(r) / name).exists()


def test_a_pre_push_it_did_not_write_stops_it_unchanged(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        (hooks(r) / 'pre-push').write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
        assert install.install(str(r)) != 0
        assert (hooks(r) / 'pre-push').read_text(encoding='utf-8') == '#!/bin/sh\nexit 0\n'
        assert not (hooks(r) / 'repo-names.py').exists()


def test_its_own_pre_push_is_replaced(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        install.install(str(r))
        (hooks(r) / 'repo-names.py').write_text('old\n', encoding='utf-8')
        assert install.install(str(r)) == 0
        assert (hooks(r) / 'repo-names.py').read_text(encoding='utf-8') != 'old\n'


def test_a_directory_that_is_not_a_clone_is_refused(tmp_path):
    with isolated(tmp_path):
        assert install.install(str(tmp_path)) != 0
        assert not (tmp_path / 'pre-push').exists()


def global_hooks(tmp_path, pre_push):
    """A global core.hooksPath whose pre-push holds pre_push (None: no pre-push there)."""
    temp = os.path.realpath(tempfile.gettempdir())
    assert os.path.realpath(os.environ.get('GIT_CONFIG_GLOBAL', '')).startswith(temp), 'global config not isolated'
    shared = pathlib.Path(os.environ['GIT_CONFIG_GLOBAL']).parent / 'hooks'
    shared.mkdir()
    if pre_push is not None:
        (shared / 'pre-push').write_text(pre_push, encoding='utf-8')
    subprocess.run(['git', 'config', '--global', 'core.hooksPath', shared.as_posix()], check=True)


CHAINS = '#!/bin/sh\nown_hook="$(git rev-parse --git-dir)/hooks/pre-push"\n[ -x "$own_hook" ] && exec "$own_hook" "$@"\n'


def test_a_global_hooks_path_that_calls_the_clone_hook_gets_it_installed(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        global_hooks(tmp_path, CHAINS)
        assert install.install(str(r)) == 0
        for name in INSTALLED:
            assert (hooks(r) / name).is_file()


def test_a_global_hooks_path_that_does_not_call_it_stops_it_unchanged(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        global_hooks(tmp_path, '#!/bin/sh\nexit 0\n')
        assert install.install(str(r)) != 0
        assert not (hooks(r) / 'pre-push').exists()


def test_a_global_hooks_path_without_a_pre_push_stops_it_unchanged(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        global_hooks(tmp_path, None)
        assert install.install(str(r)) != 0
        assert not (hooks(r) / 'pre-push').exists()


def test_isolation_restores_the_environment(tmp_path):
    before = {k: os.environ.get(k) for k in ISOLATING}
    with isolated(tmp_path):
        assert os.environ['GIT_CONFIG_NOSYSTEM'] == '1'
    assert {k: os.environ.get(k) for k in ISOLATING} == before


def test_a_relative_global_hooks_path_is_read_from_the_clone(tmp_path):
    with isolated(tmp_path):
        r = repo(tmp_path)
        (r / 'shared').mkdir()
        (r / 'shared' / 'pre-push').write_text(CHAINS, encoding='utf-8')
        subprocess.run(['git', 'config', '--global', 'core.hooksPath', 'shared'], check=True)
        assert install.install(str(r)) == 0
