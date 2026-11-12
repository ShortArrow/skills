---
name: timed-wait
description: |
  A clock and a deadline on every long wait: a VM boot, a build, a poll loop, a background command ending in a notice.
  A wait without a clock cannot tell slow from stuck, and one without a deadline can only end in success. Before waiting, write down the expected duration, a poll cadence, and the deadline where waiting stops being the plan; report elapsed with every status line. On breach, read the liveness signal chosen before the wait began rather than extending the timeout. A wait for human input is a third class, blocked-on-input: no liveness signal exists, so the deadline is a wall-clock time with a fallback declared up front. A peer message is a fourth: nothing returns from beyond this machine, so it is a notice posted, not a question asked. Use when launching a command expected to run for minutes, when polling until a condition holds, when handing back an approval that gates a deploy, when messaging a peer session, and when "still running" is about to be reported without a number.
allowed-tools: Bash, PowerShell, Read
---

# The Clock on the Wait

A wait without a clock cannot tell slow from stuck:
both look like silence,
and the reader of "still waiting" learns nothing either way.
A wait without a deadline is worse — it has no way to end except success,
so a hung process is waited on forever, politely.

Three numbers, written down before the wait starts:

1. **Expected duration.** From a previous run, a log, a document.
   When nothing supplies it, this run is the measurement — record it,
   and the next wait has its number.
2. **Poll cadence**, matched to how fast the state actually changes.
   An eight-minute boot deserves a check every minute or two,
   not every five seconds;
   polling faster than the state moves spends attention to learn nothing.
3. **The deadline** — the elapsed time at which waiting stops being the plan.
   Two or three times the expected duration is a reasonable default.
   Breach does not mean "wait more";
   it means the question has changed from "is it done" to "is it alive".

## Start the clock before the launch

The start timestamp is part of the evidence,
and it cannot be reconstructed afterwards:

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

Every status line carries elapsed against expected — "4m10s of ~8m" — so the reader,
including the one writing it,
sees drift the moment it starts rather than at the deadline.
A duration reported afterwards names both timestamps;
a number without its method does not survive the report.

## Pick the liveness signal before waiting

Done is one observable; alive is a different one, chosen in advance:
log bytes growing, files appearing, CPU consumed, a port opening.
A spinner is not progress,
and a quiet process is not necessarily hung — the distinction needs a **monotone** signal read at each poll.
Slow is "the signal still moves";
stuck is "the signal has not moved for several polls".
Deciding this after the deadline breach means staring at a silent process with no way to classify it.

A watcher ending is a third thing again, and the one most often misread.
A notification arriving says the watcher stopped,
not that the job succeeded: `completed`,
`failed` and `killed` all arrive the same way,
and a watcher killed at minute nine of a twenty-minute build observed nothing at all.
So the status and the exit code are read before anything is reported,
and `gh run watch <id> --exit-status` is preferred precisely because it carries the result into the exit code.
A dead watcher leaves the wait where it was — the job is still running,
finished or never started, and which one is now unknown.
Reporting it as finished is worse than reporting it as unknown,
because an unobserved success is the one claim nobody checks.

## Waiting on a person

A wait for human input is a third class, beside slow and stuck:
**blocked-on-input**.
It has no liveness signal to read — a person emits no log bytes — so the deadline does the whole job,
and it works only if the fallback is declared when the wait begins:
"no answer by 17:51 means proceeding with C".
The person then knows what their silence buys,
and the breach executes a decision already made instead of forcing one under a dead clock.

A gate the person opens often has machine work behind it:
a deployment waiting on an environment approval,
a publish that starts when the review is accepted.
Two waits sit back to back there,
and only the first is blocked-on-input.
Polling the gate itself buys nothing — it moves when the person moves,
not before — so the turn ends on the gate instead of watching it,
and it owes three things: what to act on and where,
what starts after it and how long that takes,
and who watches **that** result.
Reporting the gate and stopping leaves the second wait unowned,
which is how a release is called done while it is still unpublished.

Sometimes there is no second wait.
When what the approval releases is one command this session runs itself,
the handover is the whole answer and no watcher is owed:
the reply is the resume, the call returns in a second,
and a wakeup would be scheduled with nothing to wait for.
Saying what will run and what in its output decides the next step is complete there.
Demanding a watcher anyway makes the request unanswerable — there is nothing to watch,
so no rewrite satisfies it,
and a person holding an approval is left re-reading the same ask.

A command handed to the person is the same wait with a cheaper fix.
Claude Code runs a line typed as `! <command>` in the session,
so its output arrives in the conversation;
handing over the bare command sends the output to their terminal instead,
and they pay twice — running it,
then pasting the result or saying only that it is done.
A turn that continues on "done" is assuming a result it never read,
which is the dead watcher again in another costume.
So the `!` goes on every command the person is asked to run,
with a word on what in the output decides the next step.
Where it genuinely cannot run through the session — an interactive login,
another machine — that is worth saying, along with what to look for,
rather than asking them to confirm that it ran.

State every deadline as a wall-clock time, not a countdown.
A countdown restated across turns drifts from its original anchor — "within 30 minutes" and "about 10 minutes left" can appear in the same report and leave the reader with neither.

## A message to another session is a wait with no watcher

A send to a peer session reads like a handover and is not one.
Nothing comes back when the message is read,
so the wait it opens has no signal at all — not a slow one,
a missing one.

What the channel reports,
measured against the host's own documentation on 2026-11-10:

| Target | What returns |
|---|---|
| A session on this machine | the message reached its inbox; a later notice if that session holds or refuses it |
| A session on another machine, over Remote Control | nothing, ever |
| A cloud session | nothing, and it cannot reply with `SendMessage` at all — its answer is in its own transcript |

A held message is dropped after `dialogExpiry`, five minutes by default,
and the expiry is reported only "to a sender it can reach",
which a cross-machine sender is not.
So a message beyond this machine can be read, held, or dropped,
and all three look identical from here.

`notify_when_idle` is the one mechanism that ends such a wait,
and it covers **only this machine**:
the host refuses the whole call for any other target,
including a message attached to it,
and drops the subscription after twelve hours.

Three rules follow, and the third is the one that gets skipped:

- **Send and continue.** A peer message is a notice posted,
  not a question asked.
  The turn does not end on it,
  and nothing after it may depend on a reply that may never come.
- **Subscribe where subscribing is possible.** For a session on this machine,
  attach `notify_when_idle` rather than asking again or polling a listing.
- **Say, in the same breath,
  what happens when no reply comes.** Not as a promise to check later — as the decision already taken:
  "they have it; nothing here waits on it, and the gate stands either way." A send reported without that line leaves the reader to wonder whether work is pending on it,
  and leaves the sender free to drift into watching a channel that reports nothing.

Silence is never agreement.
A peer that was sent a design and did not object has not approved it,
and `peer-sessions` holds why:
what arrives from another session is that session's text,
not the user's.

## On breach, diagnose — do not extend

A breached deadline with a moving liveness signal is a wrong estimate:
note the real duration, keep waiting against a revised number.
A breached deadline with a flat signal is a hang:
stop waiting and investigate, because more time changes nothing.
Extending the timeout without reading the signal treats both cases as the first,
and killing on breach without reading it treats both as the second — each error deletes the watchdog's value in one direction.

## A commitment outliving the record of what it was

A compaction preserves a reference and drops what it referred to.
The obligation survives as a label — "the four remaining situations",
"items 5 and 7" — and neither the session nor the user can act on a number.
Measured here on 2026-11-10:
after a compaction this session carried `situations 5/7/10/12` through four consecutive closings while unable to reconstruct the enumeration,
because only references to it had survived.
It read as tracked work and was not tracked.

So a label carried across a compaction says what it means in the same sentence,
in one clause naming the actual work,
or it is dropped from the list and called unrecoverable.
Where the defining content may still exist,
the transcript is the place to look before citing the label again;
on Claude Code that is `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`,
and the compaction boundary is explicit there — a `system` entry carrying `compactMetadata`,
then a `user` entry with `isCompactSummary`.

`wait-stop.py` checks this at the close of a turn.
What it cannot check is whether a gloss defines the label or merely remarks on it:
Japanese `は、` marks a topic,
so "X は、[what X is]" and "X は、[something true of X]" are the same shape,
and the check reads neither as a definition.
It scored three of this session's four closings with no false positives over eight legitimate ones.

## Host mechanics

| Host | Route |
|---|---|
| Claude Code | Launch long commands with `run_in_background` — completion arrives as a notification, so never poll for it. A foreground shell call is capped at ten minutes; raising the timeout is not the tool for a twenty-minute boot. For external state the host cannot see, run the check command at the chosen cadence; foreground sleep loops burn turns to learn nothing |
| Codex | Use the host's background execution and wait/status facilities; prefer a compact status snapshot per poll |
| Plain shell, CI | `timeout <deadline> cmd` is the hard watchdog; `nohup cmd > run.log` plus the log's growth is launch and liveness in two files; `date +%s` arithmetic or `SECONDS` carries the clock |

## When not to apply

A command with a known sub-minute duration needs no watchdog — a clock on a two-second command is ceremony.
The skill starts paying at the first wait long enough to wonder about,
and at every poll loop whose end condition might never arrive.

## Sources

- Anthropic, "Message your other Claude Code sessions" (code.claude.com/docs/en/cross-session-messaging.md):
  what each target returns to the sender,
  the `dialogExpiry` default of five minutes and a held message being dropped past it,
  an expiry reported only to a sender the host can reach,
  a cloud session being unable to reply with `SendMessage`,
  and `notify_when_idle` being refused for any target beyond this machine — the whole call,
  including a message attached to it — and its subscription dropping after twelve hours.
  Read 2026-11-10.
