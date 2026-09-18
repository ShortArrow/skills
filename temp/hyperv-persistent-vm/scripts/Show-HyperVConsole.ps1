<#
.SYNOPSIS
  Open a Hyper-V guest's console in VMConnect, in a basic session.

.DESCRIPTION
  Launched on its own, VMConnect connects with an enhanced session, which is RDP into a
  different session: it asks for credentials although the console is already logged on,
  and the desktop it shows is not the one UI Automation is driving. A test that reports
  a missing window while enhanced session shows it right there is looking at two
  different desktops.

  VMConnect has no per-invocation switch for this, and the per-VM preference is written
  only when a person toggles it in the UI. So the host default is dropped, VMConnect is
  launched, and the default is restored once the connection stands. An established
  connection keeps the basic session afterwards.

  Close the window and reopen it, or reboot the guest and reconnect, and it follows
  whatever the host default is then. This is a measure for the time spent watching, not
  a configuration.

  To capture the screen rather than watch it -- including while nobody is logged on --
  the hyperv-screenshot skill does it from the host with no agent in the guest.

.PARAMETER VMName
  The VM to connect to.

.PARAMETER ConnectSeconds
  How long to wait for the connection to stand before restoring the host default. Raise
  it on a slow host.

.EXAMPLE
  ./Show-HyperVConsole.ps1 -VMName WinDev
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$VMName,
    [int]$ConnectSeconds = 8
)

$ErrorActionPreference = 'Stop'

$vm = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if (-not $vm) { throw "no VM named '$VMName'" }
if ($vm.State -ne 'Running') { throw "VM '$VMName' is $($vm.State), not Running" }

$restoreTo = (Get-VMHost).EnableEnhancedSessionMode

try {
    if ($restoreTo) {
        Set-VMHost -EnableEnhancedSessionMode $false
        Write-Verbose 'enhanced session mode dropped for the moment'
    }

    Start-Process -FilePath "$env:WINDIR\System32\vmconnect.exe" -ArgumentList 'localhost', $VMName
    Start-Sleep -Seconds $ConnectSeconds

    $connected = Get-Process vmconnect -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowTitle -like "*$VMName*" }
    if (-not $connected) { throw 'no VMConnect window appeared' }

    Write-Host "console open: $($connected.MainWindowTitle)" -ForegroundColor Green
}
finally {
    if ($restoreTo) {
        Set-VMHost -EnableEnhancedSessionMode $true
        Write-Verbose 'host default for enhanced session mode restored'
    }
}
