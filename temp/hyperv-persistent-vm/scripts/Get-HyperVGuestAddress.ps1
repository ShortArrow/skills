<#
.SYNOPSIS
  Print a running Hyper-V guest's IPv4 address, as the hypervisor knows it.

.DESCRIPTION
  The Default Switch hands out a new lease across reboots, so an address written into a
  config file or an ssh_config entry is correct until the first restart. Integration
  services already know it, and this depends on neither DNS nor the host's SSH
  configuration -- which is what a fixture should depend on.

  The address is reachable from the host and from nowhere else. That is the right amount
  of exposure for a machine that exists to be experimented on.

  Every call here is checked against Hyper-V's own authorization: the account has to be
  in the local Hyper-V Administrators group, and has to have signed out and in since
  being added, because group membership is written into the logon token.

.PARAMETER VMName
  The VM to ask about.

.EXAMPLE
  $address = ./Get-HyperVGuestAddress.ps1 -VMName WinDev
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$VMName
)

$ErrorActionPreference = 'Stop'

$vm = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if (-not $vm) { throw "no VM named '$VMName'" }
if ($vm.State -ne 'Running') { throw "VM '$VMName' is $($vm.State), not Running" }

$address = (Get-VMNetworkAdapter -VMName $VMName).IPAddresses |
    Where-Object { $_ -match '^\d+\.\d+\.\d+\.\d+$' } |
    Select-Object -First 1

if (-not $address) {
    throw "no IPv4 address for '$VMName'. Are the integration services running in the guest?"
}

$address
