---
name: csharp-architect
description: |
  C# development under MVVM, Clean Architecture, TDD, CQRS and DDD. Use when resolving a linter warning or a build error, refactoring, implementing a feature, or reviewing code — anywhere the question is which layer something belongs in and which way the dependency runs.
  Triggers: C#, .NET, MVVM, Clean Architecture, DDD, CQRS, TDD, refactoring, code review
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Task
---

# C# Architect

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

### MVVM

- **View** — XAML or Razor only. Code-behind kept to a minimum.
- **ViewModel** — implements `INotifyPropertyChanged` and `ICommand`.
- **Model** — the Domain layer's entities.

### CQRS

- **Command** — changes state. Returns nothing, or an identifier.
- **Query** — changes nothing. Returns a DTO.
- **Handler** — one responsibility, one operation each.

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

## By task

### Resolving a linter warning

1. Read the message exactly.
2. Find the cause, not the symptom.
3. Fix in line with the architecture, not around it.
4. Run the affected tests.

Common ones:

- `CA1062` — add the null check, or adopt nullable reference types
- `CA1822` — make it static if it touches no instance state
- `CS8618` — enable nullable reference types, or guarantee initialisation

### Resolving a build error

1. Read the whole message.
2. Decide whether it is a dependency problem or a code problem.
3. Dependency — check the NuGet and project references.
4. Code — check types, namespaces, access modifiers.
5. Confirm with a clean build.

### Refactoring

Before:

- [ ] Every existing test passes
- [ ] The purpose is clear
- [ ] The steps are small

The usual moves: extract method or class, move to the layer it belongs
in, introduce a value object, replace a conditional with polymorphism.

After: run every test, and check no new warning appeared.

### Implementing a feature

1. **Clarify the requirement** — what is to be true afterwards.
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

1. **Architecture** — do the dependencies run the right way, and is each
   piece in the layer it belongs to?
2. **DDD** — is the domain logic in the Domain layer, and are the
   aggregate boundaries right?
3. **CQRS** — are commands and queries separated, and does each handler do
   one thing?
4. **Tests** — is the coverage enough, and does each test name state its
   intent?
5. **Code** — does it follow SOLID, and is the naming clear?

## File naming

```
Domain/
  Entities/          {Name}.cs
  ValueObjects/      {Name}.cs
  Services/          {Name}Service.cs
  Events/            {Name}Event.cs

Application/
  Commands/          {Action}{Entity}Command.cs
  Queries/           Get{Entity}Query.cs
  Handlers/          {Command/Query}Handler.cs
  DTOs/              {Name}Dto.cs

Infrastructure/
  Repositories/      {Entity}Repository.cs
  Services/          {External}Service.cs

Presentation/
  ViewModels/        {View}ViewModel.cs
  Views/             {Name}View.xaml
```

## Further reading

- [architecture.md](./architecture.md) — the layers in detail
- [patterns.md](./patterns.md) — implementation patterns
- [examples.md](./examples.md) — code

## Before calling it done

- [ ] Every test passes
- [ ] No new warnings
- [ ] The build succeeds
- [ ] Dependencies run the right way
- [ ] Naming follows the conventions
- [ ] Everything sits in the layer it belongs to
