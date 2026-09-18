---
name: windows-interactive-session
description: |
  Run GUI work — a UI Automation test, an app whose window must exist, a screenshot of a real desktop — on a Windows machine reached only over SSH, PowerShell Direct or WinRM. Triggered by the moments that leave it in session 0: about to start a UI test or an application from an SSH command and expect a window, about to read AutoAdminLogon=1 as proof that autologon works, about to pass a filter or a path as a scheduled task's argument string, about to launch a helper process over SSH and expect it to outlive the command, about to measure the screen in a session other than the one the test runs in, or about to poll for a result file the previous run already left behind. UI Automation reaches only the session it runs in, and a run in session 0 fails without ever naming the session. Use when driving a headless or remote Windows desktop, and when a UI test that passes locally finds nothing on the guest.
allowed-tools: PowerShell, Read, Write, Bash
---

# Session 1 or nothing

**UI Automation reaches only the session it runs in.** Every channel into a remote Windows machine arrives in session 0,
which has a desktop nobody is looking at and a fixed 1024x768 on it,
so a test started from there enumerates an empty tree,
and an application started from there has a window nobody can see or click.

Nothing in the failure names the session.
The test reports that it could not find the main window;
the application reports nothing at all and sits in `Get-Process` with a session id you did not look at.

| Channel | Lands in | Sees the desktop |
|---|---|---|
| SSH (`sshd`) | session 0 | no |
| PowerShell Direct (`Invoke-Command -VMName`) | session 0 | no |
| WinRM, `Enter-PSSession` | session 0 | no |
| A scheduled task whose principal is `-LogonType Interactive` | the logged-on session | yes |

The last row is the whole crossing.
Everything below is what it costs.

`scripts/` is a reference implementation to copy into the repository that needs it,
not a runtime dependency — a project's runner has to work for a person and for a CI runner,
and neither has this skill installed.
The host-side scripts dot-source `GuestSsh.ps1` from `windows-ssh-commands` and take `-GuestSshPath` when that skill is not installed beside this one.

| Purpose | File |
|---|---|
| Stage, start in the logged-on session, wait, collect | `scripts/Invoke-GuestInteractiveRun.ps1` |
| The guest-side skeleton: log, exit code, marker | `scripts/guest-run-template.ps1` |
| What is missing, before a run is attempted | `scripts/Test-GuestReadiness.ps1` |

```powershell
./scripts/Test-GuestReadiness.ps1 -Address 172.28.10.5 -User User -Name myproject
./scripts/Invoke-GuestInteractiveRun.ps1 -Address 172.28.10.5 -User User -Name myproject `
    -GuestScript ./scripts/guest-run-template.ps1 `
    -Stage ([ordered]@{ app = './build/app'; test = './build/tests' }) `
    -Value @{ 'filter.txt' = 'Category=UI' } `
    -OutputDirectory ./artifacts/ui-tests
```

## Somebody has to be logged on

An interactive task runs in the session of the account it names,
and if that account is not signed in there is no session for it to run in.
The task registers, `Start-ScheduledTask` succeeds,
and nothing happens.

Automatic logon is what stands in for the person.
Write the credential with a tool that puts the password into the LSA secret rather than a plaintext registry value — Sysinternals Autologon does this:

```powershell
& $autologonExe /accepteula $user $env:COMPUTERNAME $password
```

**`AutoAdminLogon = 1` is not evidence that autologon works.** It is evidence that a registry value was written.
The password may be missing from the LSA,
the account name may not match, a policy may override it.
Reboot and measure the outcome instead:

```powershell
$p = Get-Process explorer -ErrorAction SilentlyContinue | Where-Object SessionId -gt 0
if (-not $p) { throw 'nobody is logged on' }
```

`(Get-CimInstance Win32_ComputerSystem).UserName` answers the same question in one line,
and is empty when no one is signed in.
Make the provisioning script fail there.
A machine that boots to the logon screen is a machine whose entire UI suite fails on the next run,
with a message about a missing window.

## Crossing over: the task

```powershell
$me = (Get-CimInstance Win32_ComputerSystem).UserName
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File ""$root\run.ps1"" -Root ""$root"""
$principal = New-ScheduledTaskPrincipal -UserId $me -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
```

`-LogonType Interactive` is what puts the work on the desktop;
`-RunLevel Highest` matters as soon as it touches anything that needs elevation.
Name the principal from the machine's own logged-on user rather than from a constant,
so the script survives being pointed at a differently named account.

## The task cannot answer you

`Start-ScheduledTask` returns as soon as the task has started.
There is no exit code, no output stream and no exception — the caller and the work are in different sessions,
and nothing connects them.

So the script inside writes the answer down and the caller polls for it:

```
artifacts/run.log        progress, appended as it goes
artifacts/exitcode.txt   the run's exit code
artifacts/done.marker    written last, and only last
```

Two rules make this work:

- **The marker is written after everything else**,
  including after the helper processes have been stopped.
  A marker written early turns the caller's wait into a race it usually loses.
- **Stale files are deleted before the task starts**,
  not after it finishes.
  A `done.marker` left by the previous run ends the wait immediately,
  and the caller then collects the previous run's results and reports them as this run's.
  A log opened for appending mixes two runs into one file.

Clear the caller-side output directory at the top of the run as well,
before anything that can fail.
A run that dies halfway otherwise leaves the last successful run's artifacts sitting where the reader expects fresh ones.

## Values go in files, not in the argument string

A scheduled task's action is a single string.
Anything carrying `|`, `=`,
a quote or a non-ASCII character survives at the mercy of two layers of parsing you do not control.

Write the value into a file beside the work and let the script read it:

```powershell
Set-Content "$root\artifacts\filter.txt" -Value $Filter -Encoding ascii -NoNewline
```

That is what a test-case filter such as `Category=UI|Category=Smoke` needs,
and it costs one line.

## Helpers started over SSH die with the SSH command

Win32-OpenSSH puts the command's process tree into a job object and terminates it when the session ends.
A mock server or any other background process started from an `ssh` call is killed the moment `ssh` returns — measured,
not theoretical, and it looks exactly like the process crashing during startup.

Start such helpers from the same scheduled task as the work itself.
Their lifetime is then bounded by the run,
which is what you wanted anyway,
and the task is also the only place where an environment variable set by the caller reaches the child.

If a helper has to outlive a single command and cannot live inside the task,
give it a task of its own and `schtasks /run` it.

## Measure the screen where the work runs

A probe over SSH reports session 0's fixed 1024x768.
The interactive desktop is whatever the machine's display is set to,
and the difference decides whether a window's lower controls fall inside the visible area.
A control outside it disappears from UI Automation and a coordinate click lands on nothing,
silently.

So the probe runs as its own short interactive task,
writes what it found to a file, and the caller reads that file:

```powershell
Add-Type -AssemblyName System.Windows.Forms
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
"Screen=$($b.Width)x$($b.Height)"
```

Record the real size in the run's log too.
When a click goes missing three weeks later,
that line is what tells you the window was taller than the screen.

## A readiness check that returns nothing is not a pass

Those checks run inside the machine,
so an unreachable machine produces zero problems — which reads as "ready" to any caller that counts problems.

Return facts alongside problems and treat an empty fact set as the failure it is:

```powershell
if ($facts.Count -eq 0) { $problems += 'no response from the guest' }
```

## Facts that bite

| | |
|---|---|
| **The task runs as the logged-on user, not as you** | Its environment, its `%TEMP%` and its mapped drives are that account's. Resolve paths inside the machine instead of composing them outside |
| **`Start-ScheduledTask` succeeds when the task cannot run** | No session, a disabled task, a missing file — all return the same nothing. The marker file is the only evidence that the work ran |
| **An interactive task inherits nothing from the caller** | Environment variables exported over SSH are gone by then. Whatever the work needs is set inside the script the task runs |
| **A locked screen ends the party** | UI Automation against a locked desktop finds nothing. Turn off the lock screen and the screen saver on a machine whose job is running UI tests |
| **Session ids are not stable** | Session 1 is the usual console session but not a guarantee. Assert `SessionId -gt 0`, never `-eq 1` |
| **Probe tasks have to be unregistered** | Left behind, they fill the task library and slow down every later reading of "is it ready" |
