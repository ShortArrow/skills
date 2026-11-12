---
name: slice-first
description: |
  Cutting a codebase along the axis it changes on, triggered by the moments that cut across it: about to add one feature by editing a controllers folder, a services folder and a repositories folder in turn, about to extract a base class or helper because two features' code looks alike, about to route a three-line read through every layer because the other features go that way, about to move a type into Shared or Common on its second use, about to organise tests by layer rather than by feature, about to repeat a cross-cutting check at the top of every handler, or about to put a mediator between one sender and one handler. Code that changes together belongs together, and duplication between features is the price of changing them independently. Use when adding a feature, when deciding where a new file goes, when two features start to resemble each other, and when a check has to hold for every request.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Slice first

A codebase is cut along some axis,
and the cut decides what a change costs.
Group by technical role and every feature is spread across every folder;
group by feature and a change stays where it was made.
The axis that matters is the one the code actually changes on.

## The moments this replaces

| About to… | Instead |
|---|---|
| add a feature by editing `controllers/`, `services/`, `repositories/` in turn | put the feature in one place, and let the layers live inside it |
| extract a base class because two features' handlers look alike | duplication between features buys independent change; wait until the two move together for the same reason |
| route a three-line read through the full stack | a slice may be as thin as its work; uniformity across slices is not a requirement |
| move a type into `Shared/` on its second use | what goes in shared binds every future feature; keep the copy until the shape has stopped moving |
| organise tests by layer | mirror the slices, so one feature's change touches one test folder |
| repeat the same validation at the top of every handler | put it in the pipeline, where a new handler cannot forget it |
| add a mediator between one sender and one handler | indirection earns its place from a second party, exactly as an interface does |
| name a folder for the pattern (`Handlers/`, `Dtos/`) | name it for the feature; the pattern is visible in the file |

## The axis of change

Cohesion is not "things that look alike".
It is things that change for the same reason, at the same time,
in the same commit.
A price rule changes with the pricing feature,
not with the other classes that happen to be repositories.

The layered arrangement optimises for a change that arrives per layer:
swap the database, change every controller's error format.
Those changes are real and rare.
The change that arrives every week is a feature,
and under layering it lands as a diff across four folders where nothing but the reviewer's memory says the four pieces are one thought.
Under a feature cut, the same change is one folder,
and what is not in that folder is evidence the feature does not depend on it.

This is not an argument against layers.
It is an argument about which one is the outer grouping:
layers inside a feature keep their meaning,
features inside layers lose theirs.

## Duplication between slices is a price, not a defect

Two slices with similar code are not yet a shared abstraction.
They are two places that happen to agree today,
and the shared base class extracted now becomes the reason one of them cannot change tomorrow — the second slice's requirement arrives as a flag on the base,
then a second flag, then a subclass nobody can name.

Extract when the two have shown they change together for the same reason.
Until then, the copy is cheaper than the coupling,
and it says something true: these features are independent.
The test is not how similar the code looks;
it is whether a change to one is a change to both.

`Shared/`, `Common/` and `Core/` are where this fails quietly,
because nothing rejects an addition.
A type placed there is a contract with every feature written afterwards,
so it takes the same scrutiny as any published surface:
`design-by-contract` decides whether the abstraction is earned,
and `library-design` covers what freezes once a second consumer exists.

## A slice is as thick as its work

Enforcing the same shape on every feature is the layered instinct in new clothes.
A read of one row by id does not need a repository,
a service and a mapper to be a legitimate slice;
it needs a query and a result.
A feature with a real invariant to protect gets the whole apparatus,
in its own folder, where nobody else pays for it.

Judge a slice by whether its own contract holds,
not by whether it resembles its neighbours.

## Cross-cutting checks belong in the pipeline

Validation, authorisation, transactions, logging, idempotency:
each has to hold for every request,
which is exactly what a rule repeated at the top of every handler cannot guarantee.
The handler written next week omits it, and nothing fails.

Put it in the pipeline the requests already pass through,
so the check binds by construction rather than by memory.
What belongs there is what every request needs regardless of which feature it is:
who may call, that it is logged, that it runs in a transaction,
that the input is well-formed.
A rule that exists because of one feature,
that an order must exist before it is cancelled,
is that feature's however general it sounds.
This is the same argument `agent-harness` makes for gates over prose,
applied inside the program:
a convention that has to be remembered is a convention that decays.

Two limits, and they are what keep the pipeline honest:

- **A rule that applies to one request is that request's.** Business logic in a behaviour is a feature smeared across the machinery,
  findable by nobody reading the feature.
- **The pipeline must be traceable.** A reader who cannot tell what runs before a handler has bought the forgetting they were trying to prevent.
  One list, in order, in one place.

## When the cut is wrong

The feature cut pays when features keep arriving and several people change different ones at once.
It does not pay for an application of a dozen endpoints that will not grow,
where the folders cost more than the cross-folder diff they prevent.
And it does not pay where several features share one complex rule,
a premium calculation, an allocation of stock,
that is edited in every copy every time: that rule is one thing,
and cutting it into slices turns one change into several.
Sameness that is coincidental stays duplicated.
A rule that has changed in every copy for the same reason,
and never in one alone,
is shared domain knowledge and moves to one place;
until it has that history, it is a copy.

Moving a layered codebase is not a rewrite.
Add the feature folder, write the next feature as a slice,
leave the layers where they are,
and watch whether the files a change touches stay inside the feature folder.
When they do for every new feature, the migration is done;
a change that still reaches into the old layers names the next thing to move.

## The mediator has to earn its keep

Dispatching a request through a mediator is often adopted as decoupling and delivers none:
one sender, one handler,
and an indirection that breaks go-to-definition for every reader after you.
That is the one-implementation interface `design-by-contract` refuses,
wearing a different name.

It earns its place when something real passes through the dispatch:
the pipeline above, several handlers for one notification,
a boundary where the sender genuinely must not know the handler.
Absent those, call the handler.

## How this connects

`tidy-first` keeps the move that reshapes a folder out of the commit that changes behaviour,
which is how a cut is changed safely.
`design-by-contract` decides whether a shared type or an interface has earned its existence,
and the pipeline's checks are preconditions stated once.
`state-first` names the states a slice's feature moves between.
Where the arrangement has to be expressed in a particular stack's project layout,
that placement is `architect`,
whose stack layers spell it per language.

## Sources

- 株式会社一創, 「Vertical Slice Architecture」,
  issoh.co.jp/tech/details/10356,
  published 2025-12-22 and read 2026-09-17:
  the cases where the cut does not pay,
  and migration judged by whether a change's files stay under the feature folder.
  The feature-cut layouts are drawn in `architect`'s stack layers.
  The rest of this skill rests on practice.
