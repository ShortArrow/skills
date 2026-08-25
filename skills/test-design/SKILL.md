---
name: test-design
description: |
  Deriving test cases, triggered by the moments that produce weak ones: about to write a test list that is the happy path restated, about to derive tests by reading the implementation they are meant to check, about to test the bound the specification names and not the other one, about to enumerate the roles the specification lists and skip the caller it forgot, about to vary one condition at a time from the happy path, about to draw a state or decision table without tying each row to a test, about to write an expected result with "or" in it, about to skip the error paths as unlikely, or about to grade a suite as adequate by reading it. A test derived from the implementation passes by construction and encodes the bug beside the behaviour; coverage counts equivalence classes under a named criterion, not tests. Use when writing a test plan, list or specification, when a use case or scenario is the specification in hand, when adding tests to existing code, when reviewing a suite for gaps, and when a suite is all green and proves little.
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
| test the bound the specification names | every range has two ends; the one the sentence left out is still a boundary |
| enumerate the roles the specification lists | add the caller it forgot: no role, unauthenticated, unassigned |
| vary one condition from the happy path | build the decision table and cover the rules where two conditions fail together |
| draw a state table and move on | put a test id in every row; the row that says "not allowed" most of all |
| write "rejected, or accepted provided…" as an expected result | one outcome per case; a specification that cannot decide is an open question, not a test |
| skip error paths as unlikely | each failure mode is a class: invalid input, missing resource, denied, timeout, half-done |
| test a feature by its main flow | read the alternate and exception flows off the use case; each is a class |
| grade a suite by reading it | count it against the specification: classes, both bounds, rules, transitions |
| add a fifth test to a covered class | spend it on an uncovered class — the fifth buys runtime and no coverage |

## Attack the specification, not the implementation

A test written by reading the code asserts what the code does. It passes
on arrival, it encodes the current bugs as expectations, and its failures
after a change say "the code changed", which was already known. This is
measured, not suspected: on 24 Java repositories, LLM-generated oracles
tended to capture the program's actual behaviour rather than its expected
behaviour (Konstantinou, Degiovanni, Papadakis, arXiv:2410.21136).

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

The classes the specification lists are the easy half. A role table with
three rows has a fourth class, the request that matches none of them,
and it is the one a suite built from the table never contains. For each
parameter, write the invalid classes beside the valid ones before
writing any case: wrong type, absent, outside every listed value, the
caller with no rights at all.

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

## The side the specification did not name

"Up to 10 MB" names one end of a range. The other end exists whether
or not the sentence mentions it, and cases derived from the text stop
where the text stops: a suite with the upper bound tested at −1, 0 and
+1 bytes and nothing below 1,024 has done boundary analysis on half a
range. Write the minimum and the maximum of every partition down
first, then take each with its nearest neighbour in the adjacent
partition. The unnamed side is usually zero, empty or one, and the
specification is usually silent about it because nobody decided.

## Move two conditions at once

A suite built by changing one condition from the happy path covers
every value of every condition and almost none of their combinations:
format wrong, size over, count over, each alone, and no case where two
fail together. Which error wins when both apply is rarely in the
specification either, so the missing case hides a missing decision.

Lay the conditions out as a decision table and count the rules, then
cover the rules where two conditions fail at once and the rule where a
role restriction and a format restriction both apply. The same document
can read as fully covered under all-conditions and a quarter covered
under all-rules, and only the second number says anything about the
combinations.

## A table is a claim about the suite

A state table, a decision table, the flow list of a use case: each row
claims that a test exists for it. Put the test id in the row. A row with
no id is an uncovered class, and the row that reads "not allowed" is
the one most likely to be empty, because writing the prohibition felt
like handling it. The forbidden transition — the second send while one
is in flight — is the test, and the guard that is supposed to stop it
is the thing under test.

Then read the two documents against each other. A test whose path
disagrees with the table (the table says failed → sending, the test
goes failed → selected → sending) means one of them is wrong, and
nothing but the comparison finds out which. Self-transitions and the
transitions out of the failure state count as rows too.

## One outcome per case

"Rejected, or if accepted, no corrupted data remains after send" cannot
pass or fail. It appears honestly, when the specification never said
what happens to a zero-byte file and the author declined to invent an
answer, and it survives review because the case is visibly present.
The disjunction hides in the expected column. The correct form is a
question to whoever owns the specification, listed as such, and no
test for that class until it is answered.

## Error paths are classes too

The unhappy paths are where untested code accumulates, because nothing
exercises them in normal use — a lock holder dying mid-run, a mapped
folder that does not exist, input with the expected field missing. Each
is an equivalence class with the same claim to a test as any input
range. A suite that only proves the tool works when everything
cooperates has tested the demo, not the tool.

## Use cases enumerate the classes before there is code

A use case is a specification already cut into classes: one main
flow, each alternate flow, each exception flow, and the precondition
under which each can be entered. Whoever wrote it did the enumeration
this skill asks for — the alternate and exception flows are the error
paths — so a suite that exercises the main flow has covered one class
of the N the document lists.

Read the flows off the use case and give each its test, then check
the preconditions, because a flow is reachable only when its
precondition can hold. A parity check for translated pages has a main
flow (both languages edited and committed), an alternate flow (a
one-sided edit declared as an exception), and two exception flows
that only appear once the preconditions are written down: the tree is
dirty, so staleness cannot be judged yet; the history was rewritten,
so a declared commit no longer resolves. Both were hit on one site
within a week. The happy path alone would have shown neither.

Whether an exception flow can actually occur is not settled by how
unlikely it feels. The operating envelope says what is out of scope
and the hazard analysis says what remains; both live in
`assurance-case`, and this skill takes the list they produce instead
of pruning it by intuition.

## Coverage is a number under a named criterion

One test document measured three ways: 100% of conditions, 90.9%
MC/DC, 25% of decision rules. All three are true of the same file, so
a coverage figure without its criterion says nothing, and a figure
whose criterion is chosen after the count says less. Name it before
counting: equivalence classes (valid and invalid), two-value
boundaries, decision rules, transitions taken once each. The rest of
what a number owes its reader is in `measured-claims`.

## Checking a suite: count, do not judge

Asking whether a suite is adequate returns the blind spots that
produced it. A second session on the same model shares them, and so
does the same person a day later; that is some independence in the
ISTQB sense, not much. The step that does not share them is counting:
list the classes off the specification and tick the ones with a test,
list both bounds of every range, list the rules of the decision table,
list the rows of every state table, and cite the file and line of each
gap. Whether an expected value is *right* stays a judgement and stays
with a reader who did not write it; whether a class *has* a test is
arithmetic. If the count was sampled rather than exhaustive, the
report says sampled. The refute-by-default form for the verdict is in
`adversarial-verify`; this skill supplies what to count.

## A test that can skip is a test that can lie

A fixture that fails to build, a precondition that quietly does not
hold, a guard that exits early — the test reports green while asserting
nothing. When a fixture produces the input, assert that it did: a suite
that found zero commits to scan and passed has not scanned anything.
The vacuous pass is the test-design counterpart of the never-seen-red
rule: both are tests whose ability to fail was assumed, not shown.
