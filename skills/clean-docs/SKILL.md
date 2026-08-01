---
name: clean-docs
description: Discipline for writing durable artifacts — PR bodies, commits, CHANGELOGs, ADRs, READMEs, PRDs, specifications, source code. (1) Never carry a label that only means something inside the conversation. (2) Documents obey the dependency inversion principle: a stable, abstract living document (README, PRD, principles, code) must not depend on a volatile, concrete journal (ADR, CHANGELOG, PR). No ADR numbers or section references pointing out of a living document, no mutual links, no former behaviour or history in the body, undecided items separated out, and an ADR that records reasoning rather than narrative. (3) Living documents belong together under the docs root. Use when writing a PR, a commit, a CHANGELOG, an ADR or an issue, when editing a README or PRD, when copying review or audit findings into an artifact, and whenever you are about to write "See ADR-NNNN".
---

# Self-Contained Artifacts

A durable artifact is **read after this conversation has ceased to exist,
by someone who never saw it**. Beyond that, a set of documents has an
**architecture — layers, and a direction of dependency**. Clean
architecture is not only for the implementation; the documentation has one
too. That is the whole of this skill.

## Discipline 1: conversation labels stay in the conversation

Findings organised as H1/H2/H3 and M1–M4 while working through an audit
are useful in the conversation and meaningless outside it. A PR body that
says

> This PR fixes all three (the audit's H1-H3): ...

names nothing. H1–H3 are defined in no document, so the reader has no way
to reach them.

### Rules

1. **Expand a conversation label at the moment it enters an artifact.**
   H1/M2, "option A", "the three from earlier", "that problem" — in the
   artifact, write plainly which file, and what about it.
2. **Check before submitting that the artifact stands alone.** Reading only
   this artifact, can someone tell (a) what changed, (b) why, and (c) what
   is left? If it needs the conversation log or your memory, rewrite it.
3. **Labels are fine inside the conversation.** What is forbidden is
   carrying them across.
4. **PR bodies are where this leaks most.** They tend to be written from a
   summary of the conversation rather than from the commits.

## Discipline 2: dependency inversion for documents

### The core

**A stable, abstract document (a living document — the upper layer) must
not depend on a volatile, concrete one (a journal — the lower layer). The
pointer always belongs to the concrete side.** This is DIP exactly: when
a high-level policy couples to a low-level detail, a change in the
volatile thing breaks the stable one. Avoid in documentation what you
avoid in code.

"References point one way" is a consequence, not the axiom. The axiom is
*protect the stable from the volatile*, and the direction, the ban on
mutual links, and every rule below all follow from it.

### The layers

| Layer | Documents | Nature |
|---|---|---|
| Upper — stable, abstract, present tense | Principles, PRD and specifications, README, source code and schemas | Always describe how things *are*. Edited as they evolve. |
| Lower — volatile, concrete, past tense | ADR, CHANGELOG, release notes, PR, issue, commit | Append-only records of a decision or a change. Frozen when written. |

The journals have their own internal gradient of specificity — commit <
PR < CHANGELOG < ADR. The layering is fractal.

### Rule: references run concrete → abstract only

- **A living document never points at a journal.** No "see ADR-0032", no
  "(ADR-0028)", no "details in CHANGELOG 0.0.34" in a README, a PRD, a
  principles document or a source comment. That is a stable→volatile
  dependency, and a DIP violation.
- **The pointer belongs to the concrete side.** An ADR or CHANGELOG naming
  a specification section, a file path or a function is correct — the
  volatile thing points at the stable one.
- **Mutual links are forbidden.** Bidirectional means circular, and one of
  the two edges will always be stable depending on volatile.
- **Apply it fractally.** The same holds inside the journals. References
  within one level are fine; crossing levels goes concrete → abstract only.
  "Journals may reference journals" is not unconditional.
- **A frozen journal does not follow later revisions.** Do not rely on a
  section number or a path alone — quote a sentence of what you are
  referring to so the entry stands on its own.

### Rule: a living document describes only the present

- **Git holds the history, so the body holds only the current
  specification.** No former behaviour, no "this used to be…", no account
  of how the decision was reached. Those belong to the lower layer — the
  journals, and git's diffs.
- **Why belongs in the ADR, the historical diff in git, the current What in
  the body.** A permanent fact such as a version number ("renamed in
  0.0.34") may appear in the body.

### Rule: undecided items do not dissolve into the body

- **Keep "not decided yet", "later" and "provisional" out of specification
  prose.** They break the body's promise of being the settled present, and
  the reader can no longer separate what is fixed from what is hoped for.
- Separate them into a **TODO**, or promote them into a **roadmap** — which
  is itself a living document.

### Code comments

Code is a living document, so everything above applies to its comments.
By kind:

- **Do not write inline comments inside a function.** Intent belongs in
  the function name, the variable names and the structure. **The one
  legitimate exception is a constraint the code cannot express** — an
  invariant, a reason imposed by an external specification or environment,
  or a deliberate why-not. Never narrate what the next line does, and never
  explain what reading the code would tell you.
- **A comment on a variable is a signal to rename it.** When you want to
  explain a variable, fix the name instead.
- **A docstring is where the interface contract goes.** What it does, its
  arguments, its return value, its invariants. The How lives in the body.
- **No history in comments.** `// this used to be synchronous`, `// made
  async to fix bug #123` — that is history stored in a living document. The
  decision belongs to an ADR, the change to a commit or PR, the history to
  git. A comment records only what constrains the code now.
- **No provenance, no review scars.** `// added per review`, `// addresses
  the review comment`, `// requested by …` — the origin of the work does
  not belong in the artifact. Same as Discipline 1.
- **`// TODO` is an undecided item leaking into prose.** Do not accumulate
  them in comments. Move them to the tracker or the roadmap.

### What an ADR is, and is not

- **An ADR records which design is right and how that was judged.** The
  reasoning, the criteria, the trade-offs, the alternatives rejected.
- **It is not the story of what happened on the way there.** Where an
  incident or a discussion supplies a fact the reasoning needs, quote the
  fact; do not keep the narrative.

### Why: what a DIP violation breaks

1. **Understanding the current specification starts to require reading the
   archive.** "See ADR-NNNN" only exports the body's failure to explain
   itself. A self-contained body needs no reference.
2. **The stable side couples to the volatile side.** When an ADR is
   superseded, stale references remain in the living documents and have to
   be hunted down by grep. An upper layer must not need editing because a
   lower one changed.
3. **Why ends up in two places.** Why in the ADR, What in the
   specification, How in the implementation — once a living document starts
   citing ADRs, the Why bleeds into the body and the separation collapses.

### The reader who wants to know why

They can still get there without a link from the living document. Index
the ADRs at the entrance to their layer — `docs/decisions/README.md`, say —
and since each ADR names the file and section it concerns, grep or the
index finds it. It is the same as searching for usages to find a domain
from the code: the path is the journal's responsibility, not the
specification's.

### Litmus test

For the reference you are about to write:

- "Without following this, the **current specification** is unclear" → the
  body is underexplained. Delete the reference and finish the body.
- "Only someone asking **why it is this way** would follow it" → that path
  is the ADR's job. Do not write the reference.
- The target is a journal (ADR, CHANGELOG, PR) and you are writing a living
  document → stable depending on volatile. Do not write it.

## Discipline 3: living documents belong under the docs root

- **Keep one entrance to the present.** Scattered living documents make it
  unclear which one is currently right, and versions drift apart as updates
  are missed. Consolidate under the docs root, with a clear index.
- This is about **physical placement**, not reference direction. The
  purpose is to maintain a single entrance to the current specification.
