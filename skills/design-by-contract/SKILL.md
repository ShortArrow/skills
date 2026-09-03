---
name: design-by-contract
description: |
  Obligations at an interface, triggered by the moments that blur who owes what: about to guard against a condition the caller was already required to satisfy, about to check the same argument on both sides of a call, about to return false or null where the contract was violated rather than unmet, about to declare an interface for a type that has one implementation, about to put an interface in the package that implements it, about to strengthen a precondition or weaken a postcondition in an override, or about to write a rule into prose that the type could have carried. A precondition is the caller's debt and a postcondition the callee's, and a condition defended on both sides belongs to neither. Use when writing or reviewing a function signature, when deciding whether something deserves an interface, when a null check is about to be added, and when a docstring is about to say "must not".
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Design by contract

A call is an agreement. The caller guarantees the precondition, the
callee guarantees the postcondition, and the type guarantees its
invariant between calls. Everything below follows from asking, for
each condition, **whose obligation is it** — because a condition
nobody owns is checked twice and relied on never.

## The moments this replaces

| About to… | Instead |
|---|---|
| guard against a state the caller was required to avoid | let it fail loudly at the boundary of the contract; a defensive branch turns a caller's bug into your silent behaviour |
| validate the same argument in caller and callee | pick the owner: validated at the boundary and passed as a checked type, or required and stated as a precondition |
| return `false`, `null` or `-1` on a violated precondition | distinguish the two failures: a contract violation is a bug and throws, an expected failure is a value the type carries |
| write `IThing` for the only `Thing` | let a second implementation or a boundary that has to be faked justify it; one implementation behind an interface is two names for one thing |
| put the interface next to its implementation | the consumer declares the interface it needs, so the dependency points at the abstraction and not at the provider |
| strengthen a precondition in an override | a subtype may demand less and deliver more, never the reverse; the caller holds the base contract |
| write "must not be empty" in a docstring | make the type refuse empty, and keep prose for what no type can say |
| add a case to an interface for one caller | ask whether that caller needs its own interface; a widened contract binds every implementor |

## Whose obligation is it

For each condition at a boundary, exactly one side owns it.

- **Precondition** — the caller's debt. The callee may assume it and
  does not check it for correctness. If it does check, that check
  exists to report the caller's bug, not to continue past it.
- **Postcondition** — the callee's debt, owed only when the
  precondition held. "Returns a user, or null if the id was
  malformed" is two contracts wearing one signature.
- **Invariant** — the type's debt, true between every pair of calls.
  It is the reason a constructor may reject and a setter may not
  exist.

The failure of this discipline has a shape: every function checks
every argument, no function documents what it requires, and the same
condition is enforced in five places and understood in none. Removing
one of those checks then feels dangerous, because nobody can say who
was relying on it.

## Violation is not failure

Two things can go wrong at a call and they are not the same:

- **A violated contract is a bug.** The caller passed a negative
  quantity, the object was used after disposal, the id was never
  looked up. Crash, assert, throw a defect exception. Recovering from
  it means shipping a program that no longer knows what is true.
- **An unmet expectation is a result.** The file did not exist, the
  server timed out, the credentials were rejected. This is ordinary
  business, and it belongs in the return type where the caller cannot
  step over it: a `Result`, an `Option`, a sum type. `state-first`
  covers the shape.

Merging them produces the worst of both: the bug is swallowed as a
`false`, and the expected failure is thrown as an exception nobody
catches at the right level.

## Push the contract into the type

A contract stated in prose is enforced by whoever remembers it. A
contract stated in a type is enforced by the compiler on every future
call, including the ones written by someone who never read the
docstring.

| Prose | Type |
|---|---|
| "must not be null" | a non-nullable parameter |
| "must be a valid email" | an `Email` constructible only from a valid string |
| "must be positive" | `PositiveInt`, or an unsigned type |
| "call `open` before `read`" | `read` exists only on the type `open` returns |
| "the list must not be empty" | a non-empty list type, or a first element plus a rest |

What survives in prose is what no type can carry: complexity
guarantees, thread affinity, the meaning of a domain rule, the
deliberate why-not. Those belong in the docstring, which is where
`clean-docs` puts the interface contract.

An assertion is the middle ground. It states a precondition the type
cannot, in a form that fails at the moment of violation rather than
three frames later — and, unlike a defensive branch, it does not
invent a behaviour for the broken case.

## An interface is a contract with more than one party

The point of separating interface from implementation is not
tidiness; it is that the abstraction can be depended on while the
implementation changes. That value appears only when something else
can occupy the same contract.

**An interface earns its existence from one of three things:** a
second implementation that exists today, a boundary that has to be
replaced in a test or another environment, or a published surface
whose implementations are written by other people. A type with one
implementation, one consumer and no boundary is fully described by
itself, and wrapping it adds a name, a file and an indirection that
must be followed on every read.

**The consumer owns the abstraction.** The interface belongs where it
is needed, expressed in the vocabulary of the code that needs it, not
in the package that happens to implement it today. That is what makes
the dependency point at the abstraction, and it is the whole content
of dependency inversion: the layer nearer the policy declares what it
requires, and the layer nearer the machine implements it. Layer names
are one way to arrange this; the obligation is the rule underneath.

Keep the contract narrow for the same reason. Every method on the
interface is a promise every implementor must keep, so a method added
for one caller is paid for by all of them. The interface that fits one
caller exactly and is implemented twice is worth more than the
interface that fits everyone approximately.

## Substitutability is the contract holding under replacement

A subtype is usable wherever the base type is, which is a statement
about contracts and not about inheritance syntax: a subtype may
**require less** and **deliver more**, never the reverse. An override
that strengthens a precondition (rejects an input the base accepted)
or weakens a postcondition (returns less than the base promised)
breaks callers that were written against the base and never mention
the subtype.

The same rule polices interface changes over time. Tightening what an
implementation accepts, or loosening what it returns, breaks callers
who never changed. When the interface is published, `library-design`
governs what that costs.

## How this connects

The precondition is the Given of a test and the boundary its edge —
`test-design` derives cases from exactly these conditions, and the
value one past the boundary is where the contract stops. `state-first`
names the states a precondition talks about and carries failure in the
return type. `assurance-case` writes the same `{P} C {Q}` at system
scale, where an unstated assumption is a precondition the caller
cannot see. When the interface is a package's public surface,
`library-design` covers what freezes at first use.
