---
name: reader-map
description: |
  The reader's map, triggered by the moments that lose them: about to name a thing by its properties before saying what kind of thing it is, about to open a paragraph without saying whether it deepens, leaves or returns to the one before, about to add a sentence or a paragraph because it came to mind next, about to put the word that answers the previous sentence at the end of the next, about to flatten a "perhaps" into a fact or explain two causes as one, about to assert a cause without its mechanism, about to announce a point instead of making it, about to say a thing again in other words, or about to write as confirmed what was not checked. Every sentence parses, the headings outline, and the reader still reads ahead to learn what a sentence was for. Use when revising a chapter, an article, a design note or an explanation in any language whose sentences already parse, when writing or adding to one, and when a reader says a draft is hard to follow without pointing at a sentence.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# The reader's map

Every sentence is correct.
The headings, read alone, make an outline.
And a reader still says they lost track of what the piece was about halfway down.
An editor finds where by reading one character at a time with three questions held open:

- How does this paragraph relate to the ones around it:
  does it go deeper into the last one, move to something else,
  or return to something from further back?
- What is this sentence doing in its paragraph:
  picking up the previous paragraph, developing this one,
  or handing over to the next?
- Why is this word in this position:
  is it the topic about to be discussed, the predicate of that topic,
  a modifier, or there for the rhythm?

A text where all three can be answered at every point is one where **the reader's map is intact**.
A reader builds a map as they go and files each new piece of information somewhere on it;
the moment a piece arrives with nowhere to go, they are lost.
The rules below come from editorial practice and rest on no standard.

## Language layers

The rule is language-neutral; what differs by language is layered on,
not mixed in.
Japanese: read `references/japanese.md` before writing or revising Japanese.
It carries the forms that exist only there and worked examples in Japanese.
A draft in another language uses the body alone.

## The moments this replaces

| About to… | Instead |
|---|---|
| open with properties ("it is kept per host and keeps growing while the collector is unreachable") | say what kind of thing it is first (a file, a procedure, a constraint) and hang the properties on that |
| start a paragraph without saying how it relates to the last | say it in the first words: "specifically" for deeper, "meanwhile" for elsewhere, "back to the spool" for a return |
| add a sentence because it came to mind next | if you cannot say where on the map it goes, move it to where it can go; if nowhere, cut it |
| put the word that answers the previous sentence at the end of the next | bring it to the front; the reader looks for the continuation at the start of the sentence |
| swap the subject the reader expects for its object | keep the previous sentence's subject as subject; turn a run of passive facts back into an agent doing things |
| turn "may" into "is", or "is" into "may" | decide by the evidence in the text: assert what it settles, keep the doubt where it does not; never for tone |
| explain two causes as one ("it is slow because the spool is large") | separate them, and say which remedy answers which |
| write "if A then B" and stop | add the one sentence that says why |
| announce a point ("the important thing is…") | make it |
| bold a second phrase in a section | one or two per section, at the places where a misreading would cost; elsewhere, word order carries the weight |
| say the same thing again in other words | once; a second sentence on the same subject is only a repeat if it adds no proposition |
| write "confirmed" about something not checked | write the range that was checked; where an example looks contrived, admit it and give the reason it still happens |

## The three questions for an ambush

A sentence whose purpose only becomes clear a few sentences later has ambushed the reader.
Fixing it takes three questions in order:

1. On the map the reader has built so far, where would this go?
2. Has the text so far built a map with a place for it at all?
3. If it has, what sentence would tell the reader that something new is being added here?

> The spool is kept per host and keeps growing while the collector is unreachable.
> It is capped at 256 MB by default.
> A spool is an append-only file holding log entries in the order they arrived.

Only the third sentence gives the first two somewhere to go.
Put the kind first and the properties file themselves:

> A spool is an append-only file holding log entries in the order they arrived.
> It is kept per host and keeps growing while the collector is unreachable,
> and it is capped at 256 MB by default.

What the reader has to hold grows one step at a time.
A property that is natural only to someone who already knows the thing does not come before the sentence that says what the thing is.

## A paragraph says how it follows

`document-structure` has the first sentence state what the paragraph is about.
This adds one thing: the first words also say **how it follows the paragraph before** — deeper,
elsewhere, or back.
There are only those three,
and a reader left to guess assumes "deeper",
reads on under that assumption,
and finds out mid-paragraph that it was wrong.

> The redesign keeps both versions of a conflicting record.
> (…)
>
> When the spool reaches its limit, the oldest entries are dropped.

The second paragraph reads as a continuation of conflicts and is a return to the spool.
"Back to the spool:" fixes its place on the map.
If there is no reason to return,
the paragraph belongs in the spool section.

## The writer's order is not the reader's

A writer writes in the order things occurred to them,
and that is the order of the writer's map.
When a sentence in a paragraph is not quite about the paragraph's subject,
it is usually one the writer wanted to get said here.

> On a conflict, the change synced last wins.
> In the old version the settings screen had a "prefer latest" option,
> and most users had it on.
> The rule is simple, and it silently loses the change synced first.

The old setting does not sit on this paragraph's subject,
which is the rule and its cost.
If the comparison with the old version is needed, give it a paragraph;
if not, cut it.
The test is per sentence: can you say where on the map it goes?
The one you cannot place is the intruder.

## The answering word goes first; the subject carries over

When the word that picks up the previous sentence arrives at the end of the next one,
the reader holds the whole sentence unfiled until then.

> The user makes the choice.
> Excluded from sync until that choice is made are the records that conflicted.

The second sentence's subject was the first sentence's object,
and it comes last.
Either keep the first sentence's subject,
or bring the answering word forward:

> The user makes the choice.
> A conflicted record stays out of sync until the choice is made.

A run of facts in the passive ("was identified, was found") has the same effect.
Restoring an agent that does things keeps the subject running across the sentences.

## No holes in the argument

A map can be intact and still stop the reader at a claim that does not hold.
After the draft, read it as its objector would.

- **Doubt is decided by evidence.** Do not turn "may" and "seems" into assertions mechanically.
  Assert only what the text's own evidence settles;
  leave the doubt on an unverified possibility, an inference from a log,
  a question the reader would raise.
- **Do not call different things the same.** Separate decisions,
  separate causes, different kinds of problem do not share one word.
  "It is slow because the spool is large" followed by "half the delay was the reconnect wait" is two causes.
- **A cause carries its mechanism.** "Compression makes it faster" stops short;
  the sentence that says why, less to transfer or fewer comparisons,
  goes with it.
- **Guarantees are conditional.** Nothing is "always" detected or resolved;
  say when it holds.
- **The example supports the whole claim,
  or the claim shrinks to the example.**
- **Forward references are collected.** A point deferred to "later" is checked,
  after the draft, to be there.

## Rhetoric only where it works

Announcing a point ("the important thing is…") is a preview of the point;
write the point and the preview is not needed.
Bold goes on the one or two places in a section where a misreading would cost — a negation,
a section's conclusion.
Suspense ("there is something hiding here") and rhetorical questions are for the places where the tension does work in the argument;
where a statement would do, state it.
Do not stack consequences to alarm.
In the argument, address the reader by role, not as "you".

## Say a thing once

A claim is made once.
Summarising a scene just after showing it is the same claim twice.
Redundancy is not measured in words: compress only where the motive,
the object, the operation,
the cause and the condition stay explicit in reading order,
and never by handing the reader an inference.
The repeated frame that shows list items share a status,
and the condition placed right after a definition,
are not repeats — they are different propositions.

## Confirmed means checked

Do not write as confirmed what was not checked,
and do not write it smoothly.
"The Windows agent was confirmed to behave the same" in a document whose last section says the Windows agent has not been started is false.
Write the range that was checked — Linux, three hosts,
twenty-four hours.
Where an example looks contrived, say so before the reader does,
and give the reason it happens anyway in terms of the reader's own experience ("this symptom is not rare").

## What this is not for

A paragraph whose connection to the last is obvious and needs no connective.
A softening placed on purpose for tone ("one could call it required").
Repetition and length that are needed.
Cutting the sentences that share context at the start is not pacing;
it is omission.

## Connections

Whether a sentence reads one way (subject meeting predicate, modifier attachment, spelling) is `plain-language`.
Whether the headings outline, the paragraphs hold one subject,
the procedures are numbered, is `document-structure`.
The tells of machine writing are `unmachine-prose`.
Whether a number carries its method is `measured-claims`.
This skill takes the draft that has passed those and still loses its reader.
Apply them in turn; mixing them dulls each.

The source gist (below) carries the full set of rules for book manuscripts in Japanese,
including sections not adapted here — the vocabulary list of LLM-style phrases,
narration and viewpoint, how to title a section.
A reader who wants it whole can place its SKILL.md at `~/.claude/skills/japanese-tech-writing/SKILL.md` and it loads as one skill.

## Sources

- 「編集者は日本語をどうやって推敲しているか（それを機械化できるのか）」 golden-lucky の日記,
  2026-08-20 (golden-lucky.hatenablog.com/entry/2026/08/20/185818).
  The three-level reading,
  the three symptoms and the three questions for an ambush are from this article.
  Read 2026-09-10.
- k16shikano, "japanese-tech-writing/SKILL",
  gist (gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d),
  Unlicense by the author's declaration (gist 67625f2a7d96e3bbdfae8d571a936063).
  Revision of 2026-09-09, read 2026-09-10.
  Its sections on reader load, rigour of argument, restraint in rhetoric,
  redundancy and honesty were rewritten into this repository's shape (the moment and its replacement),
  not copied.
