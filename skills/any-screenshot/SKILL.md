---
name: any-screenshot
description: |
  Choose a capture method before capturing anything. The right one depends on the target — web page, Avalonia window, running app, TUI, desktop, or a desktop over SSH/RDP — and a wrong choice returns a black or malformed image without raising. Start here whenever a screenshot is wanted and the method is not already settled; the capture itself belongs to windows-screenshot, avalonia-screenshot or flaui-screenshot.
allowed-tools: Read
---

# Any Screenshot

**Choose the method before capturing.** Branch here, then move to the
skill that owns the method.

| Target | Method | Skill |
|---|---|---|
| Web page | Host browser control, else Playwright | Claude in Chrome, Codex browser skill, Copilot in VS Code `#browser` (`screenshotPage`), Cursor Browser tool, Gemini CLI `browser_agent`, MCP browser tools, or `page.screenshot()` |
| Avalonia window | Off-screen render | `avalonia-screenshot` |
| Whole window of a running app | PrintWindow, by PID | `windows-screenshot` |
| Single element, or acting first | UI Automation | `flaui-screenshot` |
| Whole desktop | GDI capture | `windows-screenshot` |
| Desktop over SSH or RDP | Scheduled task | `windows-screenshot` |
| Guest of a running Hyper-V VM | WMI thumbnail | `hyperv-screenshot` |
| TUI application | **Do not capture** | `tui-debug` |

## The property they share

**A failed capture does not raise.** It exits 0 and leaves an image with
nothing in it. Confirming the result is therefore part of taking it.

| Symptom | Cause |
|---|---|
| Black or single colour | No window station — an SSH session, or a disconnected RDP session. Minimized window. DWM-cloaked window. A Hyper-V guest whose display has slept. |
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

Use the browser controller provided by the host.

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code; a structured tool
interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`, a permission prompt with a "rest of the session" option and
`--allow-all` mean Copilot CLI; an "Ask questions" tool, a Task tool and a
Browser tool mean Cursor; `ask_user`, `read_file` and subagents exposed as
tools of their own name mean Gemini CLI. A host that matches none of these
takes the last row.

| Host | Browser controller |
|---|---|
| Claude Code | Claude in Chrome |
| Codex | The Codex browser skill |
| Copilot in VS Code | The `#browser` tool set: `openBrowserPage`, `navigatePage`, `readPage`, `screenshotPage`, `clickElement`, `typeInPage`, `runPlaywrightCode` |
| Copilot CLI | No built-in browser tool. Add Playwright as an MCP server (`npx @playwright/mcp@latest`) |
| Cursor | The Browser tool: Navigate, Click, Type, Scroll, Screenshot, Console Output, Network Traffic, with no setup |
| Gemini CLI | The `browser_agent` subagent, which bundles chrome-devtools-mcp, is off by default, needs Chrome 144+ and shows a consent dialog on first use |
| Any other host | Playwright's `page.screenshot()`. Where nothing can drive a browser, say so and stop. Never describe a page as though it had been captured, and never fall back to another host's browser skill. |

The branch ends here; do not invoke a Windows desktop capture for browser
content.
