---
name: test-design
description: |
  Deriving test cases, triggered by the moments that produce weak ones: about to write a test list that is the happy path restated, about to derive tests by reading the implementation they are meant to check, about to pick a comfortable mid-range value where faults live at the edges, about to skip the error paths as unlikely, or about to equate a large test count with coverage. A test derived from the implementation passes by construction and encodes the bug beside the behaviour; coverage counts equivalence classes, not tests. Use when writing a test plan or list, when adding tests to existing code, and when a suite is all green and proves little.
allowed-tools: Bash, PowerShell, Read, Grep, Glob
---

# Test design

The cases decide what the suite can catch. Everything after — the
harness, the runner, the count — only executes that decision.

## The moments this replaces

| About to… | Instead |
|---|---|
| write the happy path and stop | walk the input space: for each parameter, its classes and its edges |
| derive cases from the implementation | derive them from the specification, and let the implementation surprise you |
| test with a comfortable value | test the last value inside and the first value outside each boundary |
| skip error paths as unlikely | each failure mode is a class: invalid input, missing resource, denied, timeout, half-done |
| add a fifth test to a covered class | spend it on an uncovered class — the fifth buys runtime and no coverage |

## Attack the specification, not the implementation

A test written by reading the code asserts what the code does. It passes
on arrival, it encodes the current bugs as expectations, and its failures
after a change say "the code changed", which was already known.

Derive from what the thing is *supposed* to do — the spec, the wire
format, the contract — and only then run it. The one legitimate
exception is the characterisation test that deliberately pins current
behaviour, and it is marked as such so nobody later mistakes a pinned
bug for a requirement.

A useful smell: if every test was green on its first run, the suite was
derived from the implementation, whatever the intent was.

## Equivalence classes: count classes, not tests

Inputs that the code cannot tell apart form one class, and one test per
class is enough — the second through fifth cost runtime and prove
nothing new. The discipline runs both directions: no class left
uncovered, no class covered twice by accident.

A suite of seventeen tests reads as thorough. Whether it is depends on
how many of the classes those seventeen fall into, and that number does
not appear in any runner's output. It has to be counted against the
input space by hand — which is what a test plan is.

## Boundaries, because that is where the faults are

Off-by-one is the most common arithmetic fault, and it is invisible
everywhere except at the edge. For each boundary the pair that matters
is the last value inside and the first value outside. The recurring
edges: empty, exactly one, many; zero and negative; the declared
maximum and one past it; the value that is exactly the buffer, the
limit, the timeout.

A concrete pair from this machine: a PATH check that is fine at 8,190
characters and must fail at 8,192 has to be tested at those two values.
Passing at 4,000 and 12,000 establishes almost nothing about the line
between them.

## Error paths are classes too

The unhappy paths are where untested code accumulates, because nothing
exercises them in normal use — a lock holder dying mid-run, a mapped
folder that does not exist, input with the expected field missing. Each
is an equivalence class with the same claim to a test as any input
range. A suite that only proves the tool works when everything
cooperates has tested the demo, not the tool.

## A test that can skip is a test that can lie

A fixture that fails to build, a precondition that quietly does not
hold, a guard that exits early — the test reports green while asserting
nothing. When a fixture produces the input, assert that it did: a suite
that found zero commits to scan and passed has not scanned anything.
The vacuous pass is the test-design counterpart of the never-seen-red
rule: both are tests whose ability to fail was assumed, not shown.
