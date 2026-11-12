"""SessionStart hook: bring a marketplace's own plugins up to the HEAD it installs from.

    python update-own-plugins.py <marketplace>

The HEAD compared against follows how the marketplace was added. A directory
marketplace installs from the clone, so the clone's HEAD; a GitHub or git
marketplace installs from the remote, so the remote's HEAD, read with
`git ls-remote`, which leaves any clone alone. Only plugins whose source is the
marketplace repository itself are compared; a vendored plugin pins its own commit.
When one is behind, a remote catalogue is refreshed first, then each such plugin
is updated, and one systemMessage names them. Claude Code loads plugins at
startup, so the update takes effect in the next session.

Prints the SessionStart output or nothing. A marketplace not added, an unreadable
HEAD (offline) or a git error passes in silence: the hook keeps the install
current, it does not gate the session.
"""
import json
import os
import shutil
import subprocess
import sys

TIMEOUT = 15
UPDATE_TIMEOUT = 120


def read_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def remote_url(source):
    """The URL a remote marketplace source installs from, or None for a local one."""
    if source.get('source') == 'github':
        return f"https://github.com/{source['repo']}.git"
    if source.get('source') == 'git':
        return source.get('url')
    return None


def git(*args):
    try:
        run = subprocess.run(['git', *args], capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return run.stdout.strip() if run.returncode == 0 else None


def head(entry):
    """The commit the marketplace installs from: the remote's HEAD, or the clone's."""
    url = remote_url(entry['source'])
    if url:
        out = git('ls-remote', url, 'HEAD')
        return out.split()[0] if out else None
    if entry['source'].get('source') == 'directory':
        return git('-C', entry['installLocation'], 'rev-parse', 'HEAD')
    return None


def own_plugins(location):
    """Names of the catalogue's plugins whose source is the marketplace repository itself."""
    catalogue = read_json(os.path.join(location, '.claude-plugin', 'marketplace.json')) or {}
    return {p['name'] for p in catalogue.get('plugins', []) if isinstance(p.get('source'), str)}


def behind(marketplace, installed, own, sha):
    """Installed ids of the marketplace's own plugins at a commit other than sha."""
    return [plugin_id for plugin_id, installs in installed.items()
            if plugin_id.rpartition('@')[2] == marketplace
            and plugin_id.rpartition('@')[0] in own
            and installs and installs[0].get('gitCommitSha') != sha]


def update(marketplace, plugins_dir, claude):
    """Update what is behind with claude(*args) -> bool, and the message to show, or None."""
    entry = (read_json(os.path.join(plugins_dir, 'known_marketplaces.json')) or {}).get(marketplace)
    if not entry:
        return None
    sha = head(entry)
    if not sha:
        return None
    installed = (read_json(os.path.join(plugins_dir, 'installed_plugins.json')) or {}).get('plugins', {})
    stale = behind(marketplace, installed, own_plugins(entry['installLocation']), sha)
    if not stale:
        return None
    if remote_url(entry['source']):
        claude('plugin', 'marketplace', 'update', marketplace)
    updated = [plugin_id.rpartition('@')[0] for plugin_id in stale if claude('plugin', 'update', plugin_id)]
    if not updated:
        return None
    return f"{marketplace}: {' '.join(updated)} updated to {sha[:7]}; the next session loads them"


def run_claude(*args):
    try:
        return subprocess.run([shutil.which('claude') or 'claude', *args], stdin=subprocess.DEVNULL, capture_output=True,
                              timeout=UPDATE_TIMEOUT).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def main(argv):
    if len(argv) != 2:
        return 0
    plugins_dir = os.path.join(os.path.expanduser('~'), '.claude', 'plugins')
    message = update(argv[1], plugins_dir, run_claude)
    if message:
        print(json.dumps({'systemMessage': message}))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
