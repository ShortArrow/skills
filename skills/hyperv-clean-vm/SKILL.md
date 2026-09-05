---
name: hyperv-clean-vm
description: |
  Build a Hyper-V checkpoint you can return to for every run — clean state, SSH already listening, key already trusted — so an investigation that needs a pristine Windows repeats without a UAC prompt each time. Restoring a checkpoint taken before the account had a password silently breaks PowerShell Direct, and an administrator's key does not go in the usual file. Once the checkpoint exists this is the first choice over Windows Sandbox — restore beats rebuilding sandbox state, VMs run in parallel while the sandbox slot is single, and the instance survives for inspection. Use when a bug only reproduces on a machine with nothing preinstalled, when runs must repeat from identical state, and before reaching for the shared sandbox slot.
allowed-tools: PowerShell, Read, Write, Bash
---

# A clean VM you can rewind

**The checkpoint is the fixture.** Restore, run, observe, restore. The
value is that run N+1 starts identical to run N, which is exactly what a
host machine cannot offer once the software under test has been installed
on it even once.

Once a checkpoint exists, this is the first choice, not the fallback:
a restore is cheaper than building sandbox state from scratch, several
VMs run side by side while the machine has exactly one sandbox slot to
fight over, and the instance can still be inspected after the run.
Windows Sandbox (`windows-sandbox`) keeps one job — the machine where
no clean VM has been built yet and the need is a single disposable
desktop, once. Past preference, there is also what the sandbox cannot
do at all:

| Sandbox cannot | Why |
|---|---|
| Enable a Feature on Demand (`netfx3` and friends) | Its update source is WSUS with a null URL, so FoD metadata is unreachable. Every path fails `0x80072ee6` |
| Survive a reboot | Disposal is the point |
| Keep state between runs | Same |
| Be inspected after the window closes | The instance is gone, and so is the evidence |

## Once, on the host: Hyper-V Administrators

Every host-side call in this skill — `Get-VM`, `Start-VM`,
`Restore-VMSnapshot`, `Invoke-Command -VMName` — is checked against
Hyper-V's own authorization, and a non-elevated token, even an
administrator's, is refused with an error that names "the authorization
policy". `sudo` on every call is one answer. The durable one is the local
group made for this:

```powershell
sudo pwsh -c "Add-LocalGroupMember -Group 'Hyper-V Administrators' -Member $env:USERNAME"
```

**Then sign out and sign back in.** Group membership is written into the
logon token, and the current session keeps the old token — the same
command keeps failing with the same error until the account logs on
again. `whoami /groups | findstr /i hyper-v` shows whether the token you
are holding has it. After that, none of the `sudo` below is needed, and
the quoting problems that come with `sudo pwsh -c` do not arise.

## Order of operations

The order is the skill. Every step after the first is inside the guest,
and each one invalidates the checkpoint before it.

1. **Give the account a password.** Do this before anything else. A guest
   account with a blank password cannot be reached by PowerShell Direct,
   and the images Microsoft ships for Hyper-V Quick Create — `WinDev*Eval`
   — arrive that way. In the guest console: `net user User <password>`
2. **Verify PowerShell Direct works**, because step 3 needs a channel
   into a guest that has no SSH yet
3. **Install and start sshd inside the guest**
4. **Place the public key** — and mind where, see below
5. **Confirm a real SSH connection from the host**
6. **Clean up anything the setup left behind**
7. **Checkpoint.** Name it for what it contains, not for the date

Take the checkpoint only after step 5 succeeds. A checkpoint holding an
sshd you have not connected to is a checkpoint you will restore, fail
against, and have to rebuild.

## Steps 1–3, from the host

PowerShell Direct needs no network and no guest integration beyond the
default services. It does need Hyper-V access (the group above, or
`sudo`), and it does need that password.

```powershell
$p = ConvertTo-SecureString 'user' -AsPlainText -Force
$c = New-Object System.Management.Automation.PSCredential('user', $p)
Invoke-Command -VMName 'NAME' -Credential $c -ScriptBlock {
  Add-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0' | Out-Null
  Start-Service sshd
  Set-Service sshd -StartupType Automatic
  New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
  (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^127\.' }).IPAddress
}
```

The address it prints is on the Default Switch — reachable from the host,
nowhere else. That is the right amount of exposure for a fixture.

## Step 4: where the key goes

**An administrator's key does not live in `~/.ssh/authorized_keys`.**
Windows OpenSSH reads a separate file for any member of the local
Administrators group, and the ACL on it is enforced: inherited
permissions must be stripped or sshd ignores the file without saying so.

```powershell
$k = 'C:\ProgramData\ssh\administrators_authorized_keys'
Set-Content -Path $k -Value $pub -Encoding ascii
icacls $k /inheritance:r /grant 'Administrators:F' /grant 'SYSTEM:F'
Restart-Service sshd
```

Write the per-user file too. It costs one line and covers the case where
the account turns out not to be an administrator after all.

## Using it afterwards

Restoring is a host operation, so it needs the group (or `sudo`).
Everything after that is plain SSH.

```powershell
Restore-VMSnapshot -VMName 'NAME' -Name 'clean-sshd' -Confirm:$false; Start-VM -Name 'NAME'

$o = @('-F','NUL','-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=NUL','-i',"$HOME\.ssh\id_ed25519")
ssh @o User@172.28.x.x "hostname"
```

`-F NUL` is worth keeping even when the host's `~/.ssh/config` is
healthy. A fixture should not break because an unrelated config line
changed.

## Facts that bite

| | |
|---|---|
| **A restore rewinds the password too** | Any checkpoint predating step 1 comes back with the blank-password account, and PowerShell Direct stops working — with an authentication error that reads like a wrong password rather than a missing one |
| **The guest boots slower than the cmdlet returns** | `Start-VM` returns immediately. Retry the first connection in a loop; 10 attempts at 15 seconds covers a cold boot |
| **`start /b` over SSH dies with the session** | A long job launched that way is killed when the SSH command returns. `schtasks /create ... /sc once /st 00:00 /rl highest /f` then `/run` survives; write the output to a file and poll it |
| **Quoting collapses two levels deep** | `ssh` → `powershell -Command` → the script. Copy a `.ps1` with `scp` and run it with `-File`. Trying to inline it produces `Unexpected token` from a shell you are not looking at |
| **`sudo pwsh -c` cannot take a script block** | Pass `-File <path>` instead. The error names ScriptBlock and does not mention the fix. Joining Hyper-V Administrators removes the `sudo` and the problem with it |
| **Checkpoints chain** | A new one is a child of the current state, not of the VM. Restoring an ancestor keeps the descendants but they now branch. Name them so the intended entry point is obvious |
| **`Get-VM` is refused too, not just `Start-VM`** | The error names the authorization policy: that is Hyper-V Administrators, not UAC. Membership added in this session does not count — the token was cut at logon, so it fails identically until you sign out and in |

## What to record

The evidence must survive the next restore, so it cannot live only in the
guest. Either write to a folder mapped from the host, or `scp` it out
before rewinding. A trace file inside a VM you are about to reset is a
trace file you are about to delete.
