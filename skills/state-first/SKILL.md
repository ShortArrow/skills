---
name: state-first
description: |
  Designing from states rather than operations, triggered by the moments that skip it: about to add an operation, a branch or an "except when" clause for a case the state model never named, about to add a boolean flag beside the flags already there, about to write a function whose parameters mix what an object is with what it is currently in, about to let a value that fails validation travel further than the boundary it crossed, or about to describe a feature by what it does before saying what must be true afterwards. An if added for an overlooked state hides the state; a fourth flag multiplies the cases every branch and every test must cover. Use when specifying or implementing a feature, when a conditional is about to grow, when reviewing a signature, and whenever the Given of a test cannot be written down.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# State first

An operation is a transition between two states. Designing the
operation before naming the states leaves the states to be discovered
one bug at a time, each arriving as a branch nobody planned.

## The moments this replaces

| About to… | Instead |
|---|---|
| add a branch for the case that just came up | name the state it belongs to; if the model has no name for it, the model is short a state, not a branch |
| write "X, except when Y" into a specification | write the states and the one state the operation must end in; the exception is usually a start state that was never listed |
| add `is_archived` beside `is_uploaded` and `is_locked` | replace the flag set with one enumeration of the states that can actually occur |
| write `can_do(kind, is_ready)` | split it: the property decides eligibility, the state decides availability, the call site combines them |
| carry a raw value inward and check it where it is used | reject it at the boundary it crossed, and let the type past the boundary say it was checked |
| return `null`, `-1` or log-and-continue on failure | return a value whose type carries the failure, so the caller cannot ignore it by accident |
| describe a feature as a sequence of steps | describe the state that counts as success first, then the steps that reach it from each start state |

## Name the states before the operation

For every operation, three things are written before any code: the
start states it can be called from, the one end state that counts as
success, and what happens from each start state that cannot reach it.
"Register a user by email" has three start states, no such user, an
active one, an inactive one, and one success state, an active user
with that email exists. Each start state gets a row, and the row says
whether it reaches the success state or fails and how.

Written that way, the operation has no exceptions, because every case
is a row. Written the other way round, as steps, the inactive user
arrives later as `if user.inactive:` in the middle of the function,
and the next overlooked state arrives the same way. A specification
with "except when" in it and a function with a branch per surprise
are the same defect in two notations.

The question that finds the missing state is not "what should the
code do here" but "what must be true when this is over". Product
requirements answer it as well as functions do: a feature whose
success state cannot be stated in one sentence is not specified yet.

## A state is not a property

A property is fixed for the life of the object: the file's format, the
user's role at creation, the currency of an account. A state changes
over time: uploaded or not, locked or not, active or not. They read
alike in a signature and behave nothing alike in a program. Logic on a
property needs no knowledge of any other process; logic on a state
depends on when it runs and on whoever else is writing that state.

`convertible(file.type)` is a property check, true or false forever.
`can_convert(file.type, file.is_uploaded)` looks like a small extension
and is a different kind of function: it now has a timing, a race with
the uploader, and a debugging scope that includes the queue. Keep the
two apart. The property check stays pure, the state check is named for
the state it reads, and the call site combines them, so whoever reads
the signature can see which half can change under them. Whether an
operation is *allowed* is always this composite, and the confusion
starts when it is treated as one thing.

## One enumeration, not a set of flags

Three booleans admit eight combinations; the program has perhaps four
real states. The other four are unreachable in theory and reached in
practice, because nothing stops a writer from setting two flags that
should never be true together. Every branch then tests combinations,
every test list grows as the product, and the fourth flag doubles both.

Replace the set with one enumeration whose members are the states that
can actually occur, and the impossible combinations stop existing. The
decision table in `test-design` shrinks with them: rules are counted
over states, not over bits.

## The boundary is where validation lives

A value that was not checked where it entered has to be checked
everywhere it is used, or trusted everywhere, and both happen in the
same codebase. Define the accepted range at the boundary, reject
outside it there, and let what passes carry a type that says so: a
`Email` that can only be constructed from a valid string, a
`PositiveInt` that was checked once. Inside the boundary nothing
re-checks and nothing assumes; the type is the record of the check.

Failure gets the same treatment. A function that can fail returns a
value that says so in its type, a `Result` or an `Either`, and the
caller has to take the failure apart to get at the success. `null`,
sentinel values and logged-and-swallowed exceptions all let the
failure travel as a success, and the breakage shows up wherever the
value is finally used, which is never where it went wrong.

## Hide the representation

A module that exposes its fields lets every caller depend on how it
happens to store things, and every caller then breaks when that
changes. Expose behaviour, inputs to outputs, and keep the fields
behind it; a caller who cannot reach the flag cannot set the
impossible combination either. Information hiding is the same rule as
the enumeration and the boundary type from the outside: the set of
states a caller can produce is exactly the set the module admits.

## How this connects

Working code is a state; not breaking is a structure that makes the
broken states unreachable. The Given of a test in `tdd-cycle` is a
state named here; the decision table and state table in `test-design`
are counted over the states named here; `assurance-case` writes the
same precondition and postcondition at system scale. When the states
cannot be listed, none of those can start, and that is the moment to
stop and list them.
