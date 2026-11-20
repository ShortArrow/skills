"""hooks/check-ssh-task-registration.sh refuses a scheduled task registered,
changed or deleted on an ssh command line, and lets everything else through.

    python -m pytest tests/test_check_ssh_task_registration.py
"""
import json
import os
import shutil
import subprocess

import pytest

ROOT = os.path.join(os.path.dirname(__file__), '..')
SCRIPT = os.path.join(ROOT, 'hooks', 'check-ssh-task-registration.sh')
MARKETPLACE = os.path.join(ROOT, '.claude-plugin', 'marketplace.json')
GIT_BASH = os.path.join(os.environ.get('ProgramFiles', 'C:/Program Files'), 'Git', 'bin', 'bash.exe')

DENY = [
    "ssh host.example.invalid 'schtasks /create /tn Rollback /tr C:\\tmp\\rollback.cmd /sc once /st 12:00 /ru SYSTEM'",
    'ssh host.example.invalid schtasks /create /tn X /tr notepad /sc onlogon',
    'ssh -o HostName=192.0.2.10 -o HostKeyAlias=192.0.2.11 host.example.invalid "schtasks.exe /delete /tn X /f"',
    "ssh host.example.invalid 'C:\\Windows\\System32\\schtasks.exe /change /tn X /disable'",
    'ssh host.example.invalid SCHTASKS /Create /TN X /TR notepad /SC ONLOGON',
    'ssh host.example.invalid pwsh -c "Set-ScheduledTask -TaskName X -Trigger $t"',
    'ssh host.example.invalid pwsh -c "Unregister-ScheduledTask -TaskName X -Confirm:$false"',
    'ssh host.example.invalid pwsh -NoProfile -Command "Register-ScheduledTask -TaskName X -Action $a -Trigger $t"',
    "ssh.exe host.example.invalid 'powershell -c \"register-scheduledtask -TaskName X -Xml (Get-Content x.xml -Raw)\"'",
    '& ssh host.example.invalid "Register-ScheduledTask -TaskName X -InputObject $task"',
    'scp a.txt host.example.invalid:C:/tmp/ && ssh host.example.invalid schtasks /create /tn X /tr notepad /sc onstart',
    "ssh host.example.invalid pwsh -NoProfile -Command - <<'EOF'\n"
    "$a = New-ScheduledTaskAction -Execute pwsh\n"
    "Register-ScheduledTask -TaskName X -Action $a\n"
    "EOF",
    '"C:\\Windows\\System32\\OpenSSH\\ssh.exe" host.example.invalid schtasks /create /tn X /tr notepad /sc onstart',
]

ALLOW = [
    # The sanctioned way, and the task commands that register nothing: query, run, end.
    'scp register-task.ps1 host.example.invalid:C:/tmp/ && ssh host.example.invalid pwsh -NoProfile -File C:/tmp/register-task.ps1',
    'ssh host.example.invalid pwsh -NoProfile -File C:/tmp/register-schtasks.ps1',
    'ssh host.example.invalid pwsh -NoProfile -File C:/tmp/Register-ScheduledTask.ps1',
    'ssh host.example.invalid Get-ScheduledTask',
    'ssh host.example.invalid schtasks /query /tn X /v /fo list',
    "ssh host.example.invalid 'C:\\Windows\\System32\\schtasks.exe /run /tn X'",
    'ssh host.example.invalid pwsh -c "Start-ScheduledTask -TaskName X"',
    'ssh host.example.invalid schtasks /end /tn X',
    # No ssh in command position: local task commands, searches, prose.
    'schtasks /create /tn X /tr notepad /sc onlogon',
    'Register-ScheduledTask -TaskName X -Action $a',
    "grep -n 'ssh.*schtasks' notes.md",
    'git commit -m "docs: ssh では schtasks を直接打たない"',
    'Get-Service sshd; schtasks /query /tn X',
    'ssh-keygen -t ed25519 -f key; schtasks /query /tn X',
]


def shell():
    """The bash Claude Code runs hooks with: Git Bash on Windows, where `bash` may be WSL's."""
    git_bash = os.environ.get('CLAUDE_CODE_GIT_BASH_PATH') or GIT_BASH
    return git_bash if os.name == 'nt' and os.path.exists(git_bash) else shutil.which('bash')


def verdict(argv, command, env=None):
    payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': command}}, ensure_ascii=False)
    run = subprocess.run(argv, input=payload.encode('utf-8'), capture_output=True, env=env)
    assert run.returncode == 0, run.stderr
    out = run.stdout.decode('utf-8').strip()
    if not out:
        return 'allow'
    assert json.loads(out)['hookSpecificOutput']['permissionDecision'] == 'deny'
    return 'deny'


@pytest.mark.parametrize('command', DENY)
def test_a_task_written_on_the_ssh_line_is_refused(command):
    assert verdict([shell(), SCRIPT], command) == 'deny'


@pytest.mark.parametrize('command', ALLOW)
def test_everything_else_passes(command):
    assert verdict([shell(), SCRIPT], command) == 'allow'


def test_the_reason_names_the_skill_and_the_one_line():
    payload = json.dumps({'tool_input': {'command': DENY[1]}})
    run = subprocess.run([shell(), SCRIPT], input=payload.encode(), capture_output=True)
    reason = json.loads(run.stdout)['hookSpecificOutput']['permissionDecisionReason']
    assert 'hyperv-clean-vm' in reason and 'scp' in reason and '-File' in reason


def wired_commands():
    with open(MARKETPLACE, encoding='utf-8') as f:
        plugins = json.load(f)['plugins']
    return [(group['matcher'], hook['command'])
            for plugin in plugins
            for group in (plugin.get('hooks') or {}).get('PreToolUse', [])
            for hook in group['hooks']
            if 'check-ssh-task-registration' in hook.get('command', '')]


def test_the_marketplace_wires_it_on_both_shells_and_the_command_decides():
    wired = wired_commands()
    assert sorted(matcher for matcher, _ in wired) == ['Bash', 'PowerShell']
    env = {**os.environ, 'CLAUDE_PLUGIN_ROOT': os.path.abspath(ROOT).replace('\\', '/')}
    for _, command in wired:
        assert verdict([shell(), '-c', command], DENY[1], env) == 'deny'
        assert verdict([shell(), '-c', command], ALLOW[0], env) == 'allow'
