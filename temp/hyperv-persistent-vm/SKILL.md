---
name: hyperv-persistent-vm
description: |
  A Hyper-V guest kept up as a long-lived fixture rather than rewound to a clean checkpoint before every run. Triggered by the moments that make it unreliable: about to build the guest in one unbroken script with a single checkpoint at the end, about to give a test VM fixed memory on a developer's own machine, about to write the guest's address into a config file or ssh_config, about to open VMConnect and drive whatever desktop it shows, about to hand-place a file the runner re-seeds on every run, or about to start a run while the previous one still holds its ports and its output files. A guest that keeps its state also keeps the last run's. Use when standing up or maintaining a VM that stays up between runs; hyperv-clean-vm owns the rewind-to-pristine fixture and windows-sandbox the disposable one.
allowed-tools: PowerShell, Read, Write, Bash
---

# The VM that stays up

A clean-room fixture and a workshop are different machines with the same hypervisor underneath.

| | Rewind to a checkpoint (`hyperv-clean-vm`) | Keep it running (this skill) |
|---|---|---|
| Start of a run | identical every time | whatever the last run left |
| Cost per run | a restore and a boot | nothing |
| Long-lived state (a runtime, a tool, autologon) | re-applied or baked into the checkpoint | installed once |
| What it is for | reproducing a bug on a pristine machine | a suite that runs many times a day |

Neither replaces the other, and one VM can be both: build it in stages,
checkpoint each stage,
then leave it running and restore only when a run has to start from a known state.
The seam between the two is a restore the runner performs only when asked for one.

`scripts/` is a reference implementation to copy into the repository that needs it,
not a runtime dependency.
`New-HyperVFixtureVM.ps1` dot-sources `GuestSsh.ps1` from `windows-ssh-commands`,
and takes `-GuestSshPath` when that skill is not installed beside this one.

| Purpose | File |
|---|---|
| Provision in verified stages, one checkpoint each | `scripts/New-HyperVFixtureVM.ps1` |
| The guest's address, from the hypervisor | `scripts/Get-HyperVGuestAddress.ps1` |
| Watch the console the automation is driving | `scripts/Show-HyperVConsole.ps1` |

## Build it in stages, checkpoint each one

A provisioning script that runs start to finish and checkpoints at the end has to be re-run start to finish whenever one part of it changes.
Cut it at the points where the machine gains a capability:

| Stage | What it adds | Checkpoint |
|---|---|---|
| `Sshd` | a password, OpenSSH server, the trusted key | `clean-sshd` |
| `Autologon` | automatic logon, so an interactive session exists after a reboot | `clean-autologon` |
| `Packages` | the language runtimes and tools the work needs | `clean-packages` |

`-Stage` picks the entry point,
and each stage ends by checkpointing what it just proved.
Name a checkpoint for what it contains rather than for the date — the name is what a later restore has to choose from.

**Verify from outside before checkpointing.** A stage that installed something is not a stage that works.
Checkpoint after the key has actually opened a session,
after the reboot has actually produced a logged-on desktop,
after the installed tool has actually printed its version from inside the guest.
A checkpoint holding an sshd you never connected to is a checkpoint you will restore,
fail against, and rebuild.

Order matters most in the first stage,
where a checkpoint taken before the account had a password silently breaks PowerShell Direct forever after:
`hyperv-clean-vm` has the detail.

## Dynamic memory, or the VM stops starting

Fixed memory is claimed in full at power-on.
A developer's machine is already running an IDE,
a browser and a container or two,
so the full size is not reliably there when the VM wants it,
and the VM simply does not start.

```powershell
Set-VM -Name $VMName -DynamicMemory `
  -MemoryStartupBytes 4GB -MemoryMinimumBytes 2GB -MemoryMaximumBytes 8GB
```

It shrinks while the guest idles and grows when a window opens,
which is the shape of a UI run.

**Memory configuration can only be changed while the VM is off.** Powering off a running VM to apply it destroys whatever reason it was running for — somebody watching it,
another run in progress.
Apply the setting when the state is `Off` and warn otherwise:

```powershell
if ($vm.State -eq 'Off') { Set-VM ... }
elseif (-not $vm.DynamicMemoryEnabled) { Write-Warning "still fixed at $([int]($vm.MemoryStartup/1GB)) GB" }
```

## Ask the hypervisor where the guest is

The Default Switch hands out a new lease across reboots,
so an address written into a config file or an `ssh_config` entry is right until the first restart.
Integration services already know:

```powershell
$address = (Get-VMNetworkAdapter -VMName $VMName).IPAddresses |
    Where-Object { $_ -match '^\d+\.\d+\.\d+\.\d+$' } | Select-Object -First 1
if (-not $address) { throw "no IPv4 address for $VMName — are the integration services running?" }
```

This depends on neither DNS nor the host's SSH configuration,
which is what you want from a fixture.
That address is reachable from the host and from nowhere else — the right amount of exposure.

Every host-side call here — `Get-VM`, `Get-VMNetworkAdapter`,
`Restore-VMCheckpoint` — is checked against Hyper-V's own authorization,
so the account needs to be in **Hyper-V Administrators** and to have signed out and in since being added.

## Watching the screen: the console, not a second desktop

`vmconnect.exe` launched directly connects with an enhanced session,
which is RDP to a *different* session:
it asks for credentials even though the console is already logged on,
and the desktop it shows is not the one UI Automation is driving.
When a test says a window is missing and enhanced session shows it right there,
this is why.

VMConnect has no per-invocation switch for a basic session,
and the per-VM preference is only written when a person toggles it in the UI.
Drop the host default, launch,
and put the default back once the connection stands:

```powershell
$restoreTo = (Get-VMHost).EnableEnhancedSessionMode
try {
    if ($restoreTo) { Set-VMHost -EnableEnhancedSessionMode $false }
    Start-Process "$env:WINDIR\System32\vmconnect.exe" -ArgumentList 'localhost', $VMName
    Start-Sleep -Seconds 8
}
finally {
    if ($restoreTo) { Set-VMHost -EnableEnhancedSessionMode $true }
}
```

An established connection keeps the basic session after the default returns.
Close the window and reopen it, or reboot the guest,
and it follows whatever the default is then — this is a measure for the time you spend watching,
not a configuration.

To capture the screen instead of watching it,
including while nobody is logged on,
`hyperv-screenshot` does it from the host with no agent in the guest.

## What persistence costs

Everything the last run left behind is present at the start of the next one.
The disposable fixtures never have to think about this;
a persistent guest does.

- **Processes holding ports.** A helper process that did not die keeps its listener,
  and the next run's copy silently fails to bind.
  Kill them by name at the start of the run *and* at the end of the guest-side script.
- **Output files that the caller waits for.** A stale completion marker ends the wait instantly;
  an appended log mixes two runs.
  Delete them before starting — `windows-interactive-session` has the handoff.
- **Records the test reads back.** Where a test asserts on "the last thing written",
  a record file from the previous run answers,
  and an assertion that should have failed passes.
- **Configuration the run seeds.** Seed it fresh every run — and **say so in the documentation**,
  because a configuration someone hand-placed in the guest to try something out disappears the next time the suite runs,
  with nothing to explain where it went.

What you deliberately keep is the expensive part: an installed runtime,
a staged tool.
Stamp what was copied with its size and modification time,
and skip the transfer when the stamp matches:

```powershell
$stamp = '{0}|{1}' -f $file.Length, $file.LastWriteTimeUtc.Ticks
```

## Facts that bite

| | |
|---|---|
| **Checkpoints chain** | A new one is a child of the current state. Restoring an ancestor keeps the descendants, which now branch. A restore that defaults to "the newest checkpoint" stops meaning what you want once that happens |
| **`Start-VM` returns before the guest is up** | And `Restore-VMCheckpoint` does too. Poll SSH until it answers rather than sleeping a guessed interval |
| **Evidence inside the guest dies at the next revert** | Collect artifacts out of the guest before restoring anything |
| **A guest-visible clock jumps on restore** | Anything keyed on timestamps — log rotation, "newest file" lookups — sees time move backwards after a revert |
| **`Set-VM` refuses silently often enough to check** | Read the VM back after configuring it; a warning in a log nobody reads is not a guarantee |
