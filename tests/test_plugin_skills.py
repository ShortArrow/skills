"""Each plugin in the marketplace offers exactly the skills it is meant to, and attack-guard none.

    python -m pytest tests/test_plugin_skills.py

How Claude Code finds a plugin's skills (code.claude.com/docs/en/plugins-reference): a
`skills` list adds to the default scan of the plugin's own `skills/` folder, except that
an entry whose source is the marketplace root and lists specific skills loads only those.
An empty list is not that exception, so a root-sourced plugin with `"skills": []` loads
every skill in the repository; a plugin that offers none needs a folder of its own.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MARKETPLACE = os.path.join(ROOT, '.claude-plugin', 'marketplace.json')


def plugins():
    with open(MARKETPLACE, encoding='utf-8') as f:
        return [p for p in json.load(f)['plugins'] if isinstance(p['source'], str)]


def skill_folders(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name, 'SKILL.md')))


def offered(plugin):
    """The skill names Claude Code loads for a plugin whose source is a folder in this repository."""
    root = os.path.normpath(os.path.join(ROOT, plugin['source']))
    listed = [os.path.basename(os.path.normpath(s)) for s in plugin.get('skills') or []]
    if root == ROOT and listed:
        return sorted(listed)
    return sorted(set(skill_folders(os.path.join(root, 'skills'))) | set(listed))


def test_attack_guard_offers_no_skill():
    guard = next(p for p in plugins() if p['name'] == 'attack-guard')
    assert offered(guard) == []


def test_no_skill_is_offered_by_two_plugins():
    seen = {}
    for plugin in plugins():
        for name in offered(plugin):
            assert name not in seen, (name, seen.get(name), plugin['name'])
            seen[name] = plugin['name']


def test_a_plugin_at_the_marketplace_root_lists_its_skills():
    """An empty or missing list there means the whole skills/ folder, which is never meant."""
    for plugin in plugins():
        if os.path.normpath(os.path.join(ROOT, plugin['source'])) == ROOT:
            assert plugin.get('skills'), plugin['name']


def test_a_plugin_in_a_folder_of_its_own_keeps_its_hook_scripts_inside_it():
    """A plugin installed from git is copied folder by folder, so a script above its root is not there."""
    for plugin in plugins():
        root = os.path.normpath(os.path.join(ROOT, plugin['source']))
        for groups in (plugin.get('hooks') or {}).values():
            for group in groups:
                for hook in group['hooks']:
                    for word in hook.get('command', '').split():
                        word = word.strip('"')
                        if word.startswith('${CLAUDE_PLUGIN_ROOT}/'):
                            path = os.path.join(root, word[len('${CLAUDE_PLUGIN_ROOT}/'):])
                            assert os.path.isfile(path), (plugin['name'], word)
