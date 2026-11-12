"""Characterisation tests for hooks/update-own-plugins.py, on a temporary plugins directory.

A local repository stands in for the marketplace clone, a second one for the
remote, and `claude` is a recorder, so neither the real install nor GitHub is touched.

    python -m pytest tests/test_update_own_plugins.py
"""
import importlib.util
import json
import os
import subprocess

HOOK = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'update-own-plugins.py')
spec = importlib.util.spec_from_file_location('update_own_plugins', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

CATALOGUE = {'name': 'm', 'plugins': [
    {'name': 'a', 'source': './'},
    {'name': 'b', 'source': './'},
    {'name': 'vendored', 'source': {'source': 'url', 'url': 'https://example.invalid/v.git', 'sha': '1111'}},
]}


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com',
                           '-c', 'commit.gpgsign=false', *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def repo(path, message):
    """A repository holding the catalogue, its HEAD a commit named by message."""
    (path / '.claude-plugin').mkdir(parents=True)
    (path / '.claude-plugin' / 'marketplace.json').write_text(json.dumps(CATALOGUE), encoding='utf-8')
    git(path, 'init', '-q', '-b', 'main')
    git(path, 'add', '.')
    git(path, 'commit', '-q', '-m', message)
    return git(path, 'rev-parse', 'HEAD')


def setup(tmp_path, source, installed):
    """A plugins directory whose marketplace m is added from source, with a and b installed at installed."""
    clone = tmp_path / 'clone'
    plugins = tmp_path / 'plugins'
    plugins.mkdir()
    (plugins / 'known_marketplaces.json').write_text(json.dumps(
        {'m': {'source': source, 'installLocation': str(clone)}}), encoding='utf-8')
    (plugins / 'installed_plugins.json').write_text(json.dumps({'version': 2, 'plugins': {
        'a@m': [{'gitCommitSha': installed}],
        'b@m': [{'gitCommitSha': installed}],
        'vendored@m': [{'gitCommitSha': '1111'}],
        'other@elsewhere': [{'gitCommitSha': '3333'}],
    }}), encoding='utf-8')
    return str(plugins)


class Claude:
    """Records each `claude` argument list and succeeds."""

    def __init__(self):
        self.calls = []

    def __call__(self, *args):
        self.calls.append(' '.join(args))
        return True


def test_a_local_install_follows_the_clone_head(tmp_path):
    local = repo(tmp_path / 'clone', 'local')
    plugins = setup(tmp_path, {'source': 'directory', 'path': str(tmp_path / 'clone')}, local)
    claude = Claude()
    assert hook.update('m', plugins, claude) is None
    assert claude.calls == []


def test_a_local_install_behind_the_clone_updates_the_repository_own_plugins(tmp_path):
    local = repo(tmp_path / 'clone', 'local')
    plugins = setup(tmp_path, {'source': 'directory', 'path': str(tmp_path / 'clone')}, '0' * 40)
    claude = Claude()
    message = hook.update('m', plugins, claude)
    assert claude.calls == ['plugin update a@m', 'plugin update b@m']
    assert local[:7] in message and 'a b' in message


def test_a_remote_install_follows_the_remote_head_not_the_clone(tmp_path):
    repo(tmp_path / 'clone', 'stale clone')
    remote = repo(tmp_path / 'remote', 'remote')
    plugins = setup(tmp_path, {'source': 'git', 'url': str(tmp_path / 'remote')}, remote)
    claude = Claude()
    assert hook.update('m', plugins, claude) is None
    assert claude.calls == []


def test_a_remote_install_behind_refreshes_the_catalogue_then_updates(tmp_path):
    local = repo(tmp_path / 'clone', 'clone')
    remote = repo(tmp_path / 'remote', 'remote')
    plugins = setup(tmp_path, {'source': 'git', 'url': str(tmp_path / 'remote')}, local)
    claude = Claude()
    message = hook.update('m', plugins, claude)
    assert claude.calls == ['plugin marketplace update m', 'plugin update a@m', 'plugin update b@m']
    assert remote[:7] in message


def test_a_github_source_is_read_from_its_https_url():
    assert hook.remote_url({'source': 'github', 'repo': 'o/skills'}) == 'https://github.com/o/skills.git'


def test_an_unreachable_remote_passes_in_silence(tmp_path):
    repo(tmp_path / 'clone', 'clone')
    plugins = setup(tmp_path, {'source': 'git', 'url': str(tmp_path / 'missing')}, '0' * 40)
    claude = Claude()
    assert hook.update('m', plugins, claude) is None
    assert claude.calls == []


def test_a_marketplace_not_added_passes_in_silence(tmp_path):
    repo(tmp_path / 'clone', 'clone')
    plugins = setup(tmp_path, {'source': 'directory', 'path': str(tmp_path / 'clone')}, '0' * 40)
    claude = Claude()
    assert hook.update('unknown', plugins, claude) is None
    assert claude.calls == []


def test_a_failed_update_is_left_out_of_the_message(tmp_path):
    repo(tmp_path / 'clone', 'clone')
    plugins = setup(tmp_path, {'source': 'directory', 'path': str(tmp_path / 'clone')}, '0' * 40)
    message = hook.update('m', plugins, lambda *args: args[-1] != 'a@m')
    assert ' b ' in message and ' a ' not in message
