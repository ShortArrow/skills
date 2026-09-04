---
name: library-design
description: |
  Designing a library — a published package, or an in-app module from the moment it has a second consumer. The implementation stays editable forever, while the public API, the dependency set, the performance characteristics and every observable behaviour freeze at first external use (Hyrum's law). Five duties to the caller: take no control, add no hidden cost (zero-cost abstraction as the bar), hold no hidden state, hide no failure, block no escape. Use when designing or reviewing a public API, when extracting shared code into a module, when asked to "make this reusable", when a signature-compatible change alters an observable behaviour, and when an application is being shaped around a framework's types and lifecycle.
---

# The Library Contract

An application is judged by its users; a library is judged by
programmers, and at a specific moment — when they want something the
author did not imagine. A good library is not one that is convenient
when used as intended. It is one that does not have to be discarded
when used otherwise.

Every rule below follows from one asymmetry. Inside the library you
may change anything, forever. Outside it, whatever a caller can
observe is frozen the first time someone depends on it — and with
enough callers, someone depends on all of it.

## What freezes, and when

Hyrum's law is the operating condition, not a curiosity: given enough
users, every observable behaviour becomes load-bearing — exception
wording, enumeration order, log output, timing, even behaviour you
documented as undefined. "It was never in the contract" does not
un-break the caller who shipped against it.

So the freeze line sits at observability, not at the `public` keyword,
and three consequences follow:

- **The surface starts small.** A symbol, once public, is a promise
  you can widen but never quietly withdraw. "Public for now" is debt
  taken on for no benefit; expose on demand.
- **Formats outlive code.** A file format, a network protocol, a
  persisted schema survives every rewrite of the library around it.
  Serializing the internal struct as-is welds the frozen layer to the
  editable one.
- **An in-app module crosses this line at its second consumer**, not
  at packaging. The moment two callers exist, its API has the same
  freeze economics as a published package — only the blast radius is
  smaller.

Semantic Versioning is the public spelling of the same line, and it
starts by refusing to work without one: "Software using Semantic
Versioning MUST declare a public API" (SemVer 2.0.0, clause 1). Once
declared, the increments are decided rather than felt — a backward
incompatible change to that API MUST raise MAJOR (clause 8), new
backward compatible functionality MUST raise MINOR (clause 7), a
backward compatible fix MUST raise PATCH (clause 6). Hyrum's law is
what makes the declaration hard: the spec freezes what you declared,
and callers freeze what they observed.

The spec also has a name for the module that has not crossed the line
yet. "Major version zero (0.y.z) is for initial development. Anything
MAY change at any time" (clause 4). That is the honest label for a
module with one consumer, and the day it gains a second is the day
1.0.0 is owed, not the day it is packaged.

## Take no control

Separate mechanism from policy. Performing an HTTP request is
mechanism; retrying it three times with exponential backoff is policy,
and policy baked into the core narrows the library to callers who
share it. Ship convenient defaults for logging, threading, retries,
timeouts, caching, serialization — and make every one of them
replaceable.

The application role is singular, and it is not yours. Exiting the
process, writing to stdout, trapping SIGINT, installing top-level
exception handlers, resizing the thread pool: exactly one component
per process may do these, and a library that does them fights the
component entitled to.

Magic — auto-detection, auto-conversion, auto-reconnect, auto-cache —
is admissible only while the caller can reconstruct why it did what it
did. Convenience the user cannot debug is control taken, not work
saved.

## Add no hidden cost

When things happen belongs to the caller. An import that starts a
thread, a constructor that opens a connection, a static initializer
that reads environment variables — each moves real work to a moment
the caller never chose and cannot move back.

A dependency is part of your API. Its runtime, its update cadence,
its ABI stability, its licence, its own initialization side effects
all transfer to every caller; you are choosing on their behalf.

Performance characteristics are contract. Turning an O(1) lookup into
O(n) — or doubling allocations and copies — is a breaking change
wearing a compatible signature, and callers discover it in production.

Where input arrives faster than it leaves — streams, events, logs,
queues — an unbounded internal buffer is a memory leak on a delay.
Backpressure is part of the design, not an operational detail.

The bar for the abstraction itself is zero-cost, in both of
Stroustrup's clauses. What the caller does not use, they do not pay
for: the convenience storey must not tax the primitive one with its
allocations, its dispatch, or its setup. And what they do use, they
could not reasonably write better by hand: an abstraction beaten by
hand-rolled code gets bypassed, and a bypassed library is a discarded
one wearing a version number.

## Hold no hidden state

Singletons, static caches, global event loops, process-wide
configuration: each works while yours is the only library in the
process, and collides the moment a second library, a plugin host, or
a parallel test suite shares it. State lives in an instance the
caller creates, owns, and can create twice.

## Hide no failure

The API shape declares what can happen and who is responsible.
Errors, cancellation, timeout, partial success, absence — modelled in
the types, not routed through "this never normally happens" and an
exception. The same shape carries the ownership answers a comment
cannot enforce: who closes the stream, whether the buffer may be
reused, which thread the callback arrives on.

Keep the cause. Collapsing failure into `false` or `null` strips
exactly the information the layer above needed to decide; logging it
yourself and continuing loses the same information and takes the
caller's logging policy with it.

Quality separates on the abnormal path. On the happy path libraries
are interchangeable; timeout, reconnection, mid-stream disconnect,
partial reads, corrupt data and retry are where the differences live,
so design for their composition first.

Cancellation retrofits badly — a cancellation token threads through
every signature it touches. I/O and long-running operations accept it
from the first version.

## Block no escape

Build two storeys. A high-level API that serves the common case in
one line, resting on public primitives — `ReadAsync()` over
`ReadAsync(Memory<byte>)` — so the caller whose requirement falls
outside the top storey climbs down instead of leaving. A library with
only the high storey is discarded at the first requirement it did not
anticipate.

Observability is injected, not owned: loggers, metrics, traces plug
into the caller's stack. A diagnostic format only your library reads
is telemetry taken hostage.

## One tax, two currencies

This skill and Clean Architecture are the same refusal in two
currencies. Zero-cost abstraction refuses the tax on runtime
performance; the Dependency Rule refuses the tax on changeability. In
both, an abstraction is judged by what it makes the dependent side
give up.

| Duty here | Its architectural name |
|---|---|
| Mechanism separate from policy | Use case kept apart from framework and driver |
| Defaults replaceable | Dependency inversion — the stable side picks the implementation |
| Primitives under the convenience storey | Outer details swappable |
| No global state | Dependencies explicit, so a boundary can be drawn |
| A dependency is part of your API | The Dependency Rule |

The caller's healthy shape puts your library at the bottom: a
replaceable detail beneath their policy and domain. The inverted
shape — the application living inside a framework, dragging its
lifecycle, its types, its DI, its error model, its async model — is
the library acting as the application, written at architecture scale.

The general form: good architecture minimizes not the number of
dependencies but the freedom each dependency takes away.

## The sentence

An abstraction in a library exists to widen the caller's choices. The
moment it takes performance, control, or information in exchange, it
has stopped abstracting and started deciding.

## When not to apply

A module with one consumer, one repo, one team has not crossed the
freeze line — it is at 0.y.z in SemVer's terms, whether or not it
carries a number — and building every replaceable-policy seam for it
is speculation with a maintenance bill. Keep the disciplines that cost
nothing from day one — no global state, failures that keep their
cause, no work before the caller asks — and add the seams when the
second consumer arrives, which is the moment they stop being
speculative.

## Sources

- Semantic Versioning 2.0.0, semver.org: clause 1 (public API MUST
  be declared), clauses 6–8 (PATCH, MINOR, MAJOR increments), clause 4
  (0.y.z), and the FAQ entry on deprecation (document it, then issue a
  minor release with the deprecation in place). Wording checked against
  the page on 2026-09-04.
- Hyrum's law is an observation, not a standard, and is cited as one.
