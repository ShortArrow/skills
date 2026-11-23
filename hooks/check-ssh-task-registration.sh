#!/usr/bin/env bash
# PreToolUse hook for hyperv-clean-vm's rule: a scheduled task on an ssh host
# is registered by a script sent with scp, never by schtasks or
# Register-ScheduledTask typed on the ssh command line. ssh then runs one
# line, the one that starts that script.
#
# Reads the hook input JSON on stdin. Prints a deny verdict and exits 0 when
# the command line runs ssh and, from there on, registers, changes or deletes
# a task: schtasks /create, /change or /delete, or Register-, Set- or
# Unregister-ScheduledTask. Prints nothing otherwise; silence is the allow
# verdict. Reading and starting a task (schtasks /query, /run, /end, Get- and
# Start-ScheduledTask) stay open over ssh.
#
# ssh counts only in command position (line start, after ; & | ( or a
# newline, optionally quoted or with a path), so prose, commit messages and
# searches that mention it pass, and so do ssh-keygen and sshd. The task
# command counts only as a whole word, so a script named
# register-schtasks.ps1 or Register-ScheduledTask.ps1 passes.
set -u

input="$(cat)"
shopt -s nocasematch
[[ $input == *ssh* ]] || exit 0
shopt -u nocasematch
python=$(bash "$(dirname "$0")/run-python.sh" --which)
[ -n "$python" ] || exit 0

command_line="$(printf '%s' "$input" | "$python" -c 'import json,sys
try:
    data = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    sys.stdout.write(data.get("tool_input", {}).get("command", "").replace("\r", ""))
except Exception:
    pass' 2>/dev/null | tr '\n' ';')"

ssh_onward=$(printf '%s' "$command_line" |
  grep -Eio '(^|[;&|(]) *"?([^ ;&|"]*[\\/])?ssh(\.exe)?"? .*' | head -n 1)
[ -n "$ssh_onward" ] || exit 0

word_start='(^|[^a-z0-9_-])'
schtasks_write="${word_start}schtasks(\\.exe)?[^;&|]* [\"']?/(create|change|delete)([^a-z]|\$)"
cmdlet_write="${word_start}(register|set|unregister)-scheduledtask([^a-z0-9_.-]|\$)"
if printf '%s' "$ssh_onward" | grep -Eiq "$schtasks_write|$cmdlet_write"; then
  cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Do not register, change or delete a scheduled task on the ssh command line (schtasks /create, /change, /delete, Register-, Set- or Unregister-ScheduledTask). Quoting collapses through ssh and the remote shell, and the error comes from a shell you are not looking at. Write the registration into a .ps1, send it with scp, and run only that script over ssh: scp register-task.ps1 <host>:C:/tmp/ && ssh <host> pwsh -NoProfile -File C:/tmp/register-task.ps1. Querying, running and ending a task over ssh stay allowed. The rule is hyperv-clean-vm's."}}
EOF
fi

exit 0
