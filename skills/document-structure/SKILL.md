---
name: document-structure
description: |
  The shape of one document, triggered by the moments that flatten it: about to put a second topic into a paragraph, about to write a heading called Overview, Notes or Miscellaneous, about to open with background and reach the point in the last section, about to write a procedure as prose or put two actions in one step, about to bullet a set of items that have three fields each, about to use a term before defining it or call one thing by two names, about to nest a fourth heading level or skip one, or about to explain the abstraction before showing an instance. A reader scans a page before reading it, and a document whose headings do not read as an outline has hidden its content from that pass. Use when writing or revising a README, a guide, a specification, a runbook, a report or a long message in any language, and when a draft is correct sentence by sentence and still hard to use.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Document structure

Sentences can each be right while the page fails, because the reader
never reads the page in order. They scan the headings, read the first
line of the paragraph that looks relevant, and leave or go deeper. The
structure is what that pass sees, and every rule here follows from
one fact: **the first thing in any unit is the only thing most readers
will read of it.**

## The moments this replaces

| About to… | Instead |
|---|---|
| put a second topic into a paragraph | one idea per paragraph; the first sentence states it and the rest supports it. The second idea is the next paragraph |
| write a heading called Overview, Notes, Details, Miscellaneous | name what is under it. Read the headings alone, top to bottom: if that is not an outline of the document, the headings are labels, not headings |
| open with background, history or motivation | put the conclusion, the result or the action first; the reader who needs the background will keep reading |
| write a procedure as a paragraph, or two actions in a step | numbered steps, one action each, the expected result stated after the action |
| bullet items that each carry three pieces of data | a table: rows are items, columns are the fields. A list holds one dimension |
| use a term before it is defined, or call one thing by two names | define at first use, then use the same word every time; synonyms read as different things |
| add a fourth heading level, or jump from a second to a fourth | three levels is the depth a reader can hold; past that, split the document. Never skip a level |
| explain the general case before showing one instance | the example first; the abstraction that follows is shorter and lands |
| write "see above" or "as mentioned earlier" | say it again in one sentence, or restructure so it is read once, where it is needed |

## The first line carries the unit

A paragraph's first sentence is its claim, and a reader who stops
there should know what the paragraph would have told them. That is
the paragraph's job description, and it fails in two familiar ways:
the sentence that warms up ("It is worth noting that…") and the
paragraph that changes subject halfway. The test is mechanical — read
only the first sentence of each paragraph in a section, and see
whether the section still makes sense.

The same rule scales. The first paragraph of a section states what the
section establishes; the first section of a document states what the
document is for and what the reader will be able to do afterwards. A
document that opens with history is a document whose reader has to
finish it to learn whether it was for them.

Length follows from the rule rather than from a count. A paragraph is
as long as one idea's support, which in practice is three to seven
lines; a single-line paragraph is fine when the idea is one sentence.

## Headings are the outline, and the outline is read alone

Headings are read in two ways: as signposts while scanning, and as a
table of contents when listed. Both fail on a heading that names a
kind of content rather than the content — "Overview", "Background",
"Notes", "Other". The heading has to be true of its section and false
of every other section, or it does not help the reader choose.

Two shapes work. A noun phrase names a thing the section describes
("Retry policy", "Directory layout"). A bare verb names a task the
section performs ("Install the driver", "Rotate the key"). Mixing the
two within a level is a tell that the sections are not parallel.

Depth is bounded by what a reader can hold in mind. Three levels is
the working limit; a fourth means the document has two documents in
it. Never skip a level, and never stack two headings with nothing
between them — the empty upper heading is a label for a section that
does not exist.

## Sequence gets numbers, sets get bullets, fields get columns

The form of a list is a claim about its contents. **Numbers** say the
order matters: steps, phases, priorities. **Bullets** say it does not:
options, examples, members. **A table** says each item has several
fields: rows are the items, columns the fields, and the header row
names them. Using bullets for a sequence loses the order; using them
for items with three fields each buries the fields in prose.

Whatever the form, the items are parallel: the same grammatical shape,
the same kind of thing. A list that mixes a noun phrase with a
sentence, or a step with a warning, is two lists sharing one set of
bullets. Introduce a list with a full sentence that says what the
items are, so a reader arriving from a heading knows what they are
looking at.

Single-step procedures are not numbered; one step is a sentence.

## A procedure is one action per step, with its result

A procedure is a numbered sequence a reader executes while reading,
one eye on the page and one on the screen. Every step is one action.
When an action produces something the reader needs to see before the
next step — a dialog, a prompt, a file — the step says so, after the
action: "Run the command. The prompt changes to `(venv)`." Prerequisites
go before step 1, not inside step 4 where they are discovered too
late. An optional step says "Optional:" at its start, not in
parentheses at its end where it is read after the step was done.

## Define once, name once

A term used before it is defined sends the reader forward looking for
the definition, and a thing called by two names is read as two things.
Define at first use, in the sentence where it appears, and use exactly
that word afterwards. Variety is a virtue in prose that is read for
pleasure; in a document that is used, it is a defect.

## The instance before the rule

An abstraction stated cold has to be held in mind until the example
arrives to make sense of it. Put the example first — the command, the
file, the message — and the general statement that follows is shorter
and needs no holding. This inverts the order most drafts arrive in,
because the author learned the rule before they had the instance.

## Cross-references are debts

"See above", "as mentioned in section 2", "refer to the earlier
discussion": each sends the reader elsewhere and asks them to come
back. If the fact is needed here, say it here in one sentence. If it is
needed in two places, the structure has the same material in two
places, and one of them should own it while the other points at it by
name, once, not as a habit. `clean-docs` covers which document owns a
fact; this rule is about one document not making its reader walk.

## What this is not for

Sentence-level correctness — `plain-japanese` for Japanese, and the
style guides below for English. Whether a document should exist and
what it may depend on — `clean-docs`. The tells that make prose read
as machine-written — `unmachine-prose`. Which of the four reader needs
a page serves (tutorial, how-to, reference, explanation) is Diátaxis,
via `clean-docs`; this skill applies inside whichever one it is.

## Sources

- Google developer documentation style guide, developers.google.com/style,
  read on 2026-09-04: "Headings and titles" (descriptive and unique
  headings, do not skip levels, no empty headings, noun phrases for
  concepts and bare verbs for tasks), "Lists" (numbered for sequence,
  bulleted for sets, description lists for terms; parallel structure;
  a full introductory sentence), "Procedures" (one action per step,
  action then result, prerequisites before the task, "Optional:" at
  the start, a one-step procedure is not numbered), "Tables" (three or
  more fields per item is a table, one or two is a list). The guide
  carries no version number; the date is the reference.
- Microsoft Writing Style Guide, "Scannable content",
  learn.microsoft.com/style-guide, page dated 2023-06-20 and read on
  2026-09-04: put first things first, lead paragraphs and headings with
  the keyword, three to seven lines per paragraph, parallel structure
  for compared things.
- Diátaxis (Daniele Procida) is named for the four reader needs only;
  `clean-docs` carries that citation.
