# Pinned senses

The quotations behind the table under One sense per term in `SKILL.md`,
with the source of each and the date it was read.
A row of that table is this catalogue's criterion,
written so it can be answered yes or no;
the quotation is what the criterion rests on.
Where a row says more than its quotation, this file says so.

## The rows

**Refactoring.** "a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior",
and as a verb, "to restructure software by applying a series of refactorings without changing its observable behavior".
The row keeps the last clause.

**Continuous integration.** "each member of a team merges their changes into a codebase together with their colleagues changes at least daily. Each of these integrations is verified by an automated build (including test) to detect integration errors as quickly as possible." A build server over branches that live for weeks fails the first half of the row.

**Technical debt.** "Shipping first time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite. […] Every minute spent on not-quite-right code counts as interest on that debt." The source describes a loan:
something was gained by shipping, and a rewrite repays it.
That code which is merely poor, with nothing gained in exchange,
is not debt is this catalogue's reading of the passage;
the passage does not say it in those words.

**REST.** "if the engine of application state (and hence the API) is not being driven by hypertext, then it cannot be RESTful and cannot be a REST API." And,
from the same post: "A REST API should be entered with no prior knowledge beyond the initial URI (bookmark) and set of standardized media types".
JSON over HTTP with URLs the client builds from documentation fails the row.

**Minimum viable product.** "the minimum viable product is that version of a new product which allows a team to collect the maximum amount of validated learning about customers with the least effort." And:
"MVP, despite the name, is not about creating minimal products." The row pins the sense of this post.
Whether the words appeared earlier elsewhere was not checked.

## Adding a row

A term is pinned when its two senses coexist,
so that one sentence is read both ways.
A term whose looser sense has replaced the source's is left alone.

The criterion is read in a source anyone can open,
and it has to be answerable yes or no.
A source that states a preference gives no criterion.
"Microservices prefer letting each service manage its own database" (Lewis and Fowler, 2014) is why microservices has no row:
services that share a database depart from what the article describes,
and the article does not say they stop being microservices.

Where the source is a paid book,
the row says the criterion is practice and names no source,
as `docs/design-intent.md` decides for every rule here.

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
