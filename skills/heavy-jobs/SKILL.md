---
name: heavy-jobs
description: |
  Launching a job that can fill every core, triggered by the moments that let it starve the sessions beside it: about to run a full test suite, a solution build, a benchmark, a fuzz run or an image build at the priority the agent itself runs at, about to lower the agent, its shell or the terminal multiplexer instead of the job, about to start a build whose compiler server or worker nodes outlive the command at normal priority, or about to hard-code a core mask that fits only this machine. A job at the agent's priority takes the cores from it, and where several agents share one multiplexer their panes stop drawing while keystrokes queue. The machine's own settings, HEAVY_JOB_PRIORITY and HEAVY_JOB_CPUS, decide how the job yields; with neither set it runs at the lowest priority on every core. Use before any command expected to keep the CPU busy for more than a minute on a machine where people or other agents are working.
allowed-tools: Bash, PowerShell, Read
---

# Heavy jobs yield

A build that fills every core at the agent's own priority takes the cores from the agent,
from the other agents on the machine and from the terminal that draws them.
Measured on an 8-core, 16-thread Windows machine on 2026-10-29:
sixteen busy loops at Normal for three minutes left every agent pane at BelowNormal drawing nothing,
while the multiplexer at Normal kept accepting keystrokes into a queue that drained only when the load ended.
The fix is on the job's side: the job is lowered,
and the sessions stay where they are.

## The machine's settings

How far a job yields is a property of the machine — its core count and what else runs on it — so it lives in the machine's profile,
not in a repository's `.env`, and not in a mask typed into a command.

| Variable | Windows | Linux | macOS |
|---|---|---|---|
| `HEAVY_JOB_PRIORITY` | `Idle` or `BelowNormal` | a nice value, `10` to `19` | a nice value, `10` to `19` |
| `HEAVY_JOB_CPUS` | a hexadecimal affinity mask, `FF00` | a CPU list for `taskset -c`, `8-15` | not supported; ignored |

With `HEAVY_JOB_PRIORITY` unset the job runs at the lowest priority:
`Idle`, or nice `19`.
With `HEAVY_JOB_CPUS` unset it runs on every core.
Do not invent a mask for a machine whose settings are absent;
a mask fitted to one core count is wrong on the next machine.
Read both before the launch,
and say in the report which values the job ran with.

## Launch the job already lowered

A priority set after the launch misses every child the job started in between,
so the process is created at the lowered priority:

```bash
# Windows, from Git Bash: Idle is //low, BelowNormal is //belownormal
cmd //c start "" //b //low ${HEAVY_JOB_CPUS:+//affinity $HEAVY_JOB_CPUS} //wait bash run-tests.sh
# Linux
nice -n "${HEAVY_JOB_PRIORITY:-19}" ${HEAVY_JOB_CPUS:+taskset -c "$HEAVY_JOB_CPUS"} ./run-tests.sh
# macOS
nice -n "${HEAVY_JOB_PRIORITY:-19}" ./run-tests.sh
```

```powershell
# Windows, from PowerShell
$prio = if ($env:HEAVY_JOB_PRIORITY -eq 'BelowNormal') { '/belownormal' } else { '/low' }
$cpus = if ($env:HEAVY_JOB_CPUS) { "/affinity $env:HEAVY_JOB_CPUS" } else { '' }
cmd /c "start `"`" /b $prio $cpus /wait pwsh -NoProfile -File run-tests.ps1"
```

On Windows a child inherits its parent's priority class only when that class is `Idle` or `BelowNormal`;
the parent's `AboveNormal` gives its children `Normal`.
A job launched at `Idle` therefore takes its whole tree with it,
and raising the agent instead protects nothing it starts.
The affinity mask is inherited by children as well.

## What escapes the lowering

A process the job reuses was started by an earlier run,
at that run's priority, and lowering the new job does not reach it.
Turn the reuse off for the run:

- MSBuild worker nodes: `-nodeReuse:false`.
- The Roslyn compiler server, VBCSCompiler:
  `-p:UseSharedCompilation=false`.
- The Gradle daemon: `--no-daemon`.

Never lower the agent, its shell or the multiplexer to make room.
Everything started from them afterwards inherits the lowering,
and the next job at Normal starves them;
this is how the panes in the measurement above came to be BelowNormal.

## A job already running

Lower the process and every descendant, not the top one alone.
On Windows, walk `Win32_Process` by `ParentProcessId` and set `PriorityClass` and `ProcessorAffinity` on each;
on Linux, `renice -n 19 -p <pid>` and the children `pgrep -P <pid>` lists,
recursively.

## When not to apply

A command that finishes within a minute needs none of this.
A CI runner with no sessions on it has nothing to starve,
and the job runs at the runner's default.
