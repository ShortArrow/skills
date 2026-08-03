---
name: windows-sandbox
description: |
  Run e2e or UI tests inside Windows Sandbox, where SendInput cannot steal the developer's keyboard, and share the machine's single sandbox slot with other projects. Two agents each ending their run by terminating "the" sandbox terminate each other's; a finished-looking sandbox with no window still holds the slot; disabling vGPU stops LogonCommand from ever running. Use when a project needs an isolated Windows desktop, when a sandbox will not start, or when adding a second project that wants one.
allowed-tools: PowerShell, Read, Write, Edit
---

# Windows Sandbox as a test target

| Purpose | Script |
|---|---|
| Run a command in the sandbox and get the result back | `scripts/Invoke-SandboxRun.ps1` |
| Share the slot from a runner you already have | `scripts/SandboxLock.ps1` |

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

Windows allows **one sandbox instance at a time**, machine-wide.
Documented on the overview page and again in the FAQ, and the `wsb` CLI
does not lift it. Every project on the machine competes for the same slot,
which is where the damage comes from:

- A runner that ends with "kill the sandbox processes" kills whichever
  project's sandbox is running, not necessarily its own
- Checking "is one running?" and then launching is a race. Two runners
  both see zero, both launch, and both later believe the survivor is theirs

The fix is a lock held across the **whole** span — pre-flight, launch,
wait, clean-up — not just around the launch. `scripts/SandboxLock.ps1`
is an exclusively opened file under `%ProgramData%\WindowsSandbox\`.
Windows closes the handle when the owning process dies, so a killed
runner does not leave the lock stuck, and a waiter can read who is ahead
of it.

```powershell
. "$PSScriptRoot/SandboxLock.ps1"
$lock = Enter-SandboxLock -Owner 'BiosMonitorClassic uitests'
try     { <# launch, wait, clean up #> }
finally { Exit-SandboxLock $lock }
```

Under the lock, a sandbox that is already running belongs to someone
outside the protocol — a hand-started one, or a run left open for
debugging. **Refuse; never terminate it.** `Invoke-SandboxRun.ps1` does.

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
| **Do not disable vGPU** | Observed: the automatic logon never completes and `LogonCommand` never runs. The docs describe `Disable` as a fall back to software rendering and recommend it for a white-square guest; that trade is not worth a run that silently does nothing |
| **`ReadOnly` defaults to `false`** | An omitted `ReadOnly` gives the guest write access, and those writes land on the host disk and survive disposal. This is the one hole in "nothing persists" |
| **A missing `HostFolder` fails the whole container** | Not the mapping — the start |
| **`LogonCommand` takes exactly one command** | It runs after the folders are mounted, as `WDAGUtilityAccount` (an administrator in the guest), so point it at a `.cmd` mapped in from the host. A `.ps1` needs `-ExecutionPolicy Bypass` spelled out |
| **A guest `.cmd` needs CRLF and ASCII** | `cmd.exe` will not run a script with bare LF |
| **`MemoryInMB` under 2048 is silently raised** | Default 4096 |
| **`0x80072746` on the client is cosmetic** | The connection display fails; the guest still runs `LogonCommand` to completion and the results still come back. What it costs is the guest's own shutdown, which is why the host kills by ID afterwards |

Error codes when a sandbox will not start: `ERROR_FILE_NOT_FOUND` is the
`.wsb` path, `E_INVALIDARG` is malformed XML, `REGDB_E_IIDNOTREG` means
the feature is not enabled, `0x80070005` is usually a folder mapped onto
the guest desktop — map a subfolder instead.

Casing is not worth suspecting: Microsoft's own pages ship `<vGPU>`,
`<VGpu>` and `<Mappedfolders>` as examples, so the parser is
case-insensitive.

## Adding the sandbox to a new project

The project supplies one command line and one result folder; everything
above stays here. Keep in the project only what is about the project:

- The host-side build step
- The `-Map` entries and the guest command
- Which tests are sandbox-only. Pure unit tests do not take the keyboard
  and should stay on the host, where they run in seconds

## Provenance

The protocol comes from `BiosMonitorClassic` ADR-0012 and its
`scripts/run-uitests-sandbox.ps1`, where it was validated over 12 UI
tests at one to two minutes a run. Changed on extraction: the pre-flight
check became a held lock, because a check alone races; liveness and
shutdown go through the `wsb` CLI, because a windowless sandbox is
invisible to a process-name check; and the runner takes the command as a
parameter rather than hard-coding one project's `dotnet test`.
