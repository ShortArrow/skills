---
name: hyperv-screenshot
description: |
  Capture the screen of a running Hyper-V guest from the host, without RDP, without an agent inside, and without the guest being logged in. The WMI thumbnail API returns raw RGB565 that has to be assembled by hand, and it returns four bytes more than the arithmetic says. A guest whose display has slept returns a black frame that looks identical to a failed capture — wake it with a synthetic keypress first. Use when a headless VM must be inspected and SSH or PowerShell Direct only shows you text.
allowed-tools: PowerShell, Read, Write
---

# Hyper-V guest screenshot

**The host can photograph the guest's framebuffer directly.** No RDP
session, no agent in the guest, no user logged in. The VM only has to be
running.

This matters when a log says nothing. An installer that hangs writes
"started" and then stops; the reason is a modal dialog nobody can see.
Text channels — SSH, PowerShell Direct, `Get-Process` — will not show it,
because a dialog is not a process and often not even a window with a
title.

## The call

`Msvm_VirtualSystemManagementService.GetVirtualSystemThumbnailImage`
returns a byte array of 16bpp RGB565. There is no PNG, no bitmap header,
no stride — the assembly is yours.

```powershell
$ns = 'root\virtualization\v2'
$vm = Get-CimInstance -Namespace $ns -ClassName Msvm_ComputerSystem -Filter "ElementName='NAME'"
$head = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_VideoHead | Select-Object -First 1
$w = [int]$head.CurrentHorizontalResolution
$h = [int]$head.CurrentVerticalResolution

$mgmt = Get-CimInstance -Namespace $ns -ClassName Msvm_VirtualSystemManagementService
$res = Invoke-CimMethod -InputObject $mgmt -MethodName GetVirtualSystemThumbnailImage -Arguments @{
  TargetSystem = $vm            # the instance, NOT [ref]$vm
  WidthPixels  = [uint16]$w
  HeightPixels = [uint16]$h
}
```

Ask `Msvm_VideoHead` for the size rather than passing one. A guessed size
is honoured — the API scales — and a scaled thumbnail is worthless for
reading a dialog.

## Copy row by row

`Bitmap.LockBits` gives a stride padded to a 4-byte boundary. At 1024
wide, `1024 * 2 = 2048` is already aligned and a single `Marshal.Copy`
appears to work; at 1000 wide it is not, and the image shears. Copying
per row costs nothing and is right at every width.

```powershell
$bmp  = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format16bppRgb565)
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::WriteOnly, $bmp.PixelFormat)
try {
  $srcStride = $w * 2
  for ($y = 0; $y -lt $h; $y++) {
    [System.Runtime.InteropServices.Marshal]::Copy(
      [byte[]]$res.ImageData, $y * $srcStride,
      [IntPtr]::Add($data.Scan0, $y * $data.Stride), $srcStride)
  }
} finally { $bmp.UnlockBits($data) }
$bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
```

## Wake the display first

A guest left alone blanks its screen, and the thumbnail then comes back
uniformly black — indistinguishable from the failure modes in
`any-screenshot`. Press and release a harmless key through the synthetic
keyboard, wait a moment, then capture.

```powershell
$kbd = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_Keyboard
Invoke-CimMethod -InputObject $kbd -MethodName PressKey   -Arguments @{ keyCode = [uint32]0x10 }  # Shift
Start-Sleep -Milliseconds 300
Invoke-CimMethod -InputObject $kbd -MethodName ReleaseKey -Arguments @{ keyCode = [uint32]0x10 }
Start-Sleep -Seconds 3
```

Shift is the safe choice: it wakes the session and types nothing. Do not
use Enter or Space — either one dismisses the dialog you came to read.

## Facts that bite

| | |
|---|---|
| **`ImageData` is longer than `w * h * 2`** | Four bytes longer, consistently. Copy per row for `h` rows and ignore the tail; a whole-buffer copy sized from `.Length` overruns the bitmap and takes down the CLR with `0x80131506` |
| **`TargetSystem` takes the instance, not `[ref]`** | `[ref]$vm` fails the cast to `InstanceHandle`. This is the opposite of the WMI-era examples still in circulation |
| **`Get-WmiObject` breaks under `sudo`** | The object comes back deserialized and `GetVirtualSystemThumbnailImage` is not on it. `Get-CimInstance` + `Invoke-CimMethod` survives the boundary |
| **Access is checked by Hyper-V, not UAC** | `root\virtualization\v2` refuses a caller that is neither elevated nor in the local `Hyper-V Administrators` group. Join the group once (`Add-LocalGroupMember`, elevated) and **sign out and back in** — the token is cut at logon, so the same session keeps being refused. Until then, under `sudo` on Windows, pass a script file — an inline `-c` with a large here-string is where quoting dies |
| **Black is ambiguous** | Slept display, or a guest that has genuinely painted black. Wake it and capture twice before believing the second one |
| **The thumbnail is the console, not a session** | What an RDP user sees is a different desktop. A dialog on the console is invisible over RDP and vice versa |

## Where this sits

`any-screenshot` branches by target and sends **guest of a running
Hyper-V VM** here. The host-side alternatives it lists all need the
target on the host's own desktop, which a guest never is.

For a guest you can log into, RDP plus `windows-screenshot` inside gives
a sharper image with real window handles. The thumbnail wins when there
is no session at all — an unattended install, a boot-time failure, a VM
still at the logon screen.
