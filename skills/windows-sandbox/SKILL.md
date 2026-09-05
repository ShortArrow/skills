---
name: windows-sandbox
description: |
  Run e2e or UI tests inside Windows Sandbox, where SendInput cannot steal the developer's keyboard, and share the machine's single sandbox slot with other projects. Two agents each ending their run by terminating "the" sandbox terminate each other's; a finished-looking sandbox with no window still holds the slot; disabling vGPU stops LogonCommand from ever running. Where a Hyper-V clean-VM checkpoint already exists, prefer it (`hyperv-clean-vm`) — VMs run in parallel and restore to identical state, while the sandbox slot is single and disposal-only. Use when no clean VM has been built and a project needs one disposable isolated desktop, when a sandbox will not start, or when adding a second project that wants the slot.
allowed-tools: PowerShell, Read, Write, Edit
---

# Windows Sandbox as a test target

**Nothing here is a runtime dependency.** A project's test runner must
work for a person and for CI, neither of which has this skill installed —
and the installed copy lives under a hashed plugin cache path that no
repository can reference anyway. What projects share is the lock protocol
below. `scripts/` is a reference implementation to copy in, and copies
need not agree on anything but the lock.

| Purpose | File |
|---|---|
| Take the slot, from a runner in any language | *The protocol*, below |
| Reference implementation of the protocol | `scripts/SandboxLock.ps1` |
| Whole run — build, launch, collect, clean up | `scripts/Invoke-SandboxRun.ps1` |

## Why the sandbox, and not something lighter

FlaUI, Playwright against a desktop app, anything driving a GUI — they all
end at `SendInput`, which delivers to the foreground of the **input
desktop**. Run those on the host and they type into whatever the developer
is looking at.

| Alternative | Why it does not work |
|---|---|
| Hidden Win32 desktop (`CreateDesktop`) | The process and its windows really are isolated, but `SendInput` to a non-input desktop fails with `Access is denied`. Fine for screenshots, useless for keys |
| Windows 11 virtual desktops | One input queue for all of them. Nothing is isolated |
| Windows Sandbox | Its own session, its own active input desktop. The guest receives input; the host is untouched |

Data isolation is a separate problem with separate answers (a config
directory environment variable, a temp profile). Do not reach for the
sandbox to get it.

## One slot, shared by everyone

Windows allows **one sandbox instance at a time**, machine-wide. The `wsb`
CLI does not lift it: `wsb list` is plural in wording, and `wsb start`
still needs the previous environment stopped. Every project on the machine
competes for that one slot, which is where the damage comes from:

- A runner that ends with "kill the sandbox processes" kills whichever
  project's sandbox is running, not necessarily its own
- Checking "is one running?" and then launching is a race. Two runners
  both see zero, both launch, and both later believe the survivor is theirs

### The protocol

Four rules. A runner that follows them cooperates with every other runner
on the machine, whatever it is written in.

1. **The lock is `%ProgramData%\WindowsSandbox\runner.lock`**, held by
   keeping the file open: created for **write**, sharing **read only**
   (`FILE_SHARE_READ`; `FileShare.Read` in .NET, `O_EXLOCK`-equivalent
   elsewhere). A second runner's create fails while the first holds it,
   and Windows closes the handle when the owner dies, so a killed runner
   leaves nothing stuck. Write one line into it — who you are, your PID,
   the time — so a waiter can say who it is behind. Do not delete it on
   release: the handle is the lock, the bytes are only a label
2. **Hold it across the whole span** — pre-flight, launch, wait,
   clean-up. Holding it only over the launch is the same race as no lock
   at all, because the damage is done by the clean-up
3. **Under the lock, a running sandbox is somebody else's**, hand-started
   or left open for debugging. Refuse the run. Never terminate it
4. **Clean up only what you started.** Rule 3 makes that "everything
   alive now", since you began with none

A runner outside the protocol will not appear in the lock, only in the
sandbox itself. `peer-sessions` names which session is holding it.

```powershell
# Reference implementation, for a runner the project already has
. "$PSScriptRoot/SandboxLock.ps1"     # copied into the repo, not referenced from the skill
$lock = Enter-SandboxLock -Owner 'BiosMonitorClassic uitests'
try     { <# launch, wait, clean up #> }
finally { Exit-SandboxLock $lock }
```

## The shape of a run

`Invoke-SandboxRun.ps1` implements it end to end.

1. **Build on the host.** The guest is a bare Windows install with no
   network requirement and no toolchain. Map the SDK in read-only and run
   with `--no-build --no-restore`
2. **Generate the `.wsb` per run.** It holds absolute host paths, so it is
   a temp file, not a committed one
3. **Results come back through a mapped folder.** There is no stdout from
   the guest — not from `LogonCommand`, not from `wsb exec` either. The
   guest writes a log, an exit code, and `done.marker`; the host polls for
   the marker
4. **Force-minimize the client window and hand the foreground back.** The
   host is not disturbed by the run, but a sandbox window sitting in front
   swallows keystrokes. `SetForegroundWindow` is best effort under the
   foreground lock; `SW_FORCEMINIMIZE` is what actually works
5. **Clean up by ID.** `wsb stop --id <id>` on the environments that
   appeared, then kill any process left over

```powershell
./scripts/Invoke-SandboxRun.ps1 -ResultFolder ./artifacts/uitests `
  -Map @{Host="$PWD"; Sandbox='C:\repo'; ReadOnly=$false},
       @{Host=(Split-Path (Get-Command dotnet).Source); Sandbox='C:\Program Files\dotnet'} `
  -GuestWorkingDirectory 'C:\repo' `
  -Command 'set "DOTNET_ROOT=C:\Program Files\dotnet" && set "PATH=C:\Program Files\dotnet;%PATH%" && dotnet test tests\Ui.Tests\Ui.Tests.csproj --no-build --no-restore'
```

## Facts that bite

| | |
|---|---|
| **`wsb list` is the liveness check, not the process list** | A sandbox whose window is gone still holds the slot and still costs gigabytes. It has no `WindowsSandboxClient` process, so a check by process name can miss it entirely — `vmmemWindowsSandbox` and `WindowsSandboxRemoteSession` are what remain |
| **The window is not always `WindowsSandboxClient`'s** | On the Store sandbox (`wsb.exe`, 0.8.x) it belongs to `WindowsSandboxRemoteSession`. A minimize routine written against the inbox version finds nothing and quietly leaves the window in front |
| **`vmmem*` does not answer to `Stop-Process`** | It is a VM worker. Stop the environment with `wsb stop --id`; kill processes only as the fallback |
| **`vmmemCmZygote` is not a sandbox** | It is the pre-warmed base. Killing it costs the next launch its fast start |
| **Do not disable vGPU** | The automatic logon does not complete and `LogonCommand` never runs, so the sandbox comes up and does nothing. Microsoft describes `Disable` as a fall back to software rendering and recommends it for a guest that renders as a white square — that trade buys a visible guest and loses the run |
| **`ReadOnly` defaults to `false`** | An omitted `ReadOnly` gives the guest write access, and those writes land on the host disk and survive disposal. This is the one hole in "nothing persists" |
| **A missing `HostFolder` fails the whole container** | Not the mapping — the start |
| **`LogonCommand` takes exactly one command** | It runs after the folders are mounted, as `WDAGUtilityAccount` (an administrator in the guest), so point it at a `.cmd` mapped in from the host. A `.ps1` needs `-ExecutionPolicy Bypass` spelled out |
| **A guest `.cmd` needs CRLF and ASCII** | `cmd.exe` will not run a script with bare LF |
| **`MemoryInMB` under 2048 is silently raised** | Default 4096 |
| **A Feature on Demand can never be enabled in the guest** | `NetFx3` and its kind arrive `DisabledWithPayloadRemoved`, and the guest's default update service is WSUS with a null URL — so DISM, `Enable-WindowsOptionalFeature` and any caller of them all end at `0x80072ee6`, whatever the state of `wuauserv`. Nothing installed in the guest fixes it; the payload has nowhere to come from. A package that depends on one needs a real VM, not a sandbox — see `hyperv-clean-vm` |
| **`0x80072746` on the client is cosmetic** | The connection display fails; the guest still runs `LogonCommand` to completion and the results still come back. What it costs is the guest's own shutdown, which is why the host kills by ID afterwards |

Error codes when a sandbox will not start: `ERROR_FILE_NOT_FOUND` is the
`.wsb` path, `E_INVALIDARG` is malformed XML, `REGDB_E_IIDNOTREG` means
the feature is not enabled, `0x80070005` is usually a folder mapped onto
the guest desktop — map a subfolder instead.

Casing is not worth suspecting: Microsoft's own pages ship `<vGPU>`,
`<VGpu>` and `<Mappedfolders>` as examples, so the parser is
case-insensitive.

## Adding the sandbox to a new project

Copy `scripts/` into the repository — two files, nothing outside
PowerShell and `wsb.exe` — and call them from the project's own runner.
Then the runner works for a person, for CI, and for any agent, and it
keeps working when this skill is uninstalled.

That copy will drift from this one, and mostly that is fine: the guest
command, the mappings and the timeout are the project's business. Rule 1
is the part that must not drift. Everything else is local.

A repository that already has a working runner does not need the copy at
all. Applying rules 1 to 4 to it is enough to stop it colliding with the
others.

Keep in the project only what is about the project:

- The host-side build step
- The mappings and the guest command
- Which tests are sandbox-only. Pure unit tests do not take the keyboard
  and should stay on the host, where they run in seconds
