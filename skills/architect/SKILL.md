---
name: architect
description: |
  Where a piece of code sits in a layered stack, triggered by the moments that misplace it: about to decide which project, package or folder a new type goes in, about to put a framework attribute or a client on a domain type, about to let a view decide its own visibility or set a sibling's, about to resolve an analyzer warning or a build error by editing around the architecture, about to refactor across layers, about to let an I/O callback write state directly, about to build a feature from the view inward, or about to review code for which layer each piece is in. The body is stack-neutral: what each layer holds and refuses, a pure core in a thin shell, one arbiter and one loop per screen, the build order and the checks before done. What a language, framework or binary boundary spells differently is layered on from references/, read only for the stack in hand, today C# (.NET, MVVM, Avalonia, CQRS, DDD) and Go. Dependency direction is design-by-contract's; the cut is slice-first's.
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
| let a receive callback, a timer or a file watcher write the state a screen shows | it posts a message to the one queue the arbiter reads; only the update changes state (below) |
| check a value's syntax and its business rule in the same place, or both checks in both places | the syntax is checked where the value enters, the rule where the domain type is made; each check has one home (below) |
| give a domain type a method that changes it in place, or hand the domain a clock or a repository | decide in a pure function that returns the new value or the events; the clock, the store and every port are the shell's (below) |
| build a feature from the view inward | start at the domain and work outward (below) |
| review by reading top to bottom | review layer by layer: dependency direction, domain logic in the domain, one operation per handler, tests that name their intent |

## The layers and what each holds

| Layer | Holds | Refuses |
|---|---|---|
| Presentation | views, and the presenters or view models that hold what a view shows | business rules, data access |
| Application | use cases: commands that change state, queries that read it, one handler each; the pipeline every request passes through | business rules, which are the domain's; knowledge of any adapter |
| Domain | immutable data: entities with identity, value objects equal by value, aggregates as transaction boundaries; the pure functions that decide and evolve them; the ports the shell must supply | any framework, any I/O, anything from the layers above |
| Infrastructure | the adapters that implement the ports: repositories, external services, the database context | rules |

Dependencies point inward; the domain depends on nothing.
Whether a dependency may cross a boundary,
and whether a type has earned an interface at all,
is `design-by-contract`'s.
Whether the layer or the feature is the outer folder is `slice-first`'s,
and each stack layer draws both layouts.

## A pure core in an effectful shell

Dependency direction has a sharper form.
The domain and the application's decisions are pure functions over immutable data:
the same input gives the same output,
and nothing outside the arguments is read or written.
Everything that touches the world sits in a thin shell around them:
the store, the wire, the file, the clock, randomness, a generated id.
The core takes values, not interfaces;
the current time arrives as an argument or inside a message,
and a port is something the shell holds and the core never calls.

A change of state is two functions and a starting value:

| Function | Takes | Returns |
|---|---|---|
| decide | a command and the current state | the events that happen, or the failure that stops them |
| evolve | a state and one event | the next state |

A handler is then three steps: the shell loads the state,
the core decides and evolves, the shell saves and publishes.
The loop's update below is the same shape,
with the next model as the new state and the commands as the effects it asks for,
so a screen and an aggregate are read the same way.
An aggregate that changes itself through methods and collects its own events is the object-oriented spelling of this,
and a stack layer that shows it says it is the alternative.

A failure the caller is expected to handle is a value:
a result type composed with `bind` and `map`, so the format check,
the invariant check and the decision read as one chain that stops at the first failure.
An exception is left for a precondition that was broken (`design-by-contract`).

The core is tested by tables of state, input and expected result,
and by properties that hold for every input; its tests need no mock,
and one that wants a mock has found I/O inside the core.
A fake appears only where the shell is tested.

## Two checks, two places

A value from outside passes two different checks,
and each has one place.

| Check | Asks | Where | On failure |
|---|---|---|---|
| Format | does it parse: a number where a number goes, a well-formed TOML file, a CSV row with its columns, a frame whose checksum matches | where the value enters: the adapter right after the read, the slice's entry right after the user typed | a failure message or result; nothing reaches the domain |
| Invariant | may it exist: a baud rate the port supports, a voltage inside the range, a pin map with no pin used twice | where the domain type is constructed or changed, through the one route that makes it | the type is not made; no invalid object is ever in memory |

The format check turns text into typed values and knows nothing of the business;
the invariant check knows the business and never sees text.
A rule written in both places drifts until the two disagree,
and a rule written in the adapter is skipped by the next adapter.
`state-first`'s "validation lives at the boundary" is the two together:
the boundary is where the value enters and where the type is made,
and past both nothing checks again.

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

## When input arrives from more than the user: one loop

A tool that talks to hardware,
sockets or files has more writers of its state than the user:
a receive task, a timeout, a file that changed on disk,
a write that finished.
Each one that changes the state directly is another owner of it,
and the arbiter above stops being the only one.
The loop that keeps a single owner has four parts:

| Part | Is | Refuses |
|---|---|---|
| Message | a fact that happened: the user pressed send, a packet arrived, a profile finished loading, a timeout fired | an instruction; a message says what happened, not what to do |
| Update | a pure function from the current state and one message to the next state and the effects it asks for | I/O, the clock, awaiting anything |
| Command | an effect the update asked for, carried out through an outbound port: send these bytes, write this batch, load this file | changing the state; its outcome comes back as a message |
| Subscription | an inbound adapter that turns a stream from outside into messages: a receive task, a file watcher, a scenario reader | changing the state; deciding anything |

Every message goes into one queue with one reader,
so the update sees them one at a time and in an order the log can show.
Inbound and outbound are separate adapters,
the receive side and the send side of the same port are two pieces,
because their failure, rate and ordering differ.
The domain under the update knows no file format and no wire:
the adapters convert a TOML file,
a CSV row or a frame into domain values before the message is posted.
The view renders from the state the loop publishes and posts what the user did;
it is the arbiter above with the I/O brought inside its rule.

A feature cut (`slice-first`) still holds: each slice owns its messages,
its part of the update and its view,
and the root update hands a message to the slice that declared it.
The loop is shared; the transitions are not.

## Implementing a feature

1. **Clarify the requirement** — what is to be true afterwards,
   from each state it can start in (`state-first`).
2. **Locate the layers that change.**
3. **Write the test first.**
4. **Start at the domain and work outward:** the data types and the functions that decide and evolve them,
   then the port the shell needs, then the use case and its handler,
   then the adapter, then the presenter and the view.
5. **Add an integration test.**

## Stack layers

The rule is stack-neutral; what differs by language,
framework or binary boundary is layered on, not mixed in.
Read the layer for the stack in hand before placing or naming anything,
and no other:

- C#: `references/csharp.md` — the MVVM interfaces and the screen's arbiter,
  the loop on a channel, mediator dispatch and its pipeline,
  analyzer codes, the refactoring moves,
  the layered and the feature-cut layouts.
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
- [ ] The core reads no clock, does no I/O and changes nothing in place;
  its tests use no mock
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
