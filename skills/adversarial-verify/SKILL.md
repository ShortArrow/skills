---
name: adversarial-verify
description: |
  Adversarial verification before acceptance, triggered by the moments a claim is about to pass unopposed: a subagent or tool has returned "done", "passed" or "found" and the result is about to be relayed as fact; review findings are about to be reported as confirmed though nobody has tried to kill them; a plausible document, search result or model output is about to enter a decision. A report is a claim, not an observation, and a finding nobody attacked survives by default. Not for facts one command can check — run the command. Invoke as /adversarial-verify to turn it on your own conclusion before presenting it.
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Agent
---

# Adversarial verification

An accepted claim is load-bearing the moment it lands: the next
decision stands on it. Acceptance is therefore the cheapest place to
catch an error — one attack before, or an excavation after.

## The moments this replaces

| About to… | Instead |
|---|---|
| relay a subagent's "done" as fact | run one probe that would fail if the report is wrong |
| report a finding as confirmed | write down what would kill it, then look for that |
| adopt a plausible document or search result | ask how it would read if it were wrong — plausibility is fluency, not provenance |
| grade your own work in the context that wrote it | hand the verdict to a fresh context with refute-by-default |

## A report is a claim, not an observation

A subagent's "done", a tool's "passed", a reviewer's "confirmed" — each
is a conclusion someone else drew from observations you have not seen.
Accepting the verdict imports their blind spots at zero cost. Ask for
the observation, or make one: run the test yourself, read the diff,
curl the endpoint. The probe must be able to fail; a check that cannot
fail is a ceremony. One probe is usually enough — the point is not to
redo the work, it is to give the report one chance to be wrong.

## Write the refutation before the defense

For each claim, state the observation that would kill it — the input
that breaks the fix, the caller the finding forgot, the environment
where the benchmark inverts. Then search for that, not for more
support. Support accumulates without limit and proves nothing; a claim
is only as good as the strongest attack it has survived. A claim you
cannot write a refutation for is not yet precise enough to accept.

## Author and judge must not share a context

Self-review passes by construction: the context that produced the work
contains the reasoning that made every choice look right, and the
judge inherits it wholesale. Move the verdict to a context that holds
only the artifact and the acceptance criteria — a subagent told to
refute, with "refuted" as the default verdict when uncertain. What
survives that is worth reporting; what survives your own reading is
just what you already believed.

## Expensive claims earn a panel

When being wrong is costly — a security sign-off, a release gate, a
conclusion about production — one skeptic is a coin flip on their
blind spot. Fan out independent skeptics with distinct lenses (does it
reproduce, what does it break, who else calls this) and let a majority
kill. Diversity catches what redundancy cannot: three identical
skeptics share one blind spot three times.

## When not to bother

The attack has a cost, and spending it everywhere protects nothing. A
fact one command can check — a version, a flag, a line count — is
checked, not contested. A claim that is cheap to reverse is accepted
and watched. The gate: what does it cost if this is wrong and nobody
catches it for a week? Below that bar, accept and move on.

## /adversarial-verify on your own conclusion

Before presenting a conclusion, in order: state it as one falsifiable
sentence; list the observations behind it — commands run and their
output, not impressions; write the strongest refutation you can; go
look for it; present what survived, naming the attack it survived. A
conclusion delivered with its survived attack is worth more than one
delivered with ten confirmations.
