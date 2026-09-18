<#
.SYNOPSIS
  Report whether a remote Windows machine can run GUI work, and name what is missing.

.DESCRIPTION
  Returns reasons rather than a boolean: an empty problem list means ready. The facts it
  gathers are printed alongside, because "ready" and "unreachable" otherwise look the
  same -- the checks run inside the machine, so a machine that cannot be reached reports
  no problems at all. No facts is read here as the failure it is.

  The screen size and the session id are measured by a probe that runs as its own short
  interactive task. Measured over SSH they would be session 0's, which is a fixed
  1024x768 desktop nobody is looking at, and not what the work will see.

  Exits 1 when something is missing, 0 when nothing is.

.PARAMETER Address
  The machine's IP address or host name.

.PARAMETER User
  The account to log on as.

.PARAMETER Name
  Names the working directory under %TEMP% and the probe task.

.PARAMETER RequiredFreeGB
  Free space on C: below which the machine is reported as not ready.

.PARAMETER GuestSshPath
  GuestSsh.ps1 from the windows-ssh-commands skill.

.EXAMPLE
  ./Test-GuestReadiness.ps1 -Address 172.28.10.5 -User User -Name myproject
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Address,
    [Parameter(Mandatory)][string]$User,
    [string]$Name = 'interactive-run',
    [int]$RequiredFreeGB = 5,
    [string]$GuestSshPath = "$PSScriptRoot\..\..\windows-ssh-commands\scripts\GuestSsh.ps1"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $GuestSshPath)) {
    throw "GuestSsh.ps1 not found at '$GuestSshPath'. Install the windows-ssh-commands skill beside this one, or pass -GuestSshPath."
}
. $GuestSshPath

$session = New-GuestSession -Address $Address -User $User
$taskName = "$Name-probe"

$guestRoot = Get-GuestValue -Session $session -Script "Join-Path `$env:TEMP '$Name'"
if (-not $guestRoot) { throw 'could not resolve the working directory on the guest' }

# What the probe measures has to be measured in the session the work will run in.
$probe = @"
`$out = '$guestRoot\readiness.txt'
New-Item -ItemType Directory -Path (Split-Path `$out) -Force | Out-Null
`$lines = @()
`$lines += 'SessionId=' + [System.Diagnostics.Process]::GetCurrentProcess().SessionId
try {
  Add-Type -AssemblyName System.Windows.Forms
  `$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  `$lines += 'Screen=' + `$b.Width + 'x' + `$b.Height
} catch { `$lines += 'Screen=unknown' }
`$lines | Set-Content -Path `$out -Encoding ascii
"@

$script = @"
`$problems = @()
`$facts = @{}

`$cs = Get-CimInstance Win32_ComputerSystem
`$facts['os'] = (Get-CimInstance Win32_OperatingSystem).Caption
`$facts['loggedOnUser'] = `$cs.UserName
if (-not `$cs.UserName) {
    `$problems += 'nobody is logged on. UI Automation only reaches a signed-in session; set up automatic logon.'
}

`$facts['freeGB'] = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
if (`$facts['freeGB'] -lt $RequiredFreeGB) {
    `$problems += ('only ' + `$facts['freeGB'] + ' GB free on C:.')
}

New-Item -ItemType Directory -Path '$guestRoot' -Force | Out-Null
Set-Content -Path '$guestRoot\readiness-probe.ps1' -Value @'
$probe
'@ -Encoding utf8
Remove-Item '$guestRoot\readiness.txt' -ErrorAction SilentlyContinue

`$a = New-ScheduledTaskAction -Execute 'powershell.exe' ``
    -Argument '-NoProfile -ExecutionPolicy Bypass -File "$guestRoot\readiness-probe.ps1"'
`$p = New-ScheduledTaskPrincipal -UserId `$cs.UserName -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName '$taskName' -Action `$a -Principal `$p -Force | Out-Null
Start-ScheduledTask -TaskName '$taskName'
Start-Sleep -Seconds 6
Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false -ErrorAction SilentlyContinue

if (Test-Path '$guestRoot\readiness.txt') {
    foreach (`$line in Get-Content '$guestRoot\readiness.txt') {
        `$k, `$v = `$line -split '=', 2
        `$facts[`$k] = `$v
    }
    if (`$facts['SessionId'] -eq '0') {
        `$problems += 'the interactive task ran in session 0. UI Automation will find nothing.'
    }
} else {
    `$problems += 'the interactive task left no result. It is not reaching a signed-in session.'
}

foreach (`$k in 'os','loggedOnUser','freeGB','SessionId','Screen') { 'FACT|' + `$k + '|' + `$facts[`$k] }
foreach (`$p in `$problems) { 'PROBLEM|' + `$p }
"@

$facts = @{}
$problems = @()
foreach ($line in (Invoke-GuestPowerShell -Session $session -Script $script)) {
    $text = "$line".Trim()
    if ($text -like 'FACT|*') { $parts = $text -split '\|', 3; $facts[$parts[1]] = $parts[2] }
    elseif ($text -like 'PROBLEM|*') { $problems += ($text -split '\|', 2)[1] }
}

# The judgement happens inside the machine, so an unreachable machine yields no PROBLEM
# lines and would otherwise count as ready.
if ($facts.Count -eq 0) {
    $problems += 'no response from the machine. Check that it is running and that SSH answers.'
}

foreach ($key in 'os', 'loggedOnUser', 'freeGB', 'SessionId', 'Screen') {
    Write-Host ("[host] {0,-13}: {1}" -f $key, $facts[$key])
}

Remove-GuestSession -Session $session

if ($problems.Count -gt 0) {
    Write-Host '[host] not ready:'
    $problems | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

Write-Host '[host] ready'
exit 0
