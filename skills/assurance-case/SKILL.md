---
name: assurance-case
description: |
  Turning "it works" into an engineering claim that can be supported. An assurance is a claim — property × conditions × scope × acceptance criterion — held up by an argument that rests on evidence (the SEI's assurance-case structure), and the work runs in a fixed order: claim, assumptions, boundary, failure modes, requirements, verification, evidence, residual risk. Tests are chosen last and counted against claims — a million test cases that never touch requirement R-27 are zero evidence for R-27 — with each requirement traced to the verification that checked it (NASA's traceability matrix). Assumptions are the contract ({P} C {Q}: an unstated assumption is a precondition the caller cannot see); the boundary states where knowledge stops, not what the system can do; failure is analysed before tests are written (FMEA bottom-up, FTA top-down, STPA for accidents where every component is healthy); verification asks "built as decided?", validation asks "decided on the right thing?"; ISO/IEC 25010 is the dictionary against forgotten quality axes; and what is still not assured is written down as residual risk, not implied. Use when asked to guarantee, assure, or "make sure" something works, when a performance or reliability figure is about to be promised without its conditions, when planning what to test for a nonfunctional requirement, and when reporting that something is verified or reliable.
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
map is kept as a traceability matrix, requirement by requirement.

The count that matters is coverage of claims, and volume does not
substitute: a million test cases that never touch R-27 are zero
evidence for R-27. What makes a body of tests strong is the chain
that can be walked — claim → requirement → hazard → mitigation →
verification → evidence — not its length.

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
tree without them is the vague "it works" again, drawn prettier. And
stage 8 is written, not implied: what this case does not assure is
part of the case.

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
