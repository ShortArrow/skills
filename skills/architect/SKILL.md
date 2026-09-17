---
name: architect
description: |
  Where a piece of code sits in a layered stack, triggered by the moments that misplace it: about to decide which project, package or folder a new type goes in, about to put a framework attribute or a network client on a domain type, about to let a view decide its own visibility or set a sibling's, about to resolve an analyzer warning or a build error by editing around the architecture, about to refactor across layers, about to build a feature from the view inward, or about to review code for which layer each piece is in. The body is stack-neutral: what each layer is called, holds and refuses, one arbiter for a screen's state, the order a feature is built in, and the checks before calling it done. What a language, framework or binary boundary spells differently is layered on from references/, read only for the stack in hand, today C# (.NET, MVVM, Avalonia, CQRS, DDD) and Go. Dependency direction is design-by-contract; the cut is slice-first; this skill says where the pieces sit.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Task
---

# Architect

A codebase arranged in layers has one rule and many spellings.
The rule is that the layer nearer the policy declares what it needs and the layer nearer the machine supplies it.
The spellings are what the layers are called,
which project or package holds each, and how the files are named,
and those differ by language and framework.
This body holds the rule and the names;
the stack layer holds the spelling.

## The moments this replaces

| About to… | Instead |
|---|---|
| decide which project, package or folder a new type goes in | name what the type knows: nothing outside the domain, the domain only, a port, or the world. That is its layer; the stack layer names the folder |
| put a framework attribute, an HTTP client or a clock on a domain type | the domain declares a port for it and an outer layer implements it; the type stays plain |
| let a view decide its own visibility or set a sibling's | the view reports and draws; one arbiter above it decides (below) |
| resolve an analyzer warning or a build error by editing around the architecture | read the whole message, find the layer the fix belongs to, fix it there, run the affected tests |
| refactor across layers | one move at a time with the tests green between moves (`tidy-first`); the stack layer lists the usual moves |
| build a feature from the view inward | start at the domain and work outward (below) |
| review by reading top to bottom | review layer by layer: dependency direction, domain logic in the domain, one operation per handler, tests that name their intent |

## The layers and what each holds

| Layer | Holds | Refuses |
|---|---|---|
| Presentation | views, and the presenters or view models that hold what a view shows | business rules, data access |
| Application | use cases: commands that change state, queries that read it, one handler each; the pipeline every request passes through | business rules, which are the domain's; knowledge of any adapter |
| Domain | entities with identity, value objects equal by value, aggregates as transaction boundaries, domain services for rules that belong to no single entity, the ports the domain needs | any framework, any I/O, anything from the layers above |
| Infrastructure | the adapters that implement the ports: repositories, external services, the database context | rules |

Dependencies point inward; the domain depends on nothing.
Whether a dependency may cross a boundary,
and whether a type has earned an interface at all,
is `design-by-contract`'s.
Whether the layer or the feature is the outer folder is `slice-first`'s,
and each stack layer draws both layouts.

## Presentation: the screen has one arbiter

A view draws what it is told and reports what the user did;
it decides nothing.
Which screen is visible, which input is accepted now,
and what a second keypress means while the first is still being handled are decided in one place:
an arbiter that holds the screen's state as one state machine (`state-first`),
with every view's presenter under it in a tree that has a single root.
An event a presenter cannot settle goes up the tree until one can;
nothing goes sideways to a sibling.

The failure this replaces is the one generated GUI code drifts into,
because desktop and game interface conventions are thin in what a model has read:
each screen shows and hides itself and reaches into its neighbours,
and the symptoms are a screen that stops answering rapid keypresses,
a close key that has to be pressed again,
and a popup that does not appear.
Those are three views of one missing arbiter.
The lock, the delay and the retry that get added after the first collision are `state-first`'s moment;
this skill says where the arbiter sits.

## Implementing a feature

1. **Clarify the requirement** — what is to be true afterwards,
   from each state it can start in (`state-first`).
2. **Locate the layers that change.**
3. **Write the test first.**
4. **Start at the domain and work outward:** the entities and rules,
   then the port they need, then the use case and its handler,
   then the adapter, then the presenter and the view.
5. **Add an integration test.**

## Stack layers

The rule is stack-neutral; what differs by language,
framework or binary boundary is layered on, not mixed in.
Read the layer for the stack in hand before placing or naming anything,
and no other:

- C#: `references/csharp.md` — the MVVM interfaces and the screen's arbiter,
  mediator dispatch and its pipeline, analyzer codes,
  the refactoring moves, the layered and the feature-cut layouts.
  It links onward to `references/csharp-architecture.md` (the layers in detail),
  `references/csharp-patterns.md` (implementation patterns) and `references/csharp-examples.md` (a complete feature),
  read only when the task reaches them.
- Go: `references/go.md` — the package as the unit,
  interfaces declared on the consuming side,
  middleware for the cross-cutting,
  what a package may import and the command that checks it.

A stack with no layer file uses the body alone.
A new language, a framework or a binary boundary (an ABI, an interop layer) is a new file under `references/`,
named here, holding only what differs from the body.

## Before calling it done

- [ ] Every test passes
- [ ] No new warnings
- [ ] The build succeeds
- [ ] Dependencies point inward
- [ ] Naming follows the stack layer's conventions
- [ ] Everything sits in the layer it belongs to

## Sources

- nrs, 「バイブコーディングで GUI が壊れていく理由とその対策プロンプト」,
  zenn.dev/nrs/articles/9ba91aea587bf5,
  published 2026-09-15 and read 2026-09-17: the passive view,
  the presenter tree with one root, events bubbling upward,
  the mediator that is a state machine,
  and the three symptoms of screens that decide for themselves.
- 株式会社一創, 「Vertical Slice Architecture」,
  issoh.co.jp/tech/details/10356,
  published 2025-12-22 and read 2026-09-17:
  the shape of the feature-cut layout in C# and the store interface declared on the slice's side in Go;
  the layer files say where they follow it.
  The rest of this skill rests on practice.
