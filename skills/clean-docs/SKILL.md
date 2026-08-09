---
name: clean-docs
description: Discipline for writing durable artifacts — PR bodies, commits, CHANGELOGs, ADRs, READMEs, PRDs, specifications, source code. (1) Never carry a label that only means something inside the conversation. (2) The artifact answers the reader, not the reviewer: deleting a wrong sentence needs no replacement, a non-relationship is not worth explaining, and a document that vouches for itself is padding. (3) Derivation orders documents — what is derived is more volatile than its source; a specification derivation (use case, requirement, design, test plan) must keep following its source, a record derivation (ADR, CHANGELOG, PR, test run) freezes at its moment — so references run more-derived to less-derived only: no ADR numbers pointing out of a living document, no mutual links, no former behaviour in the body, undecided items separated out, and an ADR that records reasoning rather than narrative. (4) Living documents belong together under the docs root. Use when writing a PR, a commit, a CHANGELOG, an ADR or an issue, when editing a README or PRD, when fixing something a reviewer called wrong, and whenever you are about to write "See ADR-NNNN".
---

# Self-Contained Artifacts

A durable artifact is **read after this conversation has ceased to exist,
by someone who never saw it**. And a set of documents has an architecture
— layers, and a direction of dependency — as surely as the implementation
does. That is the whole of this skill.

## Discipline 1: conversation labels stay in the conversation

A label is conversation-local when its definition exists nowhere but the
conversation. Severity codes coined while triaging, names given to options
while comparing them, positional references, a nickname for a task — each
works while both parties hold the context, and none survives losing it.

**The test is not the shape of the label. It is whether a reader holding
only the artifact can find out what it refers to.** A PR body saying

> This PR fixes all three (the audit's H1-H3): ...

names nothing, because H1–H3 is defined in no document. It fails
identically as "fixes the two we discussed", "applies option B", or
"resolves the pagination thing" — the shorthand differs, the defect does
not.

### Rules

1. **Expand the label at the moment it enters the artifact**, not later in
   review. What replaces it is plain text: which file, and what about it.
2. **Check before submitting that the artifact stands alone.** Reading only
   this artifact, can someone tell (a) what changed, (b) why, and (c) what
   is left? If it needs the conversation log or your memory, rewrite it.
3. **Labels are fine inside the conversation.** What is forbidden is
   carrying them across.
4. **PR bodies are where this leaks most.** They tend to be written from a
   summary of the conversation rather than from the commits.
5. **Deixis fails the same test.** "on this machine", "in our setup",
   "here" — the writer knows which one, and the artifact never says. A
   measurement qualified this way cannot be judged by anyone else: they
   cannot tell whether it would hold for them. Name the thing, or point at
   a document that describes it.

## Discipline 2: the artifact answers the reader, not the reviewer

Most edits to an artifact are made because someone said it was wrong. That
is exactly when the addressee slips, and the sentence that goes in answers
the person who complained.

An index page opened with "the tool pages say what is installed, these say
why". Counted, the claim held for three of eight pages. Deleting it was
right. What replaced it was not:

> They are not the other half of the tool pages. Those are readmes kept
> beside the configuration they document…

No reader had assumed a pairing. The replacement answers a question only
the reporter asked, in a document the reporter will never read again.

### Rules

1. **Removing a wrong sentence does not require writing a right one.**
   Delete it and stop. What surrounds it usually already carries the point,
   which is why the wrong sentence was removable.
2. **Do not explain a relationship that does not exist.** "X is not Y"
   earns its place only where a reader would otherwise assume it. Otherwise
   it teaches them that somebody once did.
3. **Do not let the document vouch for itself.** "the number above is not
   something anyone has to remember to measure", "that check earned itself
   immediately", "last green on 2026-07-16". These assert the quality of
   the work in place of doing it, and a reader who doubts the number is not
   reassured by a sentence claiming it is reliable.
4. **Keep project housekeeping out.** Which files were kept, why a script's
   default switch is what it is, what CI last did — decisions about the
   project, not knowledge about its subject.
5. **The author appearing as a character is the tell.** "two readers: the
   person at the machine, and CI." The moment the writer is in the text,
   the addressee has already moved.

### The test

For each sentence, **who is asking this?** If the only person who would ask
is you or your reviewer, cut it. A reader arrives with a problem, not with
a history of your edits.

## Discipline 3: derivation orders the documents

### The axiom

**What is derived is more volatile than what it derives from.** A
requirement derived from a use case moves when the use case moves; the
use case owes the requirement nothing. Protecting the stable from the
volatile — DIP exactly — then needs only one rule: **never make the
less derived depend on the more derived.** Everything below is a
theorem of this.

### Two kinds of derivation

- **Specification derivation** — an artifact derived from another and
  obliged to keep following it: a use case refines the solution, a
  requirement derives from a use case, a design satisfies a
  requirement, a test plan satisfies the design. Volatile because it
  must track its source.
- **Record derivation** — a judgment or an observation taken from an
  artifact at a moment: an ADR records which design is right and how
  that was judged — the criteria, the trade-offs, the alternatives
  rejected, never the story of the discussion; a test run records what
  held that day; a CHANGELOG entry, a PR, a commit record what changed.
  **Frozen when written.** Volatile not because it moves — it never
  moves again — but because it is true only of its moment, and every
  later revision of its subject leaves it further behind.

### The layers, derived

Specification derivation orders the living documents from stable to
volatile — solution, use case, requirement, design, infrastructure —
and every record hangs below the artifact it records. Coarsened to two
layers, this is the familiar table:

| Layer | Documents | Nature |
|---|---|---|
| Upper — specifications, present tense | Principles, PRD and specifications, README, source code and schemas | Describe how things *are*; edited as they evolve |
| Lower — records, past tense | ADR, CHANGELOG, release notes, PR, issue, commit | Append-only; frozen when written |

The order is fractal: records have their own gradient (commit < PR <
CHANGELOG < ADR), and the theorems apply across every level of it, not
only at the two-layer boundary. The axiom classifies by obligation,
not by the edge's name: a risk register *threatens* rather than
derives, but it must keep following the artifacts it threatens — a
risk retires when the design that carried it changes — so it sits on
the volatile side and holds the pointer. A "risks" section inside a
requirement or a design is that pointer written backwards.

### Theorems

1. **References run more-derived → less-derived only.** A reference is
   a dependency. "See ADR-0032" in a README makes the least derived
   document depend on a frozen record: when the ADR is superseded, the
   stable side needs editing because the volatile side changed, and the
   reference only exports the body's failure to explain itself. The
   pointer belongs to the record — an ADR naming the file and section
   it concerns is correct.
2. **Mutual links are forbidden.** Derivation is an order; a
   bidirectional link is a cycle in it, and one of the two edges is
   always the stable depending on the volatile.
3. **A record must stand on its own.** Frozen means it will not follow
   later revisions of what it cites, so never cite by section number or
   path alone — quote a sentence of what is referred to.
4. **A living document describes only the present.** Former behaviour,
   "this used to be…", how the decision was reached — record material
   stored in a following document. Git holds the diffs, the ADR the
   why, the body the current What. (A permanent fact such as "renamed
   in 0.0.34" may stay.)
5. **What is still moving does not belong in the stable layer.** "Not
   decided yet", "later", "provisional" in specification prose break
   the body's promise of being the settled present. Separate into a
   TODO, or promote into a roadmap — itself a living document.

### Code comments

Code is a living document, so the theorems apply to its comments:

- **No inline comments inside a function.** Intent belongs in the
  names and the structure. The one legitimate exception is a constraint
  the code cannot express — an invariant, an external specification, a
  deliberate why-not. Never narrate what the next line does.
- **A comment on a variable is a signal to rename it.**
- **A docstring is where the interface contract goes** — what it does,
  its arguments, its return value, its invariants. The How lives in
  the body.
- **No history, no provenance** — theorem 4, and Discipline 1: `// this
  used to be synchronous`, `// added per review`. A comment records
  only what constrains the code now.
- **`// TODO` is theorem 5 leaking into code.** Move it to the tracker
  or the roadmap.

### The reader who wants to know why

They get there without a link from the living document: index the ADRs
at the entrance to their layer — `docs/decisions/README.md`, say — and
since each ADR names the file and section it concerns, grep or the
index finds it. The path is the record's responsibility, not the
specification's.

### Litmus test

For the reference you are about to write:

- "Without following this, the **current specification** is unclear" → the
  body is underexplained. Delete the reference and finish the body.
- "Only someone asking **why it is this way** would follow it" → that path
  is the ADR's job. Do not write the reference.
- The target is a record (ADR, CHANGELOG, PR) and you are writing a living
  document → the less derived depending on the more derived. Do not
  write it.

## Discipline 4: living documents belong under the docs root

- **Keep one entrance to the present.** Scattered living documents make it
  unclear which one is currently right, and versions drift apart as updates
  are missed. Consolidate under the docs root, with a clear index.
- This is about **physical placement**, not reference direction. The
  purpose is to maintain a single entrance to the current specification.
