---
name: measured-claims
description: |
  Publishing numbers, triggered by the moments that detach them from their measurement: about to write a figure without how it was measured, about to compare numbers taken under different conditions, about to report a single run as the value, about to reuse a figure measured weeks ago as current, or about to quote an estimate where the real quantity is one command away. A number without its method is a rumour, and without its date it rots silently — a document can carry two stale figures that disagree with each other and both be wrong. Use when a benchmark, note, commit message or README is about to carry any measured quantity.
allowed-tools: Bash, PowerShell, Read, Grep
---

# Measured claims

A number in a document makes a claim the prose around it inherits. The
figure that cannot say how it was obtained, on what, and when, spends
credibility the document does not have.

## The moments this replaces

| About to… | Instead |
|---|---|
| write a figure with no method | attach the command and the environment it ran in |
| compare across different conditions | re-measure both sides under one condition, or compare nothing |
| report one run | run enough to see the spread, and report it: `127 ms (115–144), 15 runs` |
| reuse an old figure as current | re-measure, or date it and say what it moves with |
| quote an estimate when measurement is cheap | run the command — the estimate that prompted it is not worth defending |

## The method travels with the number

"7,392 characters" is a rumour. "7,392 characters under a mise shim,
limit 8,191, printed by `doctor.ps1`" is a measurement — it names the
instrument, so a reader can re-run it, dispute it, or notice that their
own machine differs. When the figure came from a one-off pipeline rather
than a script, the pipeline is the method: paste it.

The strongest form is a number a script reprints on every run. A figure
with a living instrument cannot silently drift from its source, only
from the document — which the date exposes.

## Date what moves independently

Some numbers move with the repository and need no date — the diff shows
when they changed. The ones that need dating move with something else:
the tool list, the installed packages, an external service. A document
once carried 894 and 185 for the same headroom, both stale, disagreeing
with each other — nothing in the repository had changed, and no diff
would ever have flagged either. State the date and what the number moves
with, so the reader knows what invalidates it.

## One run is an anecdote

Process spawn on a managed machine varies by tens of milliseconds run to
run; the first invocation pays caches the rest do not. A single number
sampled from that is a lottery ticket. Report the count and the spread —
median with range beats mean alone, and `(115–144)` tells the reader
more than a fourth significant digit would.

The spread is also the honesty check on a comparison: two medians whose
ranges overlap are one result, not two.

## Measure the claim, not a proxy

Parameter count and quantisation predict VRAM the way horsepower
predicts lap time. When the claim is "fits in 8 GB at 32k context", the
measurement is the resident size at 32k context, read back from the
runtime — not the estimate that motivated the attempt. Proxies choose
what to try; only the quantity itself supports the sentence that gets
published.

## Say what the number depends on

A timing measured behind a synchronous endpoint scanner is a fact about
that machine, and presenting it bare invites a reader to generalise it.
Name the environmental facts the number leans on — or point at one page
that describes the machine — so a reader can tell which figures would
hold on their hardware and which are local colour.
