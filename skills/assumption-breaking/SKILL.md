---
name: assumption-breaking
description: |
  The frame a problem arrives in, triggered by the moments a review stays inside it: about to test the inputs the specification names and not the premise it rests on, about to list ten failure modes that are one failure mode restated, about to accept "that cannot happen" as an answer, about to attack the implementation when the specification can be met while the goal still fails, about to look in the same field for analogous failures, or about to report a lateral hypothesis as a confirmed defect. Every component can behave correctly and the system still fail, and the axis nobody checked is the one the checklist does not have. Use when reviewing a design, a specification, an API or a safety argument for what its author did not think of, when a suite is green and proves little, and when an adversarial verifier is running out of things to try. Not for refuting a claim already in hand (adversarial-verify) or for covering a known axis to a criterion (test-design).
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Agent
---

# Assumption breaking

Two kinds of search look alike from outside.
One searches inside the frame the problem arrived in:
stronger material, another pillar, a better algorithm.
The other changes the frame: does anything need to cross here at all,
can the water move instead of the bridge,
can the bridge fail without anyone caring.
Ordinary review does the first well and does it exhaustively,
with `test-design` and `assurance-case` for the axes it already knows.
This skill does the second, on purpose and in order,
because the failure that reaches production is the one on an axis nobody named.
It rests on practice and cites no standard.

## The moments this replaces

| About to… | Instead |
|---|---|
| test the inputs the specification names | list the premises the specification rests on, and test those |
| write ten failure modes | check which axis each one lives on; ten on one axis is one finding |
| accept "that cannot happen" | write the one sentence that says why not, then attack that sentence |
| attack the implementation | first ask whether the specification can be satisfied while the goal is violated |
| ask what breaks when a component fails | ask what breaks when every component works, at an inconvenient moment or in an inconvenient order |
| look for analogous failures in the same field | describe the structure without the vocabulary, and look in three fields that share the structure |
| report a lateral hypothesis as a defect | file it as a hypothesis with its trigger and hand it to `adversarial-verify`; report as defects only what reproduced |
| stop when the list feels long | stop when at least four distinct axes have been walked |

## Extract the frame before attacking it

A problem arrives with its frame already drawn,
and the frame is where the author's blind spots live.
Write it down before touching it:

- **Explicit constraints.** What the specification says must hold.
- **Implicit assumptions.** What it never says because the author took it for granted:
  one client at a time, the clock is right, the cache is transparent,
  the log is written before the response, the name identifies the thing.
- **Goals and invariants.** What the system is for,
  as distinct from what it does.
  "No download after revocation" is the goal;
  "delete the row" is what it does.
- **Relaxable and unrelaxable.** Which constraints are physics or law,
  and which are habit.

A "cannot happen" is an assumption with a reason attached.
Make the reason explicit ("tokens cannot be guessed because they are 128 random bits") and the attack surface appears in the sentence itself:
guessing was never the only way to obtain a token.

## Mutate each assumption with a named operator

Do not ask for lateral thinking; apply operators.
For each assumption in the list, try in turn:

| Operator | Question |
|---|---|
| remove | the assumption is simply false |
| invert | the opposite holds |
| delay | it becomes true later than the code expects |
| duplicate | it happens twice |
| reorder | it happens after what should follow it |
| concurrent | it happens at the same time as something else |
| partial | it is true for some of the parts |
| scale | ten times more, or a tenth |
| swap actor | someone else does it, or is affected by it |
| swap input and output | the result is fed back as the request |
| failure as feature | the error path is the path an attacker wants |
| side effect as main effect | the log, the cache, the metric is the product |
| delete the problem | the component whose failure is being reviewed is not there |

Each row that yields a sentence of the form "if A, then invariant I is violated when T" is a hypothesis.
Most rows yield nothing; that is expected,
and it is why the operators are applied rather than imagined.

## Walk distinct axes, not variants of one

"Find ten problems" produces ten variants of the first problem found.
Before stopping, cover at least four of these,
and name which one each hypothesis belongs to:

- **state** — a transition the model never named
- **time** — expiry, clock skew, ordering, latency, retry
- **actor** — a user who is legitimate and unexpected, an operator,
  a support role, a second tenant
- **resource** — exhaustion, sharing, the limit counted on the wrong key
- **dependency** — a downstream system that is valid and unusual,
  or absent
- **ordering** — two valid operations in the other order
- **scale** — one becomes a million, a million becomes one
- **trust** — where a boundary is crossed by a value that was trusted on the other side
- **interpretation** — a reading of the specification the author did not intend and the text permits

Two hypotheses on the same axis are one finding until proven otherwise.

## Everything works and it still fails

The specification is a description of the parts,
and the goal is a property of the whole.
Ask, in this order:

1. Can the specification be satisfied while the goal is violated?
2. Can two valid operations, each correct, produce an invalid state?
3. Can a safety mechanism itself create the hazard it guards against?
4. What does a user do who is rational and unexpected?
5. What does an external system do that is valid and unusual?

> Revocation is immediate: after a user revokes a link,
> no further download through it succeeds.
> Files are served through the CDN with `Cache-Control: public, max-age=3600`.

Every component is correct.
The handler deletes the row; the CDN honours the header.
The goal, "no download after revocation", fails for up to an hour,
and no test of the handler will find it,
because the handler is not where the failure is.
The same specification stores a path in the link,
so `rename` followed by `download`, two valid operations,
hands out whichever file now lives at that path.

## Borrow failures by structure, not by vocabulary

Searching the same field for analogous failures finds the failures the field already knows.
Instead, describe the structure with no domain words (several agents, a finite resource, each holding one and waiting for another, in a cycle) and look in three fields that share it.
A mutex deadlock and four cars at an intersection each waiting for the car on their right share every word of that description and none of the vocabulary.
The intersection's remedies come back with it:
a right-of-way rule is lock ordering,
a roundabout removes the shared resource,
a traffic light is a scheduler.

Useful fields, because their failure modes are documented and their vocabulary is far from software:
traffic, air-traffic control, logistics, power grids, epidemiology,
accounting controls, diplomacy.
Bring back the failure mode and the remedy, and translate both.

## Diverge boldly, report conservatively

Lateral search produces hypotheses that are interesting and never occur.
The asymmetry is deliberate: generation is wide, reporting is narrow.
Sort everything found into three bins and never let them mix:

- **Confirmed** — reproduced, with the observation that proves it.
- **Hypothesis** — a trigger and a violated property written down,
  not yet reproduced; hand these to `adversarial-verify`,
  whose job is to try to kill them.
- **Exploration** — an axis walked and nothing found,
  recorded so the next reviewer does not walk it again.

A finding, in any bin, carries the violated property,
the triggering conditions,
the reproduction scenario or the reason there is none yet,
the consequence, and the confidence.
A lateral hypothesis reported as a defect costs the reviewer their credibility and the next real finding its hearing.

## When not to bother

A decision that is cheap to reverse is taken and watched,
not framed and re-framed.
A one-line fix inside a well-tested function has no frame worth attacking.
A specification fixed by law or by a customer is still framed (list its assumptions so they are known),
but its constraints are not relitigated here.
The gate is the one `adversarial-verify` uses:
what does it cost if this frame is wrong and nobody notices for a week?

## Connections

`adversarial-verify` takes a claim already in hand and tries to kill it;
this skill produces the claims worth killing, and hands them over.
`test-design` covers a named axis to a named criterion;
this skill finds the axis.
`assurance-case` names the claim,
the assumptions and the boundary and analyses failure modes of parts;
this skill attacks the assumptions it listed and the failures of wholes.
`state-first` designs from states;
the state nobody named is where most lateral findings live,
and finding one is a reason to go back to that skill.
In a plan–implement–verify split (`plan-delegate-verify`),
the verifier's prompt carries this skill and `adversarial-verify` together:
the first to widen the search, the second to narrow the report.
