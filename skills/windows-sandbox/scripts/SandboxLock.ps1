<#
.SYNOPSIS
  Machine-wide mutual exclusion for the one Windows Sandbox instance.

.DESCRIPTION
  Copy this into the repository that uses it. What runners must share is
  the lock file and the way it is opened -- an implementation in any
  language that opens %ProgramData%\WindowsSandbox\runner.lock for write
  with FILE_SHARE_READ cooperates with this one.

  Windows Sandbox runs one instance at a time, so every runner on the
  machine is competing for the same slot. The lock is an exclusively held
  file: the owning process keeps the handle open, and Windows closes it
  when that process dies, so a crash cannot leave the lock stuck.

  Dot-source this file, then wrap the whole launch-and-clean-up span:

      . "$PSScriptRoot/SandboxLock.ps1"
      $lock = Enter-SandboxLock -Owner 'my-repo uitests'
      try   { ... launch, wait, kill ... }
      finally { Exit-SandboxLock $lock }

  Holding it only across the launch is not enough. The clean-up is what
  kills other people's sandboxes.
#>

$script:SandboxLockPath = Join-Path $env:ProgramData 'WindowsSandbox\runner.lock'

function Get-SandboxLockHolder {
  <#
  .SYNOPSIS
    Who currently holds the lock, as a single line. Empty when unreadable.
  .DESCRIPTION
    Only meaningful while acquisition is failing: the file also survives a
    release, so its contents name the last owner rather than a live one.
  #>
  if (-not (Test-Path $script:SandboxLockPath)) { return '' }
  try {
    $s = [System.IO.File]::Open(
      $script:SandboxLockPath,
      [System.IO.FileMode]::Open,
      [System.IO.FileAccess]::Read,
      [System.IO.FileShare]::ReadWrite)
    try { (New-Object System.IO.StreamReader($s)).ReadToEnd().Trim() }
    finally { $s.Dispose() }
  } catch { '' }
}

function Enter-SandboxLock {
  <#
  .SYNOPSIS
    Take the sandbox slot, waiting for whoever has it.
  .PARAMETER Owner
    Free text written into the lock so a waiter can report who is ahead.
  .PARAMETER TimeoutMinutes
    Give up after this long. 0 fails immediately when the lock is taken.
  .OUTPUTS
    The open FileStream. Keep it alive for as long as the sandbox runs.
  #>
  param(
    [string]$Owner = "PID $PID",
    [int]$TimeoutMinutes = 30
  )

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $script:SandboxLockPath) | Out-Null

  $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
  $announced = $false
  while ($true) {
    try {
      $stream = [System.IO.File]::Open(
        $script:SandboxLockPath,
        [System.IO.FileMode]::Create,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::Read)
      $banner = "$Owner`tPID $PID`tsince $((Get-Date).ToString('s'))"
      $writer = New-Object System.IO.StreamWriter($stream)
      $writer.WriteLine($banner)
      $writer.Flush()   # not Dispose: that would close the stream and drop the lock
      return $stream
    } catch [System.IO.IOException] {
      if ((Get-Date) -ge $deadline) {
        throw "Windows Sandbox is held by another runner and did not free up within $TimeoutMinutes minute(s). Holder: $(Get-SandboxLockHolder)"
      }
      if (-not $announced) {
        Write-Host "Waiting for the Windows Sandbox slot. Holder: $(Get-SandboxLockHolder)" -ForegroundColor Yellow
        $announced = $true
      }
      Start-Sleep -Seconds 5
    }
  }
}

function Exit-SandboxLock {
  <#
  .SYNOPSIS
    Release the slot. Safe to call on a stream that is already closed.
  #>
  param([System.IO.FileStream]$Stream)
  if ($Stream) { try { $Stream.Dispose() } catch {} }
}
