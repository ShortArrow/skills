---
name: timed-wait
description: |
  Putting a clock and a deadline on every long wait — a VM boot, a build, a poll loop watching for a state change, a background command that ends with a notification. A wait without a clock cannot distinguish slow from stuck, and a wait without a deadline cannot end any way except success. Before waiting: write down the expected duration, a poll cadence matched to how fast the state actually changes, and the deadline where waiting stops being the plan; record the start timestamp before launching; report elapsed with every status line. On deadline breach, stop waiting and read the liveness signal — a monotone observable chosen before the wait began — instead of extending the timeout. Use when launching a command expected to run for minutes, when polling until a condition holds, when a wait has no stated end, and when "still running" is about to be reported without a number.
allowed-tools: Bash, PowerShell, Read
---

# The Clock on the Wait

A wait without a clock cannot tell slow from stuck: both look like
silence, and the reader of "still waiting" learns nothing either way. A
wait without a deadline is worse — it has no way to end except
success, so a hung process is waited on forever, politely.

Three numbers, written down before the wait starts:

1. **Expected duration.** From a previous run, a log, a document. When
   nothing supplies it, this run is the measurement — record it, and
   the next wait has its number.
2. **Poll cadence**, matched to how fast the state actually changes.
   An eight-minute boot deserves a check every minute or two, not
   every five seconds; polling faster than the state moves spends
   attention to learn nothing.
3. **The deadline** — the elapsed time at which waiting stops being
   the plan. Two or three times the expected duration is a reasonable
   default. Breach does not mean "wait more"; it means the question
   has changed from "is it done" to "is it alive".

## Start the clock before the launch

The start timestamp is part of the evidence, and it cannot be
reconstructed afterwards:

```bash
start=$(date +%s)
# ... launch ...
echo "$(( $(date +%s) - start ))s elapsed"
```

```powershell
$sw = [System.Diagnostics.Stopwatch]::StartNew()
# ... launch ...
"{0:mm\:ss} elapsed" -f $sw.Elapsed
```

Every status line carries elapsed against expected — "4m10s of ~8m" —
so the reader, including the one writing it, sees drift the moment it
starts rather than at the deadline. A duration reported afterwards
names both timestamps; a number without its method does not survive
the report.

## Pick the liveness signal before waiting

Done is one observable; alive is a different one, chosen in advance:
log bytes growing, files appearing, CPU consumed, a port opening. A
spinner is not progress, and a quiet process is not necessarily hung —
the distinction needs a **monotone** signal read at each poll. Slow is
"the signal still moves"; stuck is "the signal has not moved for
several polls". Deciding this after the deadline breach means staring
at a silent process with no way to classify it.

## On breach, diagnose — do not extend

A breached deadline with a moving liveness signal is a wrong estimate:
note the real duration, keep waiting against a revised number. A
breached deadline with a flat signal is a hang: stop waiting and
investigate, because more time changes nothing. Extending the timeout
without reading the signal treats both cases as the first, and
killing on breach without reading it treats both as the second — each
error deletes the watchdog's value in one direction.

## Host mechanics

| Host | Route |
|---|---|
| Claude Code | Launch long commands with `run_in_background` — completion arrives as a notification, so never poll for it. A foreground shell call is capped at ten minutes; raising the timeout is not the tool for a twenty-minute boot. For external state the host cannot see, run the check command at the chosen cadence; foreground sleep loops burn turns to learn nothing |
| Codex | Use the host's background execution and wait/status facilities; prefer a compact status snapshot per poll |
| Plain shell, CI | `timeout <deadline> cmd` is the hard watchdog; `nohup cmd > run.log` plus the log's growth is launch and liveness in two files; `date +%s` arithmetic or `SECONDS` carries the clock |

## When not to apply

A command with a known sub-minute duration needs no watchdog — a clock
on a two-second command is ceremony. The skill starts paying at the
first wait long enough to wonder about, and at every poll loop whose
end condition might never arrive.
