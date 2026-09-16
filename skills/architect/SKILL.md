---
name: architect
description: |
  Where a piece of code sits in a layered stack, triggered by the moments that misplace it: about to decide which project or folder a new type goes in, about to put a framework attribute or a network client on a domain type, about to let a view decide its own visibility or set a sibling's, about to add a lock, a delay or a retry so two screens stop colliding, about to resolve an analyzer warning by editing around the architecture, about to build a feature from the view inward, or about to review code for which layer each piece is in. The body is stack-neutral: what each layer is called and holds, the order a feature is built in, one arbiter for a screen's state, the checks before calling it done. What a language, framework or binary boundary spells differently is layered on from references/, read only for the stack in hand, today C# (.NET, MVVM, Avalonia, CQRS, DDD) and Go. Dependency direction is design-by-contract; the cut is slice-first; this skill says where the pieces sit.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Task
---

# Architect

## Core principles

### Clean Architecture layers

```
┌─────────────────────────────────────────┐
│         Presentation (MVVM)             │  ← ViewModels, Views
├─────────────────────────────────────────┤
│         Application (CQRS)              │  ← Commands, Queries, Handlers
├─────────────────────────────────────────┤
│         Domain (DDD)                    │  ← Entities, ValueObjects, Services
├─────────────────────────────────────────┤
│         Infrastructure                  │  ← Repositories, External Services
└─────────────────────────────────────────┘
```

**Dependencies run outward to inward.** Domain depends on nothing.

The picture names the layers;
it does not say whether the layer or the feature is the outer folder.
That is `slice-first`'s call,
and each stack layer shows the feature-cut layout beside the layered one.

These names are this stack's arrangement of one rule:
the layer nearer the policy declares the interface it needs and the layer nearer the machine implements it.
When the question is whether a dependency may point somewhere,
or whether a type has earned an interface at all,
that rule is in `design-by-contract`;
the picture above only says what the resulting pieces are called here.

### MVVM

- **View** — markup only.
  Code-behind kept to a minimum.
- **ViewModel** — exposes state for binding and commands for input.
- **Model** — the Domain layer's entities.

### Presentation: the screen has one arbiter

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
the first collision is patched with a lock, then a delay, then a retry,
and the symptoms are a screen that stops answering rapid keypresses,
a cancel key that has to be pressed twice,
and a popup that does not appear.
Those are three views of one missing arbiter.
Do not patch the collision; move the decision.

### CQRS

- **Command** — changes state.
  Returns nothing, or an identifier.
- **Query** — changes nothing.
  Returns a DTO.
- **Handler** — one responsibility, one operation each.

Cross-cutting concerns go in the pipeline the requests already pass through,
registered once, in order,
and that registration is the only place a reader can see what runs before a handler.
When the dispatch, the pipeline or the folder layout is the question,
the rule is in `slice-first` and `design-by-contract`;
the stack layer shows how the stack spells it.

### DDD

- **Entity** — has a unique identifier.
- **Value Object** — immutable, equal by value.
- **Aggregate Root** — the transaction boundary.
- **Domain Service** — business logic belonging to no single entity.
- **Repository** — defined per aggregate root, never below it.

### TDD

1. **Red** — write a failing test.
2. **Green** — the least code that passes it.
3. **Refactor** — improve, keeping the tests green.

## Stack layers

The rule is stack-neutral; what differs by language,
framework or binary boundary is layered on, not mixed in.
Read the layer for the stack in hand before placing or naming anything,
and no other:

- C#: `references/csharp.md` — the MVVM interfaces and the screen's arbiter,
  mediator dispatch and its pipeline, analyzer codes,
  the layered and the feature-cut layouts.
  It links onward to `references/csharp-architecture.md` (the layers in detail),
  `references/csharp-patterns.md` (implementation patterns) and `references/csharp-examples.md` (a complete feature),
  read only when the task reaches them.
- Go: `references/go.md` — the package as the slice,
  interfaces declared on the consuming side,
  middleware for the cross-cutting, what a slice may import.

A stack with no layer file uses the body alone.
A new language, a framework or a binary boundary (an ABI, an interop layer) is a new file under `references/`,
named here, holding only what differs from the body.

## By task

### Resolving a linter warning

1. Read the message exactly.
2. Find the cause, not the symptom.
3. Fix in line with the architecture, not around it.
4. Run the affected tests.

The stack layer lists the common codes and their fixes.

### Resolving a build error

1. Read the whole message.
2. Decide whether it is a dependency problem or a code problem.
3. Dependency — check the package and project references.
4. Code — check types, namespaces, access modifiers.
5. Confirm with a clean build.

### Refactoring

Before:

- [ ] Every existing test passes
- [ ] The purpose is clear
- [ ] The steps are small

The usual moves: extract method or class,
move to the layer it belongs in, introduce a value object,
replace a conditional with polymorphism.

After: run every test, and check no new warning appeared.

### Implementing a feature

1. **Clarify the requirement** — what is to be true afterwards,
   from each state it can start in (`state-first`).
2. **Locate the impact** — which layers change.
3. **Write the test first.**
4. **Start at the Domain** and work outward.
5. **Add an integration test.**

Order:

```
Domain Entity/VO → Domain Service → Repository interface
→ Application Command/Query → Handler
→ Infrastructure Repository → ViewModel → View
```

### Reviewing code

1. **Architecture** — do the dependencies run the right way,
   and is each piece in the layer it belongs to?
2. **DDD** — is the domain logic in the Domain layer,
   and are the aggregate boundaries right?
3. **CQRS** — are commands and queries separated,
   and does each handler do one thing?
4. **Tests** — is the coverage enough,
   and does each test name state its intent?
5. **Code** — does it follow SOLID, and is the naming clear?

## Before calling it done

- [ ] Every test passes
- [ ] No new warnings
- [ ] The build succeeds
- [ ] Dependencies run the right way
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
  issoh.co.jp/tech/details/10356, read 2026-09-17:
  the feature-cut layouts in C# and Go and the store interface declared on the slice's side.
  The rest of this skill rests on practice.
