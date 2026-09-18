---
name: windows-ssh-commands
description: |
  Sending commands and files to a Windows machine over SSH from a PowerShell caller. Triggered by the moments that break it silently: about to inline a script in an ssh command line, about to hand it to powershell with -EncodedCommand, about to write the script file without a BOM, about to read ssh or scp output as the result without checking $LASTEXITCODE, about to give scp a remote path holding backslashes or spaces, about to pass NUL as UserKnownHostsFile, about to call a step done because it printed no error, or about to trust a readiness check that runs inside the machine you cannot reach. Quoting collapses three shells deep, an encoded command line hides what actually ran, and PowerShell does not stop on a native non-zero exit. Use when automating a Windows guest, VM or remote box over OpenSSH.
allowed-tools: PowerShell, Read, Write, Bash
---

# Talking to Windows over SSH

Three things sit between the caller and the code that runs:
the local `ssh` client, the remote default shell,
and the PowerShell that finally reads the script.
Every one of them parses quotes,
and a failure at any of them is reported by the layer above as something else.

**Copy a file, run it with `-File`.** That is the whole technique,
and the rest of this skill is what happens when it is not followed.

`scripts/GuestSsh.ps1` is a reference implementation of everything below — dot-source it,
or copy it into the repository that needs it.
It is not a runtime dependency:
a project's own runner has to work for a person and for a CI runner,
neither of which has this skill installed.

| Function | |
|---|---|
| `New-GuestSession` | The machine, the account and the ssh options, in one object |
| `Invoke-GuestPowerShell` / `Get-GuestValue` | Run a script there; the second returns one trimmed string |
| `Copy-GuestScript` / `Invoke-GuestScriptFile` | Send once, call many times — for a polling loop |
| `Copy-GuestItem` / `Receive-GuestItem` | Files out and back, with the path rules applied |
| `Wait-GuestSsh` | Wait for the machine to answer, rather than sleeping a guess |
| `Remove-GuestSession` | Delete the step file this process left behind |

```powershell
$local = Join-Path ([IO.Path]::GetTempPath()) "step-$PID.ps1"
[IO.File]::WriteAllText($local, $script, (New-Object Text.UTF8Encoding $true))
& scp @sshOptions -q $local "${user}@${address}:step-$PID.ps1"
if ($LASTEXITCODE -ne 0) { throw "could not send the script (exit=$LASTEXITCODE)" }

$out = & ssh @sshOptions "$user@$address" `
  "powershell -NoProfile -ExecutionPolicy Bypass -File step-$PID.ps1" 2>&1
if ($LASTEXITCODE -ne 0) { throw "the guest failed the step (exit=$LASTEXITCODE): $out" }
```

A relative destination lands in the account's home directory,
which is the one path you can use before you know anything about the machine.
Name the file after the caller's process id so two runs against one machine do not overwrite each other's step.

## Never `-EncodedCommand`

It looks like the answer to quoting: base64 of UTF-16LE passes quotes,
pipes and non-ASCII text through untouched.
It is the wrong answer.
An encoded command line is opaque — you cannot read it in a log,
cannot diff it,
and cannot see what actually ran when a step misbehaves — and it buys nothing a file does not.

A file plus `-File` solves the same quoting problem and stays readable.
Copy the script, run it, and there is nothing to encode.

## The file is written UTF-8 with a BOM

Windows PowerShell 5.1 — still the `powershell.exe` on the far end — reads a file with no BOM as ANSI in the machine's code page.
A script holding Japanese, or any other non-ASCII text,
is then mojibake before it runs,
and the error it raises is a parse error on a line that looks fine in your editor.

`New-Object Text.UTF8Encoding $true` is the `$true` that matters.

## Filter CLIXML out of the output

Remote PowerShell writes its progress stream to stderr as CLIXML.
Merge stderr into stdout (`2>&1`) and those fragments arrive interleaved with the result:

```powershell
$out | Where-Object { $_ -notmatch '^#< CLIXML' -and $_ -notmatch '^<Objs ' }
```

Drop them at the one place that runs guest commands,
not at every call site.

## PowerShell does not stop at a failing exe

`$ErrorActionPreference = 'Stop'` does not apply to a native executable's exit status.
`ssh` and `scp` return their codes and the script keeps going.

This is the failure that costs a whole afternoon:
a collection step fails, the script continues,
and the caller reads the artifacts that were already on disk from the previous run.
The run is reported green against yesterday's results.

Check `$LASTEXITCODE` after **every** `ssh` and `scp`.
Where a step can fail transiently — `sshd` answers `Connection closed` when it cannot set up a session — retry two or three times with a pause,
and throw when the last attempt fails.
A polling loop is the exception:
a single dropped connection should not end a twenty-minute wait,
so tolerate one failure there and let the deadline decide.

## Two different ssh clients, two different path rules

Windows has Win32-OpenSSH in `System32`;
Git for Windows ships an MSYS build,
and a PowerShell script invoked from a bash-flavoured shell may pick up either one.
They disagree exactly where it hurts:

| | Win32-OpenSSH | MSYS (Git) |
|---|---|---|
| `-o UserKnownHostsFile=NUL` | the null device | creates a file literally named `NUL` in the working directory |
| `-o UserKnownHostsFile=/dev/null` | works | works |
| A backslash in a **remote source** path | kept | eaten as an escape: `C:\Users\User\...` collapses to `C:UsersUser...` |
| A backslash in a **remote destination** path | kept | kept |

The asymmetry in the last two rows is why this hides so well:
sending works, so the transfer code looks correct,
and only the collection at the end of the run silently fetches nothing.

Two habits cover both clients.
Use `/dev/null` for the known-hosts file,
and convert any remote path to forward slashes before it goes anywhere near a glob:

```powershell
$remote = ($guestRoot -replace '\\', '/') + '/artifacts/*'
& scp @sshOptions -r -q "${user}@${address}:$remote" $localDir
if ($LASTEXITCODE -ne 0) { throw "could not collect the artifacts (exit=$LASTEXITCODE)" }
```

## Spaces in a remote path: stage, then move

How a remote destination containing spaces is quoted depends on the client,
and `C:\Program Files\...` is exactly where runtimes and frameworks live.

Copy into a space-free working directory and move the file inside the machine,
where one shell does the parsing:

```powershell
& scp @sshOptions -r -q $source "${user}@${address}:$stagingDir/$name"
# then, on the far end
Move-Item "$stagingDir\$name" -Destination $destinationWithSpaces -Force
```

## Compose paths on the far end

The account's home directory,
`%TEMP%` and the drive layout belong to the machine, not to you.
Ask for them:

```powershell
$guestRoot = (Invoke-GuestPowerShell -Script "Join-Path `$env:TEMP '$projectName\run'").Trim()
if (-not $guestRoot) { throw 'could not resolve the working directory' }
```

Naming the directory after the project rather than the product keeps two projects sharing one machine out of each other's way,
and keeps the product name out of the script.

## Write, then read back

A step that reports "3 lines written" has reported that it wrote three lines.
It has not reported that the lines say what you meant.

A here-string that expands (`@"…"@`) evaluates every `$` inside it on the caller's side,
so a single missing backtick embeds a caller-side expression as literal text on the far end — quotation marks,
concatenation operators and all.
The write succeeds, the count is right, and the value is nonsense.

Read the value back and check it means something:
that the path exists on the machine,
that the key is in the section you intended,
that the service is listening.
Throw when it does not.

Configuration files with the same key name in two sections are the sharp case.
A blind text replacement writes one section's value into the other,
and the program reads the wrong value without complaining.
Edit section-aware, then read the section back.

## An unreachable machine reports no problems

When a readiness check runs inside the machine,
every problem it can find is found in there.
An unreachable machine finds nothing, returns nothing,
and the caller counts zero problems.

Return facts alongside the problems and treat the absence of facts as the failure:

```powershell
if ($facts.Count -eq 0) { $problems += 'no response: check that the machine is up and SSH is reachable' }
```

## Facts that bite

| | |
|---|---|
| **The default shell for `sshd` is `cmd`** | Point `HKLM:\SOFTWARE\OpenSSH\DefaultShell` at `powershell.exe` for the interactive case, and keep naming `powershell -File` explicitly in scripts anyway |
| **A key for an administrator goes in another file** | `%ProgramData%\ssh\administrators_authorized_keys`, with inheritance stripped and only SYSTEM and Administrators granted, or sshd ignores it without a word |
| **`BatchMode=yes` turns a hang into an error** | Without it a missing key waits at a password prompt that nobody will ever answer |
| **The script file stays on the far end** | Delete it when the run ends, or every run leaves one more `step-<pid>.ps1` in the home directory |
| **A polling loop should not re-send its script** | Copy the wait script once and call it by name; hundreds of iterations otherwise mean hundreds of transfers |
| **stderr merged into stdout changes the type** | `2>&1` turns lines into `ErrorRecord` objects. `"$out".Trim()` before comparing, or a match against a plain string quietly fails |
