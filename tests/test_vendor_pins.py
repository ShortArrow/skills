"""A vendored plugin installs the commit its submodule records.

Claude Code clones a marketplace without its submodules, so a plugin kept as a
submodule is installed from its own URL; the marketplace entry pins that URL to
a sha, and this test holds the sha to the commit the submodule records.

    python -m pytest tests/test_vendor_pins.py
"""
import configparser
import json
import os
import subprocess

ROOT = os.path.join(os.path.dirname(__file__), '..')
MARKETPLACE = os.path.join(ROOT, '.claude-plugin', 'marketplace.json')


def normalized(url):
    return url.rstrip('/').removesuffix('.git').lower()


def submodules():
    """Submodule path by normalized URL, from .gitmodules."""
    parser = configparser.ConfigParser()
    parser.read(os.path.join(ROOT, '.gitmodules'), encoding='utf-8')
    return {normalized(parser[s]['url']): parser[s]['path'] for s in parser.sections() if s.startswith('submodule')}


def recorded_commit(path):
    """The commit the index records for a submodule path (mode 160000)."""
    line = subprocess.run(['git', 'ls-files', '-s', '--', path], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.split()
    assert line and line[0] == '160000', (path, line)
    return line[1]


def test_every_vendored_plugin_installs_the_commit_its_submodule_records():
    with open(MARKETPLACE, encoding='utf-8') as f:
        plugins = json.load(f)['plugins']
    paths = submodules()
    vendored = [(p['name'], p['source'], paths[normalized(p['source']['url'])]) for p in plugins
                if isinstance(p.get('source'), dict) and normalized(p['source'].get('url', '')) in paths]
    assert vendored, 'no marketplace plugin is fetched from a submodule URL'
    for name, source, path in vendored:
        assert source.get('sha') == recorded_commit(path), (name, source.get('sha'), path)
