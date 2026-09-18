<#
.SYNOPSIS
  Take a stock Windows evaluation VM to a state where GUI work can be driven from the
  host, one verified stage at a time.

.DESCRIPTION
  A stock image has neither an SSH server nor automatic logon. Driving UI work from the
  host needs both: a way in that does not involve a person (sshd), and a signed-in
  desktop after every boot, because UI Automation only reaches a logged-on session.

  The work is cut into stages, and each stage ends by checkpointing what it has just
  proved. A stage that installed something is not a stage that works, so the
  verification comes first and the checkpoint after: a checkpoint holding an sshd you
  never connected to is one you will restore, fail against, and rebuild.

    Sshd       password, OpenSSH server, trusted key      -> clean-sshd
    Autologon  automatic logon, verified across a reboot  -> clean-autologon
    Packages   whatever the work needs, by winget id      -> clean-packages

  -Stage picks the entry point, so changing the last stage does not mean re-running the
  first.

  Order matters most at the start. The images Microsoft ships for Quick Create arrive
  with a blank password, and PowerShell Direct cannot authenticate to a blank-password
  account: a checkpoint taken before the password is set comes back unreachable, with an
  error that reads like a wrong password rather than a missing one. So the password is
  set before anything is checkpointed, and a failure there stops the run.

  Host-side calls need membership of the local Hyper-V Administrators group, effective
  only after signing out and in.

.PARAMETER VMName
  The VM to provision. It must already exist.

.PARAMETER GuestUser
  The guest's local account. Microsoft's development images use "User".

.PARAMETER GuestPassword
  The password to set. Automatic logon stores this in the LSA secret. There is no
  default: a password shipped in a script is a password everyone knows.

.PARAMETER PublicKeyPath
  The public key to trust in the guest.

.PARAMETER Stage
  All, Sshd, Autologon or Packages.

.PARAMETER WingetPackage
  Package ids installed in the Packages stage, in order.

.PARAMETER VerifyPackageCommand
  A PowerShell expression run in the guest after the packages are installed. It must
  print something; whatever it prints is matched against -VerifyPackagePattern. Leave
  both empty to skip the check -- at the cost of a checkpoint that may hold a failed
  install.

.PARAMETER VerifyPackagePattern
  A regular expression the verification output must match.

.PARAMETER MemoryStartupGB
  Dynamic memory's startup size. Fixed memory is claimed in full at power-on, and a
  developer's machine cannot promise that much, so the VM simply fails to start.

.PARAMETER MemoryMinimumGB
  Lower bound while the guest idles.

.PARAMETER MemoryMaximumGB
  Upper bound. A GUI run grows into it.

.PARAMETER GuestSshPath
  GuestSsh.ps1 from the windows-ssh-commands skill.

.EXAMPLE
  ./New-HyperVFixtureVM.ps1 -VMName WinDev -GuestPassword (Read-Host 'guest password')

.EXAMPLE
  ./New-HyperVFixtureVM.ps1 -VMName WinDev -GuestPassword $password -Stage Packages `
      -WingetPackage 'Git.Git' `
      -VerifyPackageCommand '& "C:\Program Files\Git\cmd\git.exe" --version' `
      -VerifyPackagePattern '^git version'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$VMName,
    [string]$GuestUser = 'User',
    [Parameter(Mandatory)][string]$GuestPassword,
    [string]$PublicKeyPath = "$HOME\.ssh\id_ed25519.pub",
    [ValidateSet('All', 'Sshd', 'Autologon', 'Packages')]
    [string]$Stage = 'All',
    [string[]]$WingetPackage = @(),
    [string]$VerifyPackageCommand = '',
    [string]$VerifyPackagePattern = '',
    [int]$MemoryStartupGB = 4,
    [int]$MemoryMinimumGB = 2,
    [int]$MemoryMaximumGB = 8,
    [int]$TimeoutMinutes = 10,
    [string]$GuestSshPath = "$PSScriptRoot\..\..\windows-ssh-commands\scripts\GuestSsh.ps1"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $GuestSshPath)) {
    throw "GuestSsh.ps1 not found at '$GuestSshPath'. Install the windows-ssh-commands skill beside this one, or pass -GuestSshPath."
}
. $GuestSshPath

$addressScript = Join-Path $PSScriptRoot 'Get-HyperVGuestAddress.ps1'

function Get-Session {
    $address = & $addressScript -VMName $VMName
    New-GuestSession -Address $address -User $GuestUser
}

# ---------------------------------------------------------------------------

$vm = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if (-not $vm) { throw "no VM named '$VMName'" }

# Memory configuration only applies while the VM is off. Powering a running VM off to
# apply it destroys whatever it was running for -- someone watching it, another run in
# progress -- so the running case is a warning, not an action.
if ($vm.State -eq 'Off') {
    Set-VM -Name $VMName -DynamicMemory `
        -MemoryStartupBytes ($MemoryStartupGB * 1GB) `
        -MemoryMinimumBytes ($MemoryMinimumGB * 1GB) `
        -MemoryMaximumBytes ($MemoryMaximumGB * 1GB)
    Write-Host "dynamic memory: startup $MemoryStartupGB / min $MemoryMinimumGB / max $MemoryMaximumGB GB" -ForegroundColor Cyan
}
elseif (-not $vm.DynamicMemoryEnabled) {
    Write-Warning "VM is $($vm.State), so memory was left as fixed $([int]($vm.MemoryStartup / 1GB)) GB"
}

if ($vm.State -ne 'Running') {
    Write-Host 'starting the VM' -ForegroundColor Cyan
    Start-VM -Name $VMName
}

# --- Sshd -------------------------------------------------------------------
# PowerShell Direct needs no network and no key, which makes it the only way in before
# sshd exists. It does need the account to have a password.
if ($Stage -in 'All', 'Sshd') {
    Write-Host '== sshd ==' -ForegroundColor Cyan

    if (-not (Test-Path $PublicKeyPath)) { throw "no public key at $PublicKeyPath" }
    $publicKey = (Get-Content $PublicKeyPath -Raw).Trim()

    $credential = New-Object System.Management.Automation.PSCredential(
        $GuestUser, (ConvertTo-SecureString $GuestPassword -AsPlainText -Force))

    Invoke-Command -VMName $VMName -Credential $credential -ScriptBlock {
        param($User, $Password, $PublicKey)

        # Swallowing this failure would carry a blank-password account into the first
        # checkpoint, and every later restore would lose PowerShell Direct with it.
        net user $User $Password | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "could not set the guest password (net user exit=$LASTEXITCODE)" }

        Add-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0' | Out-Null
        Set-Service -Name sshd -StartupType Automatic
        Start-Service sshd
        New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
            -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 `
            -ErrorAction SilentlyContinue | Out-Null

        # sshd's default shell is cmd. Scripts name powershell explicitly anyway, but an
        # interactive session landing in cmd is a surprise nobody needs.
        New-Item -Path 'HKLM:\SOFTWARE\OpenSSH' -Force | Out-Null
        Set-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell `
            -Value 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -Type String

        # A member of the Administrators group is not served by ~/.ssh/authorized_keys.
        # The shipped sshd_config points at this file instead, and sshd ignores it -
        # without a word - unless inherited permissions are stripped.
        $adminKeys = "$env:ProgramData\ssh\administrators_authorized_keys"
        Set-Content -Path $adminKeys -Value $PublicKey -Encoding ascii
        icacls $adminKeys /inheritance:r /grant 'SYSTEM:F' /grant 'BUILTIN\Administrators:F' | Out-Null

        # And the per-user file too, for the day the account is not an administrator.
        $userSsh = Join-Path $env:USERPROFILE '.ssh'
        New-Item -ItemType Directory -Force $userSsh | Out-Null
        Set-Content -Path (Join-Path $userSsh 'authorized_keys') -Value $PublicKey -Encoding ascii

        Restart-Service sshd
    } -ArgumentList $GuestUser, $GuestPassword, $publicKey

    $session = Get-Session
    if (-not (Wait-GuestSsh -Session $session -Minutes $TimeoutMinutes)) {
        throw "sshd did not answer within $TimeoutMinutes minutes"
    }
    Write-Host "  the key opens a session: $($session.Address)" -ForegroundColor Green

    Checkpoint-VM -Name $VMName -SnapshotName 'clean-sshd'
    Write-Host '  checkpoint clean-sshd' -ForegroundColor Green
}

# --- Autologon --------------------------------------------------------------
# SSH and PowerShell Direct both land in session 0. Without automatic logon, every
# reboot needs a person before any GUI work can run.
if ($Stage -in 'All', 'Autologon') {
    Write-Host '== automatic logon ==' -ForegroundColor Cyan
    $session = Get-Session

    # Sysinternals Autologon puts the password in the LSA secret rather than in a
    # plaintext registry value. The msstore source can fail certificate validation, and
    # winget then stops unable to choose a candidate, so name the source.
    $install = @'
$ProgressPreference = "SilentlyContinue"
winget install --id Microsoft.Sysinternals.Autologon --source winget `
    --accept-package-agreements --accept-source-agreements --disable-interactivity 2>&1 |
    Select-Object -Last 3
'@
    Invoke-GuestPowerShell -Session $session -Script $install | ForEach-Object { "  $_" }

    $configure = @"
`$exe = Get-ChildItem "`$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter 'Autologon64.exe' |
    Select-Object -First 1 -ExpandProperty FullName
if (-not `$exe) { throw 'Autologon64.exe not found' }
& `$exe /accepteula '$GuestUser' `$env:COMPUTERNAME '$GuestPassword'
`$k = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
(Get-ItemProperty `$k -Name AutoAdminLogon).AutoAdminLogon
"@
    $applied = Invoke-GuestPowerShell -Session $session -Script $configure
    if ($applied -notcontains '1') { throw "AutoAdminLogon did not become 1: $applied" }

    # A registry value is not evidence that automatic logon works. Reboot, and see
    # whether a desktop comes up with nobody touching it.
    Write-Host '  rebooting to measure it' -ForegroundColor Cyan
    & ssh @($session.SshOptions) $session.Target 'shutdown /r /t 0' 2>&1 | Out-Null
    Start-Sleep -Seconds 20

    $session = Get-Session
    if (-not (Wait-GuestSsh -Session $session -Minutes $TimeoutMinutes)) {
        throw 'sshd did not answer after the reboot'
    }

    $verify = @'
$p = Get-Process explorer -ErrorAction SilentlyContinue | Where-Object SessionId -gt 0
if ($p) { "session=" + ($p | Select-Object -First 1).SessionId } else { "no interactive session" }
'@
    $observed = Get-GuestValue -Session $session -Script $verify
    if ($observed -notmatch '^session=[1-9]') { throw "automatic logon did not happen: $observed" }
    Write-Host "  nobody touched it and there is a desktop: $observed" -ForegroundColor Green

    Checkpoint-VM -Name $VMName -SnapshotName 'clean-autologon'
    Write-Host '  checkpoint clean-autologon' -ForegroundColor Green
}

# --- Packages ---------------------------------------------------------------
# Installed in the guest and baked into a checkpoint, rather than copied in per run: a
# missing runtime fails at a distance, in whatever the work does next, and the message
# never mentions the runtime.
if ($Stage -in 'All', 'Packages' -and $WingetPackage.Count -gt 0) {
    Write-Host '== packages ==' -ForegroundColor Cyan
    $session = Get-Session

    $ids = ($WingetPackage | ForEach-Object { "'$_'" }) -join ','
    $install = @"
`$ProgressPreference = "SilentlyContinue"
foreach (`$id in @($ids)) {
    winget install --id `$id --source winget ``
        --accept-package-agreements --accept-source-agreements --disable-interactivity 2>&1 |
        Select-Object -Last 1
}
"@
    Invoke-GuestPowerShell -Session $session -Script $install | ForEach-Object { "  $_" }

    if ($VerifyPackageCommand) {
        $observed = Get-GuestValue -Session $session -Script $VerifyPackageCommand
        if ($VerifyPackagePattern -and $observed -notmatch $VerifyPackagePattern) {
            throw "the packages did not verify. '$VerifyPackageCommand' printed: $observed"
        }
        Write-Host "  verified: $observed" -ForegroundColor Green
    } else {
        Write-Warning '  no verification was asked for, so this checkpoint may hold a failed install'
    }

    Checkpoint-VM -Name $VMName -SnapshotName 'clean-packages'
    Write-Host '  checkpoint clean-packages' -ForegroundColor Green
}

Write-Host ''
Get-VMCheckpoint -VMName $VMName | Sort-Object CreationTime |
    Select-Object Name, CreationTime, ParentCheckpointName | Format-Table -AutoSize
