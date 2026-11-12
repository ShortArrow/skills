# Pinned senses

The quotation each row under One sense per term in `SKILL.md` rests on,
with notes on how the row reads it.

## The rows

**Refactoring.**

> a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior

The row keeps the last clause.

**Continuous integration.**

> each member of a team merges their changes into a codebase together with their colleagues changes at least daily.
> Each of these integrations is verified by an automated build (including test) to detect integration errors as quickly as possible.

**Technical debt.**

> Shipping first time code is like going into debt.
> A little debt speeds development so long as it is paid back promptly with a rewrite.
> […] Every minute spent on not-quite-right code counts as interest on that debt.

The passage describes a loan: shipping sooner is what was borrowed.
This catalogue's reading, not the passage's words:
poor code with nothing gained in exchange is not debt.

**REST.**

> if the engine of application state (and hence the API) is not being driven by hypertext,
> then it cannot be RESTful and cannot be a REST API.

> A REST API should be entered with no prior knowledge beyond the initial URI (bookmark) and set of standardized media types

JSON over HTTP with URLs the client builds from documentation fails the row.

**Minimum viable product.**

> the minimum viable product is that version of a new product which allows a team to collect the maximum amount of validated learning about customers with the least effort.

> MVP, despite the name, is not about creating minimal products.

Whether the phrase predates this post was not checked.

## Adding a row

A row needs three things: two coexisting senses,
so that one sentence is read both ways; a source anyone can open;
and a criterion in that source answered yes or no.
Microservices fails the third.
"Microservices prefer letting each service manage its own database" (Lewis and Fowler) states a preference,
and the article does not say that services sharing a database stop being microservices.
`docs/design-intent.md` carries the reasons.

## Sources

Each was fetched and the quoted strings matched against the page text on 2026-09-18.

- Martin Fowler, "DefinitionOfRefactoring", 1 September 2004,
  martinfowler.com/bliki/DefinitionOfRefactoring.html.
- Martin Fowler, "Continuous Integration", revised 18 January 2024,
  martinfowler.com/articles/continuousIntegration.html.
- Ward Cunningham, "The WyCash Portfolio Management System",
  OOPSLA '92 experience report, 1992, c2.com/doc/oopsla92.html.
- Roy T. Fielding, "REST APIs must be hypertext-driven", 20 October 2008,
  roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven.
- Eric Ries, "Minimum Viable Product: a guide", 3 August 2009,
  startuplessonslearned.com/2009/08/minimum-viable-product-guide.html.
- James Lewis and Martin Fowler, "Microservices", 25 March 2014,
  martinfowler.com/articles/microservices.html.
  Read for the sentence quoted under Adding a row.
