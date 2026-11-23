"""Hooks start Python with whichever of python3 and python works, and attack-guard
refuses the call when neither does.

    python -m pytest tests/test_run_python.py

Each case runs the marketplace's own hook command under a PATH holding only the
interpreters the case names, so a Linux machine with python3 alone, an older one
with python alone, Windows where python3 is the Store stub that only prints a
message, and a machine with neither are all reproduced here. The fake interpreters
are shell scripts that hand over to the Python running the tests.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MARKETPLACE = os.path.join(ROOT, '.claude-plugin', 'marketplace.json')
GIT_BASH = os.path.join(os.environ.get('ProgramFiles', 'C:/Program Files'), 'Git', 'bin', 'bash.exe')
REAL = sys.executable.replace('\\', '/')
TOOLS = ('cat', 'grep', 'tr', 'head', 'dirname')
CASES = {
    'python3 only': {'python3': 'real'},
    'python only': {'python': 'real'},
    'the Store stub as python3, then python': {'WindowsApps/python3': 'stub', 'python': 'real'},
    'a Store install as python3 alone': {'WindowsApps/python3': 'real'},
}


def shell():
    """The bash Claude Code runs hooks with: Git Bash on Windows, where `bash` may be WSL's."""
    git_bash = os.environ.get('CLAUDE_CODE_GIT_BASH_PATH') or GIT_BASH
    return git_bash if os.name == 'nt' and os.path.exists(git_bash) else shutil.which('bash')


def fake_bin(tmp_path, interpreters):
    """A directory holding only the named interpreters, as PATH will see them."""
    path = tmp_path / 'bin'
    path.mkdir()
    for tool in TOOLS:
        located = shutil.which(tool, path=os.environ['PATH']) if os.name != 'nt' else None
        located = located or os.path.join(os.path.dirname(shell()), '..', 'usr', 'bin', tool + '.exe')
        (path / tool).write_text(f'#!/bin/sh\nexec "{located}" "$@"\n'.replace('\\', '/'), encoding='utf-8', newline='\n')
        os.chmod(path / tool, 0o755)
    store = tmp_path / 'WindowsApps'
    store.mkdir()
    log = str(tmp_path / 'starts.log').replace('\\', '/')
    for name, kind in interpreters.items():
        body = (f'#!/bin/sh\necho "$*" >> "{log}"\nexec "{REAL}" "$@"\n' if kind == 'real'
                else '#!/bin/sh\necho "Python was not found; run without arguments to install from the Microsoft Store" >&2\nexit 49\n')
        target = tmp_path / name if name.startswith('WindowsApps/') else path / name
        target.write_text(body, encoding='utf-8', newline='\n')
        os.chmod(target, 0o755)
    return f'{path}{os.pathsep}{store}'


def hook_commands():
    with open(MARKETPLACE, encoding='utf-8') as f:
        plugins = json.load(f)['plugins']
    return [(plugin['name'], event, group.get('matcher'), hook['command'])
            for plugin in plugins
            for event, groups in (plugin.get('hooks') or {}).items()
            for group in groups
            for hook in group['hooks'] if hook['type'] == 'command']


def run(command, payload, path, root=ROOT, **env):
    full = {**os.environ, 'PATH': path, 'CLAUDE_PLUGIN_ROOT': root.replace('\\', '/'), **env}
    return subprocess.run([shell(), '-c', command], input=json.dumps(payload), env=full,
                          capture_output=True, text=True, encoding='utf-8')


def attack_guard_command():
    return next(c for p, e, m, c in hook_commands() if 'attack-guard' in c and m == 'Bash')


@pytest.mark.parametrize('case', CASES)
def test_attack_guard_runs_on_whichever_python_works(tmp_path, case):
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'echo attack-guard-canary'}}
    out = run(attack_guard_command(), payload, fake_bin(tmp_path, CASES[case]), ATTACK_GUARD='ask')
    assert out.returncode == 0, out.stderr
    verdict = json.loads(out.stdout)['hookSpecificOutput']
    assert verdict['permissionDecision'] == 'deny' and 'canary' in verdict['permissionDecisionReason']


def test_a_python_outside_the_store_folder_starts_once_with_no_trial_run(tmp_path):
    """A trial run costs a process on every tool call; only the Store folder, where the stub lives, needs one."""
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'git status'}}
    path = fake_bin(tmp_path, {'python3': 'real', 'python': 'real'})
    run(attack_guard_command(), payload, path, ATTACK_GUARD='ask')
    starts = (tmp_path / 'starts.log').read_text(encoding='utf-8').splitlines()
    assert len(starts) == 1 and starts[0].endswith('attack-guard.py'), starts


def test_attack_guard_without_python_refuses_and_says_why(tmp_path):
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'git status'}}
    out = run(attack_guard_command(), payload, fake_bin(tmp_path, {'WindowsApps/python3': 'stub'}), ATTACK_GUARD='ask')
    assert out.returncode == 0, out.stderr
    verdict = json.loads(out.stdout)['hookSpecificOutput']
    assert verdict['permissionDecision'] == 'deny'
    assert 'python3' in verdict['permissionDecisionReason'] and 'python' in verdict['permissionDecisionReason']


def stand_in_root(tmp_path):
    """A plugin root whose Python hooks only report that they ran, beside the real launcher and shell hooks."""
    root = tmp_path / 'root'
    shutil.copytree(os.path.join(ROOT, 'hooks'), root / 'hooks')
    for name in os.listdir(root / 'hooks'):
        if name.endswith('.py'):
            (root / 'hooks' / name).write_text(f'import sys\nsys.stdin.read()\nprint("ran {name}")\n', encoding='utf-8')
    return str(root)


@pytest.mark.parametrize('case', CASES)
def test_every_python_hook_starts_on_whichever_python_works(tmp_path, case):
    path, root = fake_bin(tmp_path, CASES[case]), stand_in_root(tmp_path)
    for plugin, event, matcher, command in hook_commands():
        script = next((w.strip('"').split('/')[-1] for w in command.split() if w.strip('"').endswith('.py')), None)
        if script:
            out = run(command, {}, path, root)
            assert f'ran {script}' in out.stdout, (plugin, event, command, out.stderr)


@pytest.mark.parametrize('case', CASES)
def test_the_shell_hooks_read_their_input_with_whichever_python_works(tmp_path, case):
    """check-ssh-task-registration.sh parses its input with Python; a refusal shows it did."""
    path = fake_bin(tmp_path, CASES[case])
    command = next(c for p, e, m, c in hook_commands() if 'check-ssh-task-registration' in c and m == 'Bash')
    payload = {'tool_name': 'Bash', 'tool_input': {'command': 'ssh host.example.invalid schtasks /create /tn X /tr y /sc onlogon'}}
    out = run(command, payload, path)
    assert json.loads(out.stdout)['hookSpecificOutput']['permissionDecision'] == 'deny', out.stderr


def test_other_hooks_without_python_give_no_verdict_and_do_not_block(tmp_path):
    path = fake_bin(tmp_path, {})
    for plugin, event, matcher, command in hook_commands():
        if 'attack-guard' in command:
            continue
        out = run(command, {}, path)
        assert out.returncode != 2 and not out.stdout.strip(), (plugin, event, command, out.stdout)
