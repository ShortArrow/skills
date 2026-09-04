---
name: assurance-case
description: |
  Turning "it works" into a claim that can be supported: assurance = property × conditions × scope × acceptance criterion, held up by an argument resting on evidence, built in a fixed order — claim, assumptions, boundary, failure modes (FMEA/FTA/STPA), requirements, verification, evidence, residual risk. Tests come last and are counted against claims: a million cases that never touch R-27 are zero evidence for R-27. The suite is the only home of every claim it can express; assurance prose holds just the remainder — hazards, out-of-scope, residual risk. Use when asked to guarantee or "make sure" something works, when a performance or reliability figure is about to be promised without its conditions, when planning what to test for a nonfunctional requirement, and when reporting something as verified or reliable.
---

# Claim, Argument, Evidence

"It works" cannot be assured, because it names no property, no
conditions, no scope and no criterion. The unit of assurance is a
claim:

> On Windows 11 24H2, on the specified CPU and driver, at CPU load
> below 80%: 99.999% of frames complete within 1 ms of arrival, and
> no frame exceeds 1.5 ms.

**Assurance = property × conditions × scope × acceptance criterion.**
Leave any factor implicit and every test that follows checks
something unstatable — after a thousand green runs nobody can say
what was confirmed.

A claim is then held up by an argument, and the argument rests on
evidence. That three-layer shape — the SEI's assurance case — is the
whole method; everything below is the order in which to build one.

## The eight questions, in order

| Stage | Question | Instrument |
|---|---|---|
| 1. Claim | What is being assured? | Assurance case |
| 2. Assumption | Under what premises? | Contract, ConOps |
| 3. Boundary | Up to where? | Operating envelope |
| 4. Failure | What can break? | FMEA, FTA, STPA |
| 5. Requirement | What counts as passing? | Requirements engineering |
| 6. Verification | How is it checked? | Test, analysis, review, measurement |
| 7. Evidence | What remains as proof? | Traceability, test evidence |
| 8. Residual risk | What is still not assured? | Risk assessment |

The order is the discipline. Testing begins at stage 6; starting
there — the usual reflex — produces tests that check nothing anyone
committed to.

## Assumptions are the contract

The premises a claim stands on are enumerable, and unlisted ones are
the ones that fail:

```text
A1: OS is Windows 11 x64          A5: frames are <= 1024 bytes
A2: RAM is >= 16 GB               A6: input rate is <= 1 kHz
A3: the device is connected       A7: the system clock never runs backwards
A4: driver >= 4.2 is installed
```

Only now does the claim have a shape: A1–A7 hold, therefore C1. This
is Design by Contract at system scale — precondition, program,
postcondition, `{P} C {Q}` — and an unstated assumption is a
precondition the caller cannot see and so cannot honour.

## The boundary states where knowledge stops

The envelope's job is the opposite of a feature list: it records the
line beyond which nothing is claimed. OS crash, hardware failure, a
malicious kernel driver — outside the envelope, and said to be
outside, so that "we never claimed that" is written down before the
incident instead of pleaded after it.

## Failure is analysed before tests are written

Three instruments, three directions:

- **FMEA**, bottom-up: this part fails — then what? A network drop
  becomes a `read()` timeout becomes a stalled worker becomes a
  frozen UI becomes lost frames; each arrow is a row.
- **FTA**, top-down: this hazard occurred — by which combinations of
  causes? The tree runs from the unacceptable output back to its
  minimal cut sets.
- **STPA**, for the accidents the other two cannot see: A is
  healthy, B is healthy, C is healthy, and the A→B→C interaction
  still causes the loss. Control structure and unsafe control
  actions, in place of component failure. GUI + device + network +
  real-time is exactly where this class lives.

What stage 4 yields is the hazard list that stages 5 and 6 exist to
cover.

## Tests are chosen last and counted against claims

Each requirement names its verification — unit test, integration
test, static analysis, review, measurement, formal argument — and the
map is the traceability matrix: generated from test names and tags
where a suite exists, requirement by requirement.

The count that matters is coverage of claims, and volume does not
substitute: a million test cases that never touch R-27 are zero
evidence for R-27. What makes a body of tests strong is the chain
that can be walked — claim → requirement → hazard → mitigation →
verification → evidence — not its length.

## The suite holds what it can express

A test is already a claim in the assurance shape: premises in its
setup, a criterion in its assertion, verified by machine on every run
and following the implementation the way no prose can. So for any
claim the suite can express, the suite is its only home — assumptions
become fixture guards, acceptance criteria become assertions, and the
requirement's identity travels as a test name or tag. The
traceability matrix is generated from those tags; a hand-maintained
matrix is the same knowledge kept twice, and the copies part ways at
the first refactor.

Prose earns its place only where the suite cannot reach: the hazard
inventory (a test can cover a hazard, none records the list), the
envelope's out-of-scope line (absence has no test), residual risk,
and measurement records frozen with their method and date. An
assurance document that restates green tests is ceremony; one that
holds exactly this remainder is the case.

## Verification is not validation

Verification: was it built as decided? Validation: was the right
thing decided? The stop button specified at 100 ms and measured at
99 ms verifies; if avoiding the accident needed 10 ms, it does not
validate. Both questions get asked, because a green suite answers
only the first.

## The dictionary against forgotten axes

When the quality question is "what am I failing to even consider",
ISO/IEC 25010:2023 enumerates the characteristics — functional
suitability, performance, compatibility, usability, reliability,
security, maintainability, portability and their sub-characteristics
— as a checklist for requirement-writing, ahead of any measuring.

## The case, assembled

```text
C1: fit for 1 kHz data acquisition
├─ C1.1 no input frame is lost      → load test, soak test, buffer analysis
├─ C1.2 deadlines are met           → WCET measurement, high-load test
├─ C1.3 failure stops safely        → fault injection, FMEA
└─ C1.4 corruption is detected      → CRC test, property test

Context:      Windows 11, driver >= 4.2
Assumptions:  input <= 1 kHz, frame <= 1024 bytes
Out of scope: OS crash, hardware failure, malicious kernel driver
```

Context, assumptions and out-of-scope travel with the tree; a claim
tree without them is the vague "it works" again, drawn prettier.
Where a suite exists, the arrows are generated from its names and
tags, not typed by hand. And
stage 8 is written, not implied: what this case does not assure is
part of the case.

The tree above is an argument structure, and there is a public
notation for exactly that shape: Goal Structuring Notation, whose
Community Standard (Version 3, SCSC-141C, from the Safety-Critical
Systems Club) is the reference. In its vocabulary the claim is a
goal, the reasoning step that splits a goal into sub-goals is a
strategy, and a piece of evidence is a solution; context,
assumptions and justifications are elements attached to the goals
they qualify rather than prose beside the diagram, and a goal left
without support is marked undeveloped instead of omitted. That last
mark is stage 8 drawn in: the residual risk has a symbol, so a case
cannot look complete by leaving it out. The mapping here is this
skill's reading of the notation; the standard's own definitions
govern where they differ.

The essence: the goal is never to prove the system perfect. It is to
reach the sentence "under these conditions, within this scope,
against this risk model, this evidence supports this claim" — and to
have every noun in that sentence written down.

## When not to apply

A full assurance case for a CRUD form is ceremony. Two parts cost
nothing and always apply: a claim carries its conditions, and each
requirement names the evidence that checked it. The rest — FMEA,
STPA, WCET, formal argument — scales with the harm of the claim
being wrong, which is a stage-8 judgement made once, at the start.

## Sources

- GSN Community Standard, Version 3, document SCSC-141C, Safety-Critical
  Systems Club (scsc.uk/gsn-standard). Version and document number
  checked on 2026-09-04; the element mapping above is paraphrase, not
  quotation.
- ISO/IEC 25010:2023 is named for its characteristic list only; it is
  not free, and no rule here depends on its text.
- FMEA, FTA and STPA are named as methods. Their standards (IEC 60812,
  IEC 61025) are not free; the STPA Handbook (Leveson and Thomas) is a
  free pointer for the third.
