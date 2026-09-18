<#
.SYNOPSIS
  Skeleton for the script that runs inside the logged-on session.

.DESCRIPTION
  Invoke-GuestInteractiveRun.ps1 copies this file to the machine and starts it as a
  scheduled task with an interactive principal. Nothing here can report back to the
  caller: the sessions are different and no stream connects them. The answer is written
  to files under <Root>\artifacts, and done.marker is written last.

  Replace the block marked "the work" with the command to run. Everything around it is
  the part that is the same every time.

.PARAMETER Root
  The working directory, holding whatever was staged plus artifacts\. Passed by the
  caller; the default only matters when this is run by hand on the machine itself.

.NOTES
  ASCII only: a BOM-less non-ASCII .ps1 is read as ANSI and corrupted before it runs.
  ErrorActionPreference stays Continue so that a failure still reaches the two lines at
  the end that tell the caller what happened.
#>
[CmdletBinding()]
param(
    [string]$Root = (Join-Path $env:TEMP 'interactive-run')
)

$ErrorActionPreference = 'Continue'

$artifactsDir = Join-Path $Root 'artifacts'
$logFile = Join-Path $artifactsDir 'run.log'
$exitCodeFile = Join-Path $artifactsDir 'exitcode.txt'
$doneMarker = Join-Path $artifactsDir 'done.marker'
$helpers = @()

New-Item -ItemType Directory -Path $artifactsDir -Force | Out-Null

function Write-Log {
    param([string]$Message)
    "[guest] $Message" | Add-Content -Path $logFile -Encoding utf8
}

"[guest] start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content -Path $logFile -Encoding utf8
Write-Log "session=$([System.Diagnostics.Process]::GetCurrentProcess().SessionId)"

# Session 0 has a fixed 1024x768 desktop, so the size measured over SSH is not the size
# the work sees. Record the real one here: when a click misses three weeks from now,
# this line is what says the window was taller than the screen.
try {
    Add-Type -AssemblyName System.Windows.Forms
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen
    Write-Log "screen=$($screen.Bounds.Width)x$($screen.Bounds.Height) workarea=$($screen.WorkingArea.Width)x$($screen.WorkingArea.Height)"
} catch {
    Write-Log "WARN: could not read the screen size: $($_.Exception.Message)"
}

# Values too awkward for a task's single argument string arrive as files.
$filterFile = Join-Path $artifactsDir 'filter.txt'
$filter = if (Test-Path $filterFile) { (Get-Content $filterFile -Raw).Trim() } else { '' }
Write-Log "filter=$filter"

# --- helpers ---------------------------------------------------------------
# A background process started over SSH is killed when the ssh command returns:
# Win32-OpenSSH puts the process tree in a job object and terminates it. Started here,
# a helper's lifetime is bounded by the run instead, and this task is also the only
# place an environment variable set for it reaches the child.
#
#   $helpers += Start-Process -FilePath "$Root\tools\helper.exe" -PassThru `
#       -WindowStyle Hidden `
#       -RedirectStandardOutput (Join-Path $artifactsDir 'helper.log') `
#       -RedirectStandardError  (Join-Path $artifactsDir 'helper.err')

# --- the work --------------------------------------------------------------
$exitCode = 1
try {
    # Replace this with the real command. Write its output into the log; the caller
    # reads the tail of that file, and it is the only trace once the machine moves on.
    & (Join-Path $Root 'testun.cmd') --filter "$filter" --results $artifactsDir 2>&1 |
        Add-Content -Path $logFile -Encoding utf8
    $exitCode = $LASTEXITCODE
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
}

# --- the answer ------------------------------------------------------------
# Helpers die before the marker is written. On a machine that stays up, one left
# holding a port makes the next run's copy fail to bind, and a record file it keeps
# open answers a test that should have found nothing.
foreach ($helper in $helpers) {
    try { Stop-Process -Id $helper.Id -Force -ErrorAction SilentlyContinue } catch { }
}

Set-Content -Path $exitCodeFile -Value $exitCode -Encoding ascii
Write-Log "end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') exit=$exitCode"

# Last, and only last: the caller's wait ends the moment this file appears.
Set-Content -Path $doneMarker -Value 'done' -Encoding ascii
