<#
.SYNOPSIS
  Run one command inside Windows Sandbox and bring the result back, without
  disturbing the desktop or another project's sandbox.

.DESCRIPTION
  The sandbox has its own active input desktop, which is why UI tests belong
  in it: SendInput reaches the guest application and never touches the host
  keyboard, mouse or foreground window.

  There is one instance per machine, so the whole run -- pre-flight, launch,
  wait, clean-up -- is held under the lock in SandboxLock.ps1. Runners that
  skip the lock kill each other: each one ends by terminating "the" sandbox
  processes, which are somebody else's.

  Fixed contract with the guest:

    C:\out            the -ResultFolder, read-write. Everything comes back
                      through it: run.log, exitcode.txt, done.marker
    C:\out\_run.cmd   generated wrapper. Runs -Command, records the exit
                      code, writes the marker, then shuts the guest down

  Nothing is installed in the guest, so -Command must run against what the
  sandbox already has plus what -Map brings in. Build on the host and map
  the output; a compiler inside the guest is a download away.

.PARAMETER Command
  The command line cmd.exe runs in the guest. One line.

.PARAMETER ResultFolder
  Host folder mapped to C:\out. Created if absent. Stale markers are
  removed before the run.

.PARAMETER Map
  Extra folders, as hashtables with Host, Sandbox, and optional ReadOnly.
  A host folder that does not exist stops the container from starting at
  all, so paths are resolved before launch.

  ReadOnly defaults to $true here, the opposite of the .wsb schema. A
  writable mapping is the one hole in "nothing survives the sandbox": the
  guest writes straight onto the host disk. Ask for it deliberately.

.PARAMETER MemoryInMB
  Guest memory. The .wsb default is 4096 and anything under 2048 is
  silently raised.

.PARAMETER GuestWorkingDirectory
  Guest path to cd into before -Command. Defaults to C:\out.

.PARAMETER TimeoutMinutes
  How long to wait for done.marker before giving up and cleaning up.

.PARAMETER LockWaitMinutes
  How long to queue behind another runner. 0 fails immediately.

.PARAMETER ShowWindow
  Leave the sandbox window in front. By default it is force-minimized and
  the foreground is handed back, so stray keystrokes are not swallowed.

.PARAMETER KeepSandbox
  Skip the guest shutdown and the host-side kill, to inspect a failed run.
  The slot stays occupied until the sandbox is closed by hand.

.OUTPUTS
  The guest exit code. run.log is echoed to the host console.

.EXAMPLE
  ./Invoke-SandboxRun.ps1 -ResultFolder ./artifacts/uitests `
    -Map @{Host="$PWD"; Sandbox='C:\repo'; ReadOnly=$false},
         @{Host=(Split-Path (Get-Command dotnet).Source); Sandbox='C:\Program Files\dotnet'} `
    -GuestWorkingDirectory 'C:\repo' `
    -Command 'set "DOTNET_ROOT=C:\Program Files\dotnet" && set "PATH=C:\Program Files\dotnet;%PATH%" && dotnet test tests\Ui.Tests\Ui.Tests.csproj --no-build --no-restore'
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$Command,
  [Parameter(Mandatory)][string]$ResultFolder,
  [hashtable[]]$Map = @(),
  [string]$GuestWorkingDirectory = 'C:\out',
  [int]$TimeoutMinutes = 20,
  [int]$LockWaitMinutes = 30,
  [int]$MemoryInMB = 8192,
  [ValidateSet('Default', 'Disable')][string]$Networking = 'Default',
  [string]$Owner = '',
  [switch]$ShowWindow,
  [switch]$KeepSandbox
)
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/SandboxLock.ps1"

$sandboxExe = "$env:windir\System32\WindowsSandbox.exe"
if (-not (Test-Path $sandboxExe)) {
  throw "WindowsSandbox.exe is missing. Enable the Windows Sandbox feature: Enable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM (needs elevation and a reboot)."
}

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class SbxWin {
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@ -ErrorAction SilentlyContinue

# vmmemCmZygote is the pre-warmed base image, not a running sandbox, and
# killing it costs the next launch its fast start. vmmemWindowsSandbox is a
# real one, but it is a VM worker: it answers to wsb stop, not Stop-Process.
$sandboxProcessNames = 'WindowsSandbox', 'WindowsSandboxClient', 'WindowsSandboxServer',
                       'WindowsSandboxRemoteSession', 'ManagedWindowsVM', 'vmmemWindowsSandbox'
$killableProcessNames = $sandboxProcessNames | Where-Object { $_ -notlike 'vmmem*' }

$wsbCli = Get-Command wsb -CommandType Application -ErrorAction SilentlyContinue

# The only reliable liveness check. A sandbox whose window has gone still
# holds the slot, and shows up here with no WindowsSandboxClient process.
function Get-SandboxEnvironmentIds {
  if (-not $wsbCli) { return @() }
  try {
    $raw = & $wsbCli.Source list --raw 2>$null | Out-String
    if (-not $raw.Trim()) { return @() }
    @(($raw | ConvertFrom-Json).WindowsSandboxEnvironments | ForEach-Object { $_.Id })
  } catch { @() }
}

function Get-SandboxPids {
  @(Get-Process -Name $sandboxProcessNames -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty Id)
}

function Test-SandboxRunning {
  if ($wsbCli) { return (Get-SandboxEnvironmentIds).Count -gt 0 }
  return (Get-SandboxPids).Count -gt 0
}

# SW_FORCEMINIMIZE (11) minimizes even a window that is not pumping messages,
# and does not activate the next window in the z-order.
#
# The window belongs to WindowsSandboxClient on the inbox sandbox and to
# WindowsSandboxRemoteSession on the Store one (wsb.exe, 0.8.x), so both are
# searched rather than assuming a version.
function Hide-SandboxWindow {
  $win = Get-Process -Name WindowsSandboxClient, WindowsSandboxRemoteSession -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
  if (-not $win) { return $false }
  [void][SbxWin]::ShowWindowAsync($win.MainWindowHandle, 11)
  return $true
}

$resultDir = (New-Item -ItemType Directory -Force -Path $ResultFolder).FullName
'done.marker', 'run.log', 'exitcode.txt', '_run.cmd', '_command.cmd' | ForEach-Object {
  Remove-Item (Join-Path $resultDir $_) -ErrorAction SilentlyContinue
}

# cmd.exe rejects a script with bare LF line endings, so both scripts are
# written with explicit CRLF and no characters outside ASCII.
function Write-GuestScript([string]$Name, [string[]]$Lines) {
  [System.IO.File]::WriteAllText(
    (Join-Path $resultDir $Name),
    (($Lines -join "`r`n") + "`r`n"),
    [System.Text.Encoding]::ASCII)
}

# -Command goes in a file of its own so the redirection can wrap all of it.
# Written inline, `a && b > log` would redirect b alone and drop a's output.
Write-GuestScript '_command.cmd' @('@echo off', $Command)

$wrapperLines = @(
  '@echo off'
  'setlocal'
  "cd /d $GuestWorkingDirectory"
  'call C:\out\_command.cmd > C:\out\run.log 2>&1'
  'set "RC=%ERRORLEVEL%"'
  '>C:\out\exitcode.txt echo %RC%'
  '>C:\out\done.marker echo done'
)
if (-not $KeepSandbox) { $wrapperLines += 'shutdown /s /t 3 /f' }
Write-GuestScript '_run.cmd' $wrapperLines

$folders = @(@{ Host = $resultDir; Sandbox = 'C:\out'; ReadOnly = $false }) + $Map
$mappedXml = foreach ($m in $folders) {
  $hostPath = (Resolve-Path -LiteralPath $m.Host).ProviderPath
  $readOnly = if ($null -eq $m.ReadOnly) { $true } else { [bool]$m.ReadOnly }
  @"
    <MappedFolder>
      <HostFolder>$([System.Security.SecurityElement]::Escape($hostPath))</HostFolder>
      <SandboxFolder>$([System.Security.SecurityElement]::Escape($m.Sandbox))</SandboxFolder>
      <ReadOnly>$($readOnly.ToString().ToLower())</ReadOnly>
    </MappedFolder>
"@
}

# Absolute host paths differ per machine, so the .wsb is generated per run
# and never committed.
$wsb = Join-Path $env:TEMP ("sbxrun-" + [Guid]::NewGuid().ToString('N').Substring(0, 8) + ".wsb")
@"
<Configuration>
  <MappedFolders>
$($mappedXml -join '')  </MappedFolders>
  <LogonCommand>
    <Command>cmd.exe /c C:\out\_run.cmd</Command>
  </LogonCommand>
  <!-- vGPU stays enabled. Disabling it stops the automatic logon from
       completing, and LogonCommand never runs. -->
  <Networking>$Networking</Networking>
  <MemoryInMB>$MemoryInMB</MemoryInMB>
</Configuration>
"@ | Set-Content -LiteralPath $wsb -Encoding UTF8

if (-not $Owner) { $Owner = Split-Path -Leaf (Get-Location).Path }
$lock = Enter-SandboxLock -Owner $Owner -TimeoutMinutes $LockWaitMinutes

$exit = 1
$launched = $false
try {
  # Under the lock, a live sandbox belongs to someone outside this protocol
  # -- a hand-started one, or a -KeepSandbox run left open. Refuse rather
  # than take the machine's only slot away from them.
  if (Test-SandboxRunning) {
    $who = if ($wsbCli) { "environment $((Get-SandboxEnvironmentIds) -join ', ')" }
           else { "PID $((Get-SandboxPids) -join ', ')" }
    throw "A Windows Sandbox is already running outside this runner ($who). It was not started here, so it will not be terminated. Close it -- wsb stop --id <id> -- and try again."
  }
  $priorIds = Get-SandboxEnvironmentIds

  $savedForeground = [SbxWin]::GetForegroundWindow()
  Write-Host "Starting Windows Sandbox..." -ForegroundColor Cyan
  $style = if ($ShowWindow) { 'Normal' } else { 'Minimized' }
  Start-Process -FilePath $sandboxExe -ArgumentList $wsb -WindowStyle $style
  $launched = $true

  if (-not $ShowWindow) {
    $hidden = $false
    for ($i = 0; $i -lt 60 -and -not $hidden; $i++) {
      $hidden = Hide-SandboxWindow
      if (-not $hidden) { Start-Sleep -Milliseconds 500 }
    }
    # SetForegroundWindow obeys the foreground lock, so this is best effort;
    # the forced minimize is what actually keeps the desktop usable.
    if ($hidden -and $savedForeground -ne [IntPtr]::Zero) {
      [void][SbxWin]::SetForegroundWindow($savedForeground)
    }
  }

  $marker = Join-Path $resultDir 'done.marker'
  $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
  Write-Host "Waiting for the guest to finish (up to $TimeoutMinutes minutes)..."
  while (-not (Test-Path $marker)) {
    if ((Get-Date) -gt $deadline) {
      throw "Timed out: the guest did not write done.marker within $TimeoutMinutes minutes."
    }
    if (-not $ShowWindow -and (Hide-SandboxWindow) -and $savedForeground -ne [IntPtr]::Zero) {
      [void][SbxWin]::SetForegroundWindow($savedForeground)
    }
    Start-Sleep -Seconds 3
  }

  Start-Sleep -Seconds 1  # let the last of the redirected output land
  $log = Join-Path $resultDir 'run.log'
  if (Test-Path $log) { Get-Content -LiteralPath $log }
  $codeFile = Join-Path $resultDir 'exitcode.txt'
  if (Test-Path $codeFile) {
    $raw = (Get-Content -LiteralPath $codeFile -Raw).Trim()
    if ($raw -match '^\d+$') { $exit = [int]$raw }
  }
}
finally {
  if ($KeepSandbox -and $launched) {
    Write-Host "-KeepSandbox: the sandbox is still running and holds the machine's only slot until it is closed." -ForegroundColor Yellow
  } elseif ($launched) {
    # Everything alive now was started here: the check above ran under the
    # lock and found nothing. A guest that could not shut itself down leaves
    # a VM worker and a RemoteSession behind, several hundred MB to several
    # GB, and they keep holding the machine's only slot.
    foreach ($id in (Get-SandboxEnvironmentIds | Where-Object { $_ -notin $priorIds })) {
      try { & $wsbCli.Source stop --id $id 2>&1 | Out-Null } catch {}
    }
    foreach ($proc in Get-Process -Name $killableProcessNames -ErrorAction SilentlyContinue) {
      try { Stop-Process -Id $proc.Id -Force -ErrorAction Stop } catch {}
    }
  }
  Remove-Item -LiteralPath $wsb -ErrorAction SilentlyContinue
  Exit-SandboxLock $lock
}

exit $exit
