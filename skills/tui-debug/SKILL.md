---
name: tui-debug
description: Read what a TUI application is displaying when there is no way to see its terminal — redirect stdout and stderr to files, strip the ANSI escapes, and read the result as plain text. Covers ratatui, textual, curses, blessed and similar. Use to smoke-test a TUI on the user's behalf, to check layout, colour or values, or to verify a release against the previous one.
---

# TUI Debug

An agent cannot screenshot a Windows console or a Linux TTY. It does not
need to: a TUI writes cursor positions, text and colour to stdout as ANSI
escapes, so **redirecting stdout reconstructs the screen after the fact**.

This is how to start such an application and turn its display into
something readable.

## When to use it

- Confirming a TUI starts, on the user's behalf
- Checking layout, colour or displayed values automatically
- Comparing a release against the previous one
- Reproducing a reported state to inspect it

## When not to

- **Genuine interaction** — verifying a sequence of state transitions
  driven by keystrokes needs stdin too. Use expect or pty automation.
- **Applications that write to the screen buffer directly** — curses code
  using `addstr` plus `refresh` may draw nothing through a redirect. Most
  frameworks (ratatui, textual, Charm) write to stdout and are fine; some
  native implementations require a raw tty.
- **Full-screen applications built around mouse events.**

## PowerShell

```powershell
# 1. Start with stdout/stderr redirected, window hidden
Push-Location <project>
$proc = Start-Process -FilePath <tui_app.exe> `
    -ArgumentList <args> `
    -RedirectStandardOutput "$env:TEMP\tui_out.log" `
    -RedirectStandardError  "$env:TEMP\tui_err.log" `
    -PassThru -WindowStyle Hidden
Pop-Location

# 2. Let it draw — usually 2 to 5 seconds
Start-Sleep -Seconds 4
Write-Host "[viewer] pid=$($proc.Id) HasExited=$($proc.HasExited)"

# 3. Strip the escapes and read
$raw = Get-Content "$env:TEMP\tui_out.log" -Raw
#   `e[<n>;<m>H            cursor position (row, column)
#   `e[<params>m           SGR — colour and style
#   `e[?<n>h / `e[?<n>l    DECSET — mode changes such as alternate screen
$clean = $raw -replace "`e\[[0-9;]*[a-zA-Z]", ""
$clean = $clean -replace "`e\[\?[0-9]+[a-zA-Z]", ""
$clean -split "`n" | Select-Object -Last 60

# 4. Clean up
Stop-Process -Id $proc.Id -Force
```

`-WindowStyle Hidden` keeps a console from appearing while the user is
working. Some TUIs will not start their draw thread when hidden — if
stdout comes back empty, try `-NoNewWindow` or `-WindowStyle Normal`.

## bash, Linux, WSL

```bash
# 1. Start, redirected
nohup <tui_app> <args> > /tmp/tui_out.log 2> /tmp/tui_err.log < /dev/null &
PID=$!

# 2. Wait
sleep 4

# 3. Strip and read
sed -E 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\[\?[0-9]+[a-zA-Z]//g' /tmp/tui_out.log | tail -60

# 4. Clean up
kill $PID
```

## Stripping the escapes

| Form | Example | Purpose | Regex (PCRE) |
|---|---|---|---|
| CSI + SGR | `\e[38;5;3;49m` | Colour, including 256-colour | `\e\[[0-9;]*m` |
| CSI + cursor | `\e[5;10H` | Cursor position | `\e\[[0-9;]*H` |
| CSI + clear | `\e[2J` | Clear screen | `\e\[[0-9;]*J` |
| DECSET | `\e[?1049h` | Alternate screen | `\e\[\?[0-9]+[a-zA-Z]` |
| OSC | `\e]0;title\a` | Window title | `\e\][0-9;]*[a-zA-Z]*\a` |

One expression covering nearly everything:

```regex
\e\[[0-9;?]*[a-zA-Z]
```

Or, to remove ANSI entirely:

```regex
\x1b(\[[0-9;?]*[a-zA-Z]|\][0-9;]*\x07)
```

## Things that will catch you out

**The capture is a stream of updates, not a screen.** Some applications
redraw everything each frame; others move the cursor back with `\e[H`, or
address a cell with `\e[r;cH`, and overwrite. With the latter, **later
output is closer to the current screen** — `tail -60` shows the final
state.

**ratatui and friends use the alternate screen buffer.** `\e[?1049h` on
start, `\e[?1049l` on exit, both captured. Reading the log after the
process has exited can therefore look as though nothing was drawn.
**Read while the process is alive.**

**Wide characters shift the columns.** Japanese and other two-cell
characters break grid alignment in the stripped text. Values are still
readable; the box drawing will not line up.

**Check the process is still running.** `HasExited` tells you. If it died
immediately, a configuration error is waiting in stderr — always look:

```powershell
Get-Content "$env:TEMP\tui_err.log" | Select-Object -Last 30
```

**Separate the application's own logging.** `tracing` and `log` normally
write to stderr, which the redirect above captures too. Where log lines
are interleaved with the drawing they survive the ANSI stripping, so grep
them out by prefix when they get in the way.

## What a captured ratatui screen looks like

```
┌Tabs───────────────────────────────────────────────────┐
│ Tab A │ Tab B │ All │
└─────────────────────────────────────────────────────────┘
┌ stream_out [SEND] ─────────────────┐┌ stream_in [RECV] fr:21 [0/41] ───┐
│ Waiting for data...                ││ Row Name       B  HEX   Value    │
│                                    ││  1  field_0    1  7E    126      │
│                                    ││  2  field_1    2  01 00 1        │
│                                    ││  3  field_2    2  3C 00 60       │
...
```

The borders are ragged, but Name, HEX and Value extract as text — enough
to decide whether frames are arriving and whether a field is in range.

## Related

- **Full automation including keystrokes** — expect or pty automation.
  Out of scope here.
- **Screenshots of a GUI application** — choose the method with
  `any-screenshot`; the capture belongs to `windows-screenshot` or
  `avalonia-screenshot`. Those failures exit 0 and leave an empty image,
  so a wrong choice goes unnoticed.
- **Reading the TUI's internal state directly** — over IPC, by adding a
  JSON dump endpoint. Often the easier path.
