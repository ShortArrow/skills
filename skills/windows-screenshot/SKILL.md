---
name: windows-screenshot
description: |
  Capture a Windows desktop or window from PowerShell — by PID, whole screen, or over SSH/RDP. A session with no window station returns a black PNG with exit code 0; minimized and DWM-cloaked windows capture as blank and are refused by default.
  Triggers: Windows screenshot, capture the desktop, capture a window by PID, see the screen remotely, デスクトップを撮って, PIDのウィンドウを撮って, リモートで画面を見たい, 画面が真っ黒
allowed-tools: Bash, Read
---

# Windows Screenshot

`any-screenshot` decides which method applies. This is the native Windows
capture itself.

| Purpose | Script |
|---|---|
| A process's windows, by PID | `scripts/Save-WindowScreenshot.ps1` |
| Whole screen, inside an interactive session | `scripts/Save-Screenshot.ps1` |
| Whole screen, over SSH or RDP | `scripts/Invoke-ScreenshotViaTask.ps1` |

Each prints the saved path on stdout, so it can be handed straight to
`Read`.

## By PID is the default choice

```pwsh
./scripts/Save-WindowScreenshot.ps1 -ProcessId 11268 -List
./scripts/Save-WindowScreenshot.ps1 -ProcessId 11268 -TitleMatch 'dotfiles' -Path C:/temp/w.png
```

`PrintWindow` with `PW_RENDERFULLCONTENT` asks the window to draw itself.
Against copying a screen region, that gives:

- **Occluded windows still capture.** No need to raise anything, so the
  desktop is left as it was
- **GPU-composited windows do not come back black.** A plain `BitBlt`
  fails on them
- **No dependence on resolution.** The image is the window's own size, so
  comparisons between runs stay stable

A process may own several windows — wezterm routinely does — and all of
them are enumerated. Check with `-List`, narrow with `-TitleMatch`.

Bounds come from `DWMWA_EXTENDED_FRAME_BOUNDS`, not `GetWindowRect`.
Since Windows 10 the latter includes an invisible resize border, which
would add a transparent margin to every capture.

## Three states that capture nothing

**None of them raises.** That is the subject of this skill.

| State | What happens | Response |
|---|---|---|
| SSH / disconnected RDP | No window station; `CopyFromScreen` returns a black PNG with exit code 0 | `Invoke-ScreenshotViaTask.ps1` |
| Minimized | No surface to draw | Refused by default; `-IncludeEmpty` overrides |
| DWM-cloaked | A live window the shell is hiding: a suspended UWP app, or one a tiling manager holds on an unviewed workspace | As above |

Cloaking misleads the most. The window enumerates normally and reports a
real size, yet capturing it yields a single colour — forcing one here
produced exactly one distinct colour.

## Over SSH or RDP

```pwsh
./scripts/Invoke-ScreenshotViaTask.ps1 -Path C:/temp/remote.png
```

Registers a one-shot scheduled task that runs as the interactive user, so
the capture happens inside the desktop session while the caller stays
headless. The task is removed afterwards.

This assumes the target user is logged on with a live desktop. A machine
that is signed out has nothing to capture.

## Provenance

`scripts/` comes from the author's private `Get-ScreenShot` repository.
Changed on import:

- The destination is a `-Path` parameter and the resolved path goes to
  stdout. A caller that cannot read the file back cannot automate anything
- The fixed three-second wait became polling for the file, up to 30
  seconds. Deleting the task on a timer could remove it mid-capture
- Task names carry a GUID fragment so concurrent runs do not collide
- `Save-WindowScreenshot.ps1` is new
