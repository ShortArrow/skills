<#
.SYNOPSIS
  Send commands and files to a Windows machine over SSH, without the silent failures.

.DESCRIPTION
  Dot-source this file and call the functions. Every one of them applies the rules the
  skill states: a script is copied as a file and run with -File (never -EncodedCommand),
  the file is written UTF-8 with a BOM, CLIXML progress fragments are dropped from the
  output, a remote path used as a source is converted to forward slashes, and the exit
  code of every ssh and scp call is checked.

  The machine is addressed by IP or host name. Nothing here knows about a hypervisor;
  a Hyper-V caller resolves the address first (Get-HyperVGuestAddress.ps1 in the
  hyperv-persistent-vm skill) and passes it in.

.EXAMPLE
  . "$PSScriptRoot\GuestSsh.ps1"
  $session = New-GuestSession -Address 172.28.10.5 -User User
  Invoke-GuestPowerShell -Session $session -Script 'Get-Date'

.NOTES
  ASCII only, deliberately: a .ps1 holding non-ASCII text is mojibake the moment it is
  read by a Windows PowerShell that assumes ANSI.
#>

Set-StrictMode -Version Latest

<#
.SYNOPSIS
  Describe one machine and the ssh options used to reach it.

.DESCRIPTION
  BatchMode turns a missing key into an error instead of a password prompt nobody will
  answer. UserKnownHostsFile is /dev/null rather than NUL: in the MSYS build of ssh that
  Git for Windows ships, NUL is not the null device and a file of that name appears in
  the working directory.

  StepScript is named after the caller's process id so two runs against one machine do
  not overwrite each other's step file.

.PARAMETER Address
  IP address or host name of the target machine.

.PARAMETER User
  The account to log on as.

.PARAMETER ConnectTimeoutSeconds
  Seconds ssh waits for the TCP connection.
#>
function New-GuestSession {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Address,
        [Parameter(Mandatory)][string]$User,
        [int]$ConnectTimeoutSeconds = 5
    )

    [pscustomobject]@{
        Address    = $Address
        User       = $User
        Target     = "$User@$Address"
        StepScript = "guest-step-$PID.ps1"
        SshOptions = @(
            '-o', 'BatchMode=yes'
            '-o', 'StrictHostKeyChecking=no'
            '-o', 'UserKnownHostsFile=/dev/null'
            '-o', 'LogLevel=ERROR'
            '-o', "ConnectTimeout=$ConnectTimeoutSeconds"
        )
    }
}

<#
.SYNOPSIS
  Drop the CLIXML progress fragments that remote PowerShell writes to stderr.
#>
function Remove-GuestNoise {
    param([object[]]$Output)

    $Output | Where-Object { "$_" -notmatch '^#< CLIXML' -and "$_" -notmatch '^<Objs ' }
}

<#
.SYNOPSIS
  Write a script to a temporary file and copy it to the machine. Returns the remote name.

.DESCRIPTION
  The file is UTF-8 with a BOM. Windows PowerShell 5.1 reads a BOM-less file as ANSI in
  the machine's code page, so a script holding any non-ASCII text is corrupted before it
  runs and fails with a parse error on a line that looks correct in the editor.

  A relative destination lands in the account's home directory, which is the one path
  usable before anything is known about the machine.

  sshd answers "Connection closed" when it cannot set up a session, so a single failure
  is retried rather than ending a long run.

.PARAMETER Session
  A session from New-GuestSession.

.PARAMETER Script
  The script text to send.

.PARAMETER Name
  The remote file name. Defaults to the session's per-process step file.
#>
function Copy-GuestScript {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [Parameter(Mandatory)][string]$Script,
        [string]$Name
    )

    if (-not $Name) { $Name = $Session.StepScript }

    $local = Join-Path ([IO.Path]::GetTempPath()) $Name
    [IO.File]::WriteAllText($local, $Script, (New-Object Text.UTF8Encoding $true))

    $sent = 1
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        & scp @($Session.SshOptions) -q $local "$($Session.Target):$Name"
        $sent = $LASTEXITCODE
        if ($sent -eq 0) { break }
        Start-Sleep -Seconds 2
    }
    Remove-Item $local -Force -ErrorAction SilentlyContinue
    if ($sent -ne 0) { throw "could not send '$Name' to $($Session.Address) (3 attempts, exit=$sent)" }

    return $Name
}

<#
.SYNOPSIS
  Run a script file that is already on the machine and return its output.

.DESCRIPTION
  PowerShell does not stop at a native executable's non-zero exit, and
  $ErrorActionPreference = 'Stop' does not change that, so the exit code is read here.
  Without this the caller continues past a failed step and reports whatever was already
  on disk from the previous run.

.PARAMETER What
  A description used in the error message. The first line of the script is a good one.

.PARAMETER Tolerant
  Return whatever came back instead of throwing. For a polling loop, where one dropped
  connection should not end a long wait and the caller's deadline decides.
#>
function Invoke-GuestScriptFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [Parameter(Mandatory)][string]$Name,
        [string]$What = '',
        [switch]$Tolerant
    )

    $attempts = if ($Tolerant) { 1 } else { 3 }
    $output = @()
    for ($attempt = 1; $attempt -le $attempts; $attempt++) {
        $output = & ssh @($Session.SshOptions) $Session.Target `
            "powershell -NoProfile -ExecutionPolicy Bypass -File $Name" 2>&1
        if ($LASTEXITCODE -eq 0) { break }

        if ($attempt -eq $attempts) {
            if ($Tolerant) { break }
            throw ("the guest failed the step ($attempts attempts, exit=$LASTEXITCODE): $output" +
                   "`n  what it was running: $What")
        }
        Start-Sleep -Seconds 2
    }

    Remove-GuestNoise -Output $output
}

<#
.SYNOPSIS
  Run a script on the machine and return its output.

.DESCRIPTION
  The script is copied and run with -File. It is never passed with -EncodedCommand: an
  encoded command line is opaque in a log and buys nothing a file does not, while a file
  keeps the script readable and debuggable when a step misbehaves.
#>
function Invoke-GuestPowerShell {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [Parameter(Mandatory)][string]$Script,
        [switch]$Tolerant
    )

    $name = Copy-GuestScript -Session $Session -Script $Script
    $what = ($Script -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 1)
    if ($what) { $what = $what.Trim() }

    Invoke-GuestScriptFile -Session $Session -Name $name -What $what -Tolerant:$Tolerant
}

<#
.SYNOPSIS
  Run a script on the machine and return its output as one trimmed string.

.DESCRIPTION
  For the single-value case. Merging stderr into stdout turns lines into ErrorRecord
  objects, so a comparison against a plain string fails unless the result is stringified
  first.
#>
function Get-GuestValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [Parameter(Mandatory)][string]$Script
    )

    $output = Invoke-GuestPowerShell -Session $Session -Script $Script
    "$(($output | Select-Object -Last 1))".Trim()
}

<#
.SYNOPSIS
  Copy a file or directory from here to the machine.

.DESCRIPTION
  A destination containing spaces is quoted differently by each ssh implementation, and
  "C:\Program Files\..." is exactly where runtimes live. Copy into a space-free staging
  directory and move the item inside the machine, where one shell does the parsing.
#>
function Copy-GuestItem {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Destination,
        [switch]$Recurse
    )

    if (-not (Test-Path $Path)) { throw "nothing to copy at '$Path'" }
    if ($Destination -match '\s') {
        throw "remote destination '$Destination' contains a space: stage it somewhere without one and move it on the far end"
    }

    $local = (Resolve-Path $Path).Path.Replace('\', '/')
    $arguments = @($Session.SshOptions) + @('-q')
    if ($Recurse) { $arguments += '-r' }

    & scp @arguments $local "$($Session.Target):$Destination"
    if ($LASTEXITCODE -ne 0) { throw "could not copy '$Path' to $Destination (exit=$LASTEXITCODE)" }
}

<#
.SYNOPSIS
  Collect files from the machine into a local directory.

.DESCRIPTION
  The remote path is converted to forward slashes first. The MSYS build of scp eats a
  backslash in a remote SOURCE path as an escape, so "C:\Users\User\..." collapses to
  "C:UsersUser..." and nothing is fetched; as a destination the same path works, which
  is why sending looks correct and only the collection is empty.
#>
function Receive-GuestItem {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [Parameter(Mandatory)][string]$RemotePath,
        [Parameter(Mandatory)][string]$Destination
    )

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    $remote = $RemotePath -replace '\\', '/'

    & scp @($Session.SshOptions) -r -q "$($Session.Target):$remote" $Destination
    if ($LASTEXITCODE -ne 0) { throw "could not collect '$remote' from $($Session.Address) (exit=$LASTEXITCODE)" }
}

<#
.SYNOPSIS
  Wait until the machine answers an SSH command with the key. Returns $true or $false.

.DESCRIPTION
  A start or a checkpoint restore returns long before the guest is up, so the wait is on
  the service answering rather than on a guessed interval.
#>
function Wait-GuestSsh {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Session,
        [int]$Minutes = 10,
        [int]$PollSeconds = 10
    )

    $deadline = (Get-Date).AddMinutes($Minutes)
    while ((Get-Date) -lt $deadline) {
        & ssh @($Session.SshOptions) $Session.Target 'hostname' 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { return $true }
        Start-Sleep -Seconds $PollSeconds
    }
    return $false
}

<#
.SYNOPSIS
  Delete the per-process step file the session left in the home directory.

.DESCRIPTION
  Sent as a plain command rather than through Invoke-GuestPowerShell: that would copy
  the step file again and then ask the far end to delete the script it is running. This
  one line has nothing to copy, so a plain command is simpler.

  Left undone, every run leaves one more guest-step-<pid>.ps1 in the home directory.
#>
function Remove-GuestSession {
    [CmdletBinding()]
    param([Parameter(Mandatory)][object]$Session)

    $command = "powershell -NoProfile -Command Remove-Item -Path $($Session.StepScript) -Force -ErrorAction SilentlyContinue"
    & ssh @($Session.SshOptions) $Session.Target $command 2>&1 | Out-Null
}
