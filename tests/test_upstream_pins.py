"""A plugin taken unchanged from someone else's repository is pinned to a commit that repository still carries.

A fork of a plugin is held by tests/test_vendor_pins.py: its submodule records the
commit and the marketplace entry repeats it, so the two cannot drift. A plugin
nobody forked has no submodule to check it against, and its `sha` is then a
string no test reads. This asks the remote instead: the pinned commit exists, and
the declared `ref` reaches it, so an install gets the tree that was reviewed.

An unreachable remote skips rather than fails, the way hooks/upstream-behind.py
does: the pin is reviewed when it is set and this holds it afterwards, so no
network is a reason to skip rather than to fail.

    python -m pytest tests/test_upstream_pins.py
"""
import configparser
import json
import os
import subprocess

ROOT = os.path.join(os.path.dirname(__file__), '..')
MARKETPLACE = os.path.join(ROOT, '.claude-plugin', 'marketplace.json')
TIMEOUT = 20


def normalized(url):
    return url.rstrip('/').removesuffix('.git').lower()


def forked_urls():
    """The URLs that test_vendor_pins.py already holds, by submodule."""
    parser = configparser.ConfigParser()
    parser.read(os.path.join(ROOT, '.gitmodules'), encoding='utf-8')
    return {normalized(parser[s]['url']) for s in parser.sections() if s.startswith('submodule')}


def unforked():
    """(name, url, ref, sha) for every URL-sourced plugin with no submodule of its own."""
    with open(MARKETPLACE, encoding='utf-8') as f:
        plugins = json.load(f)['plugins']
    forked = forked_urls()
    return [(p['name'], s['url'], s.get('ref'), s.get('sha'))
            for p in plugins
            if isinstance(s := p.get('source'), dict) and s.get('source') == 'url'
            and normalized(s.get('url', '')) not in forked]


def remote_sha(url, ref):
    """The commit the remote's ref points at, or None when the remote cannot be reached."""
    done = subprocess.run(['git', 'ls-remote', url, ref],
                          capture_output=True, text=True, timeout=TIMEOUT)
    if done.returncode != 0:
        return None
    line = done.stdout.split()
    return line[0] if line else ''


def test_every_unforked_plugin_declares_a_ref_and_a_sha():
    for name, url, ref, sha in unforked():
        assert ref, f'{name}: no ref, so an install follows the default branch wherever it moves'
        assert sha and len(sha) == 40, f'{name}: {sha!r} is not a full commit sha'


def test_every_unforked_pin_is_a_commit_its_remote_still_carries():
    for name, url, ref, sha in unforked():
        head = remote_sha(url, ref)
        if head is None:
            continue
        assert head, f'{name}: {url} carries no ref {ref}'
        if head == sha:
            continue
        fetched = subprocess.run(['git', 'fetch', '--quiet', '--depth', '50', url, ref],
                                 cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT * 3)
        if fetched.returncode != 0:
            continue
        reachable = subprocess.run(['git', 'merge-base', '--is-ancestor', sha, head],
                                   cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT)
        assert reachable.returncode == 0, (
            f'{name}: pinned {sha[:7]} is not an ancestor of {ref} ({head[:7]}) at {url}; '
            'the commit was rewritten or dropped, so an install gets a tree nobody reviewed')
