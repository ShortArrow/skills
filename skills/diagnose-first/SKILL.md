---
name: diagnose-first
description: |
  Diagnosis before correction, triggered by the moments that skip it: about to name a cause because it appeared at the right time, about to declare a fix worked because the symptom went quiet, about to explain two symptoms with one cause nobody tested, about to change something without having reproduced the failure, or about to read a configuration value and call it the running state. A monthly event correlates with every symptom that starts that month, and an intermittent fault goes quiet after anything. Use when investigating a bug, an outage or a flaky failure, and before writing "root cause" anywhere.
allowed-tools: Bash, PowerShell, Read, Grep, Glob
---

# Diagnose first

A correction applied to an undiagnosed fault is an experiment with no
control. Sometimes it lands; nothing distinguishes landing from
coincidence, and the fault keeps its second chance.

## The moments this replaces

| About to… | Instead |
|---|---|
| name the cause that appeared at the right time | ask how often that suspect appears regardless — its base rate |
| declare the fix worked because the symptom stopped | set the pass criterion *before* acting: how long quiet counts as fixed |
| explain two symptoms with one cause | test the link, or investigate them separately — shared cause is a hypothesis, not an economy |
| fix without reproducing | reproduce, or say the change is speculative and keep watching |
| quote a config value as the running state | read the running state; the config is what was requested, not what is |

## Correlation needs a base rate

Parts of every system change constantly — monthly updates, daily deploys,
rolling restarts. A symptom that starts in late June will always find a
late-June change to blame. Matching to the minute adds nothing over
matching to the day when the suspect fires every day.

The question that breaks the spell: **how many times did the suspect
occur without the symptom?** Ten reconnections, four crashes is a
different fact from "crashes follow reconnection" — the denominator is
where the claim lives. Count the non-events; they never volunteer.

## Decide what would refute it, before acting

A diagnosis you cannot state a refutation for is a preference. Before
changing anything, write down what observation would kill the hypothesis
— an event that should be in the log and is not, a machine that should be
affected and is not, a setting that should matter and does not. Then look
for that, not for more confirmation.

The absence of an expected trace is evidence, and it is the cheapest
kind: one missing log line can eliminate a whole family of causes at
once. It only works if you asked what should be there before looking.

## Intermittent faults need the pass mark in advance

An intermittent fault goes quiet after anything — that is what
intermittent means. Whatever you just did, a good stretch follows
eventually, and it will feel like confirmation. Decide before acting how
long green means fixed, and let a revert be part of the plan when the
stretch falls short. A fix accepted without a pass mark is superstition
with a commit hash.

## Two faults at once show neither signature

A weak battery tracks charge. An obstruction tracks position. Both at
once track nothing — and a symptom that tracks nothing looks deeper than
it is, pointing the investigation at drivers and kernels when the answer
is two cheap faults stacked. When no single hypothesis tracks the
symptom, try superposition before exotics.

## State, not configuration

`DisableRealtimeMonitoring: False` is a preference. `AMRunningMode: SxS
Passive Mode` is the state, and it says the preference is moot. Every
system has this pair — the value that was set, and what is actually
running — and diagnosing from the first produces mechanisms that sound
right and are not occurring. When a claim matters, find the interface
that reports what *is*, and quote that one.
