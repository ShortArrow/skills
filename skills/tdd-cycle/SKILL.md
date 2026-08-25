---
name: tdd-cycle
description: |
  Red-Green-Refactor as the working procedure, triggered by the moments that replace it: about to verify a change by running the program and reading its output, about to edit code with no failing test in hand, about to fix a bug at the suspected line before reproducing it in a test, about to touch code that has no tests at all, about to paste the observed output into an assertion's expected value, or about to write "add tests later" into a plan. A log line cannot fail before the change and pass after it, so running-and-looking is observation, not verification. Use when implementing, fixing or refactoring anything whose behaviour can be asserted.
allowed-tools: Bash, PowerShell, Read, Edit, Write
---

# The cycle is the procedure

Red, then green, then refactor. Not a review standard applied afterwards —
the order in which the work happens.

1. **Red.** Write the smallest test that fails for the reason the change
   exists. Run it. **The failure message is part of the work product**:
   keep it, because it is the only evidence the test can fail at all. A
   test first seen passing proves nothing — a test that asserts nothing
   passes too. The expected value comes from the specification and is
   written before the implementation exists; that order is the whole
   defence against an oracle that copies the code, which is what
   generated oracles measurably tend to be (arXiv:2410.21136). An
   expected value with "or" in it cannot go red for a reason, so it is
   a question for the specification, not yet a test.
2. **Green.** The smallest change that makes it pass. Resist fixing the
   adjacent thing; it has no failing test yet.
3. **Refactor.** Only while green, and the tests stay untouched. If a
   structural change needs the tests edited, it was not structural.

## The moments this replaces

Each of these is the cycle skipped, and each has a correct form:

| About to… | Instead |
|---|---|
| run the program and eyeball the output | write the assertion that would have read that output, and let it fail first |
| fix the bug at the line that looks wrong | reproduce it as a failing test before touching the line — otherwise nothing distinguishes *fixed* from *moved* |
| edit code no test covers | pin current behaviour with a characterisation test first, then change against that baseline |
| paste the observed output into the expected value | write the expected value from the specification; if the specification is silent, that is a question to ask, not a value to assert |
| write "tests will be added later" | write the test list now, even if the tests come later — deciding what would be asserted is the part that shapes the design |

The second row is the one that pays most. A bug that was never reproduced
in a test can return without anything failing.

## Characterisation tests

For untested code, the first test asserts **what the code does today**,
verified by running it, not what it should do. Mark it as such — a pinned
bug looks identical to a pinned feature, and nothing downstream can tell
them apart. This is the minimal entry point the cycle needs before any
edit to legacy code.

## The shape of a test

Given a state, when one thing happens, then one expected difference.
Assert the delta, not the whole world: a test that asserts everything
fails for every reason, which is the same as explaining nothing. If the
Given cannot be stated, the ambiguity is in the design, not the test —
settle it first. Which Givens the list needs (the classes, both ends of
every range, the combinations) is `test-design`; this skill only fixes
the order in which each one is written.

## When a test is genuinely impractical

Hardware in the loop, a GUI without a harness, a one-shot migration.
The fallback is not silence: state that the change is going in untested,
write the test plan — the cases, the expected values, what blocks
automating them — and leave it where the follow-up happens. An untested
change that says so is recoverable; one that does not is a time bomb with
no manifest.

## What this is not for

- **Spikes.** Exploring a shape with throwaway code needs no tests — but
  the spike is thrown away, and what gets kept is rewritten through the
  cycle. Keeping the spike *is* skipping the cycle.
- **Prose and configuration with no assertable behaviour.** Where a check
  exists (a linter, a parity script, a schema), that check plays the role
  of the test: see it fail first, same rule.
