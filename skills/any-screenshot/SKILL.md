---
name: any-screenshot
description: |
  Gate for choosing a screen capture method. Branch here before capturing anything. The right method depends on the target — a web page, an Avalonia window, a running application, a TUI, a whole desktop, or a desktop reached over SSH or RDP — and the wrong choice yields a black or malformed image.
  Most of these failures do not raise. They exit 0 and leave an image with nothing in it, so the point of this skill is to stop you proceeding as though you captured something. The capture itself belongs to windows-screenshot, avalonia-screenshot or flaui-screenshot.
  Triggers: screenshot, screen capture, take a screenshot, check the UI, black screenshot, スクリーンショット, スクショ, 画面を撮って, UI確認, 見た目確認, デザイン確認, 画面が真っ黒
allowed-tools: Read
---

# Any Screenshot

**Choose the method before capturing.** Branch here, then move to the
skill that owns the method.

| Target | Method | Skill |
|---|---|---|
| Web page | Claude in Chrome, else Playwright | MCP browser tools / `page.screenshot()` |
| Avalonia window | Off-screen render | `avalonia-screenshot` |
| Whole window of a running app | PrintWindow, by PID | `windows-screenshot` |
| Single element, or acting first | UI Automation | `flaui-screenshot` |
| Whole desktop | GDI capture | `windows-screenshot` |
| Desktop over SSH or RDP | Scheduled task | `windows-screenshot` |
| TUI application | **Do not capture** | `tui-debug` |

## The property they share

**A failed capture does not raise.** It exits 0 and leaves an image with
nothing in it. Confirming the result is therefore part of taking it.

| Symptom | Cause |
|---|---|
| Black or single colour | No window station — an SSH session, or a disconnected RDP session. Minimized window. DWM-cloaked window. |
| Empty or malformed | Captured before layout finished (Avalonia) |
| Wrong thing in frame | Copied a screen region and caught whatever was in front |

Counting distinct colours is the quickest check. Close to one means the
capture failed.

## Prefer a window over the desktop

Always better when the target can be named: nothing occludes it, the
result does not depend on the desktop resolution, and comparisons between
runs stay stable.

Avalonia does not even need the application running. Win32 windows can be
captured while they stay hidden. Capturing the whole desktop is the last
resort, for when the target cannot be identified.

## PrintWindow against UI Automation

Both capture a running application, and their properties are opposite.

| | `windows-screenshot` | `flaui-screenshot` |
|---|---|---|
| Mechanism | The window draws itself | A screen region is copied |
| Occluded window | Captures fine | Must be brought to the front |
| Granularity | Whole window | Individual element |
| Act, then capture | No | Yes |
| Preparation | None | Needs an AutomationId |

Use the former to photograph something without disturbing it. Use the
latter to press a button first, or to cut out one control.

## Do not capture a TUI

The drawing is already on stdout as ANSI escapes, so redirecting and
reconstructing it is faster and exact. An image would need OCR. Use
`tui-debug`.

## Web

Claude in Chrome is the shortest path where it is available, and
Playwright's `page.screenshot()` where it is not. Neither gets a skill of
its own — the branch ends here, and neither hides a trap.
