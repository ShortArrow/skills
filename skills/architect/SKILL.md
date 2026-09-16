---
name: architect
description: |
  Where a piece of code sits in a layered stack: what each layer is called, what it holds and refuses, the order a feature is built in, and the checks before calling it done. Use when resolving a linter warning or a build error, refactoring, implementing a feature, or reviewing code in a solution arranged as MVVM, Clean Architecture, CQRS and DDD. The body is stack-neutral; what differs by language, framework or binary boundary is layered on from references/ and read only for the stack in hand — today C# (.NET, MVVM, Avalonia, CQRS with a mediator, DDD, analyzer codes). Which way a dependency runs, and who owes what at an interface, is `design-by-contract`; how the code is cut is `slice-first`; this skill only says where the pieces sit.
  Triggers: C#, .NET, MVVM, Clean Architecture, DDD, CQRS, TDD, refactoring, code review
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

- C#: `references/csharp.md` — the MVVM interfaces,
  mediator dispatch and its pipeline, analyzer codes, file naming.
  It links onward to `references/csharp-architecture.md` (the layers in detail),
  `references/csharp-patterns.md` (implementation patterns) and `references/csharp-examples.md` (a complete feature),
  read only when the task reaches them.

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
