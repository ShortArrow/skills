# Design intent

The forces of this repository's design as they stand: what each part
protects, which forces pull against each other, what is refused and
why while that reason holds, and how the next case of the same kind is
decided. This file is edited in place when the forces change; its
history is the series of snapshots a pile of decision records would
otherwise hold. Each section names the gate that enforces it, where
one exists.

## Host-specific skill procedures

**Protects.** A skill works through its concreteness. "Call
`AskUserQuestion`" tells the model what to do; "use the host's
approval mechanism" hands the choice back to the reader. Tool names
and approval mechanisms are runtime protocol, and the protocol is the
part that must stay exact.

**In tension.** The same skill is wanted on many hosts, and each host
names its own tools. Every added host grows the prose. A
generalisation reads as an improvement in review, and what it deleted
does not show in the diff.

**Refused, while these reasons hold.**

- Generalising a host-specific instruction into host-neutral prose.
  The dilution is invisible in a diff and permanent in effect.
- Writing a tool name or mechanism no official document states. A
  wrong concrete is worse than an honest gap; an undocumented
  capability is written as `not documented (checked <date>)` and falls
  through to the last row.
- Substituting one host's procedure or script on another host,
  simulating a missing tool in prose, or pretending a subagent ran.
- One section per host. Sections multiply the words around the
  procedure; a capability table grows by one row per host per
  capability instead.

**The next case.** A new host is one row per capability table,
holding only documented mechanisms with a check date, placed above
the final `Any other host` row, which states a substitute procedure
and the prohibitions. Existing hosts' rows are not touched by the
addition.

**Gate.** `tests/check-portability.ps1`: every branching skill must
name each host and `Any other host`, and per-host invariant strings
(`AskUserQuestion`, `runSubagent`, `ask_user`, `browser_agent`, …)
fail the run when a row is generalised away. Deleting a row's key
string or renaming `Any other host` makes the script exit 1.
