"""Every command hook lets the call through when its script is missing,
and every prompt hook sees its input and answers in the schema.

A marketplace update reads the new hook commands before the installed plugin
holds the scripts they name, and exit code 2 from a hook blocks the tool call or
the stop, so a missing script must not exit 2.

    python -m pytest tests/test_hook_commands.py
"""
import json
import os
import shutil
import subprocess

MARKETPLACE = os.path.join(os.path.dirname(__file__), '..', '.claude-plugin', 'marketplace.json')
GIT_BASH = os.path.join(os.environ.get('ProgramFiles', 'C:/Program Files'), 'Git', 'bin', 'bash.exe')


def hook_commands():
    with open(MARKETPLACE, encoding='utf-8') as f:
        plugins = json.load(f)['plugins']
    for plugin in plugins:
        for event, groups in (plugin.get('hooks') or {}).items():
            for group in groups:
                for hook in group['hooks']:
                    yield plugin['name'], event, hook


def shell():
    """The bash Claude Code runs hooks with: Git Bash on Windows, where `bash` may be WSL's."""
    git_bash = os.environ.get('CLAUDE_CODE_GIT_BASH_PATH') or GIT_BASH
    return git_bash if os.name == 'nt' and os.path.exists(git_bash) else shutil.which('bash')


def test_a_hook_whose_script_is_missing_does_not_block(tmp_path):
    env = {**os.environ, 'CLAUDE_PLUGIN_ROOT': str(tmp_path).replace('\\', '/')}
    for plugin, event, hook in hook_commands():
        if hook['type'] != 'command':
            continue
        run =subprocess.run([shell(), '-c', hook['command']], input='{}', env=env,
                             capture_output=True, text=True)
        assert run.returncode != 2, (plugin, event, hook['command'], run.stderr)


def test_a_prompt_hook_sees_the_input_and_answers_in_the_schema():
    prompts = [(p, e, h) for p, e, h in hook_commands() if h['type'] == 'prompt']
    assert prompts
    for plugin, event, hook in prompts:
        assert '$ARGUMENTS' in hook['prompt'], (plugin, event)
        assert '{"ok": true}' in hook['prompt'] and '{"ok": false, "reason":' in hook['prompt'], (plugin, event)
        assert '$' not in hook['prompt'].replace('$ARGUMENTS', ''), (plugin, event)
