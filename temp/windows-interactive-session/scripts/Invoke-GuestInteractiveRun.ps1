<#
.SYNOPSIS
  Run a script in a remote Windows machine's logged-on desktop session and collect what
  it produced.

.DESCRIPTION
  SSH lands in session 0, where UI Automation sees nothing and a window nobody can look
  at. This script crosses into the logged-on session the only way that exists: a
  scheduled task whose principal is -LogonType Interactive.

  The task cannot report back, so the guest-side script writes its answer down
  (guest-run-template.ps1 is the skeleton) and this one polls for the completion marker:

    <GuestRoot>\artifacts\run.log        progress
    <GuestRoot>\artifacts\exitcode.txt   the exit code
    <GuestRoot>\artifacts\done.marker    written last, and only last

  Stale files from the previous run are deleted before the task starts. A leftover
  marker ends the wait immediately and the caller collects the previous run's results.

  Exits with the guest-side exit code.

.PARAMETER Address
  The machine's IP address or host name. For a Hyper-V guest, resolve it first with
  Get-HyperVGuestAddress.ps1 (hyperv-persistent-vm) rather than writing it down.

.PARAMETER User
  The account to log on as. It must be the account that is signed in on the console, or
  the task has no session to run in.

.PARAMETER GuestScript
  The local script to run in the interactive session. Copied to <GuestRoot> and named in
  the task's action.

.PARAMETER Stage
  Local directories or files to copy into <GuestRoot> before the run, as an ordered
  dictionary of <guest subdirectory> = <local path>.

.PARAMETER Value
  Values the guest-side script needs, as <file name> = <text>. Written into
  <GuestRoot>\artifacts. A scheduled task's action is one string, so anything holding
  |, =, a quote or non-ASCII text goes through a file instead of through the argument.

.PARAMETER Clean
  Guest subdirectories of <GuestRoot> to delete before staging.

.PARAMETER OutputDirectory
  Local directory the artifacts are collected into. Emptied at the start of the run,
  before anything that can fail: a run that dies halfway otherwise leaves the last
  successful run's artifacts where the reader expects fresh ones.

.PARAMETER Name
  Names the working directory under the machine's %TEMP% and the scheduled task. Use
  the project's name, so two projects sharing one machine stay out of each other's way.

.PARAMETER GuestRoot
  The working directory. Resolved on the far end from %TEMP% and -Name when omitted;
  the account's temp path and drive layout belong to the machine, not to the caller.

.PARAMETER TimeoutMinutes
  How long to wait for the marker before unregistering the task and failing.

.PARAMETER GuestSshPath
  GuestSsh.ps1 from the windows-ssh-commands skill. Defaults to the sibling skill's
  copy; pass a path when only this skill is installed.

.EXAMPLE
  ./Invoke-GuestInteractiveRun.ps1 -Address 172.28.10.5 -User User -Name myproject `
      -GuestScript ./guest-run-template.ps1 `
      -Stage ([ordered]@{ app = './build/app'; test = './build/tests' }) `
      -Value @{ 'filter.txt' = 'Category=UI|Category=Smoke' } `
      -OutputDirectory ./artifacts/ui-tests
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Address,
    [Parameter(Mandatory)][string]$User,
    [Parameter(Mandatory)][string]$GuestScript,
    [System.Collections.IDictionary]$Stage = @{},
    [System.Collections.IDictionary]$Value = @{},
    [string[]]$Clean = @(),
    [string]$OutputDirectory = (Join-Path (Get-Location) 'artifacts'),
    [string]$Name = 'interactive-run',
    [string]$GuestRoot = '',
    [int]$TimeoutMinutes = 25,
    [string]$GuestSshPath = "$PSScriptRoot\..\..\windows-ssh-commands\scripts\GuestSsh.ps1"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $GuestSshPath)) {
    throw "GuestSsh.ps1 not found at '$GuestSshPath'. Install the windows-ssh-commands skill beside this one, or pass -GuestSshPath."
}
. $GuestSshPath

if (-not (Test-Path $GuestScript)) { throw "guest script not found: $GuestScript" }

$taskName = "$Name-interactive"
$session = New-GuestSession -Address $Address -User $User

# Empty the local output directory first. Anything below can fail, and a half-finished
# run must not leave the previous run's results looking like this one's.
if (Test-Path $OutputDirectory) {
    Remove-Item (Join-Path $OutputDirectory '*') -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

if (-not $GuestRoot) {
    $GuestRoot = Get-GuestValue -Session $session -Script "Join-Path `$env:TEMP '$Name'"
    if (-not $GuestRoot) { throw 'could not resolve the working directory on the guest' }
}
Write-Host "[host] guest $Address, work dir $GuestRoot"

# Delete the previous run's answer before starting, not after finishing: a leftover
# done.marker ends the wait instantly, and a log opened for appending mixes two runs.
$cleanList = ($Clean | ForEach-Object { "'$_'" }) -join ','
$prepare = @"
foreach (`$stale in 'done.marker','exitcode.txt','run.log') {
    Remove-Item (Join-Path '$GuestRoot\artifacts' `$stale) -Force -ErrorAction SilentlyContinue
}
foreach (`$directory in @($cleanList)) {
    `$path = Join-Path '$GuestRoot' `$directory
    if (Test-Path `$path) { Remove-Item `$path -Recurse -Force -ErrorAction SilentlyContinue }
}
New-Item -ItemType Directory -Path '$GuestRoot\artifacts' -Force | Out-Null
"@
Invoke-GuestPowerShell -Session $session -Script $prepare | Out-Null

foreach ($entry in $Stage.GetEnumerator()) {
    Write-Host "[host] staging $($entry.Value) -> $GuestRoot/$($entry.Key)"
    Copy-GuestItem -Session $session -Path $entry.Value -Destination "$GuestRoot/$($entry.Key)" -Recurse
}

$guestScriptName = Split-Path $GuestScript -Leaf
Copy-GuestItem -Session $session -Path $GuestScript -Destination "$GuestRoot/$guestScriptName"

foreach ($entry in $Value.GetEnumerator()) {
    Invoke-GuestPowerShell -Session $session -Script @"
Set-Content -Path '$GuestRoot\artifacts\$($entry.Key)' -Value '$($entry.Value)' -Encoding ascii -NoNewline
"@ | Out-Null
}

# The principal is read from the machine rather than assumed, so this works against a
# differently named account. An empty UserName means nobody is signed in, and an
# interactive task then has no session to run in: fail here, where it can be explained.
Write-Host "[host] starting the interactive task"
$start = @"
`$me = (Get-CimInstance Win32_ComputerSystem).UserName
if (-not `$me) { throw 'nobody is logged on: an interactive task has no session to run in' }
`$action = New-ScheduledTaskAction -Execute 'powershell.exe' ``
    -Argument '-NoProfile -ExecutionPolicy Bypass -File "$GuestRoot\$guestScriptName" -Root "$GuestRoot"'
`$principal = New-ScheduledTaskPrincipal -UserId `$me -LogonType Interactive -RunLevel Highest
`$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries ``
    -ExecutionTimeLimit ([TimeSpan]::Zero)
Register-ScheduledTask -TaskName '$taskName' -Action `$action -Principal `$principal -Settings `$settings -Force | Out-Null
Start-ScheduledTask -TaskName '$taskName'
"@
Invoke-GuestPowerShell -Session $session -Script $start | Out-Null

# The wait script is copied once and called by name. Sent again every iteration, a long
# run would mean hundreds of transfers of the same two lines.
$waitScript = "$Name-wait-$PID.ps1"
Copy-GuestScript -Session $session -Name $waitScript -Script @"
if (Test-Path '$GuestRoot\artifacts\done.marker') { 'yes' } else { 'no' }
"@ | Out-Null

$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
Write-Host "[host] waiting for done.marker (timeout $TimeoutMinutes min, started $(Get-Date -Format HH:mm:ss))"
while ($true) {
    # Tolerant: one dropped connection must not end a long run. The deadline decides.
    $done = Invoke-GuestScriptFile -Session $session -Name $waitScript -Tolerant
    if ("$done".Trim() -eq 'yes') { break }

    if ((Get-Date) -gt $deadline) {
        Invoke-GuestPowerShell -Session $session -Script @"
Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false -ErrorAction SilentlyContinue
"@ -Tolerant | Out-Null
        throw "timed out: no done.marker within $TimeoutMinutes minutes. Open the console and look at the desktop."
    }
    Start-Sleep -Seconds 5
}

Receive-GuestItem -Session $session -RemotePath "$GuestRoot/artifacts/*" -Destination $OutputDirectory

Invoke-GuestPowerShell -Session $session -Script @"
Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false -ErrorAction SilentlyContinue
Remove-Item '$waitScript' -Force -ErrorAction SilentlyContinue
"@ | Out-Null
Remove-GuestSession -Session $session

$logFile = Join-Path $OutputDirectory 'run.log'
if (Test-Path $logFile) {
    Write-Host '--- log tail ---'
    Get-Content $logFile -Tail 40
}

$exitCodeFile = Join-Path $OutputDirectory 'exitcode.txt'
$exitCode = if (Test-Path $exitCodeFile) { [int](Get-Content $exitCodeFile -First 1) } else { 1 }
Write-Host "[host] finished with exit=$exitCode"
exit $exitCode
