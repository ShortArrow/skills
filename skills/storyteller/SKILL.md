---
name: storyteller
description: |
  The skeleton of a technical article or post meant to be read through, triggered by the moments that let the material choose it: about to order the sections in the order the notes were taken, about to put the answer in the title, about to keep every false lead because it happened, about to pass the most surprising finding as one step among the others, about to open the way every post opens, or about to borrow a known story's text where its shape was what was wanted. Chronology is a skeleton only when the turn comes last in time; otherwise the reader learns the answer before the question has weight. Covers finding the turn, choosing a skeleton that lands on it (kishōtenketsu, the detective arc, the fall and the rise, a borrowed form recast), a title that asks, and an ending that returns. Use when outlining or restructuring a technical blog post, an incident write-up or a talk in any language. Not for pages read by search or scanned; document-structure owns those.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Storyteller

An article read through is held by one thing:
the reader wants to know what happens next.
Notes are written in the order things happened,
and an article built in the same order reads as a log.
The skeleton is chosen, and the material is placed on it,
not the other way round.

## Language layers

The rule is language-neutral; what differs by language is layered on,
not mixed in.
Japanese: read `references/japanese.md` before writing or revising Japanese.
It carries the forms that exist only there and worked examples in Japanese.
A draft in another language uses the body alone.

## The moments this replaces

| About to… | Instead |
|---|---|
| make the sections the steps of the notes, in order | find the turn first, then choose a skeleton that lands on it; keep chronology only when the turn is also the last event |
| put the answer in the title ("X was caused by Y") | title the question or the symptom the reader recognises; the answer belongs where the skeleton turns |
| keep every false lead because it happened | keep the one that makes the turn land, the belief the reader shares and the evidence breaks; cut the rest to a clause |
| pass the most surprising finding as one step | make it the turn: give it its own section, and slow down before it |
| open with the incident scene because the notes begin there | open with whatever makes the question felt: the turn stated before it can be understood, the strangest observation, the belief about to break |
| end on a list of lessons, or on the same question to the reader every post ends on | return to the opening and show it again through the new frame |
| copy a known story's sentences to borrow its shape | borrow the shape and recast it with this material; the text stays the author's own |

## Find the turn

Before any outline, list the events of the material in one line each,
and mark the one that changed what the author believed.
That is the turn.
An investigation usually has one:
the observation after which the first hypothesis could not stand.
If no event changed a belief, the material is a procedure,
and a procedure is written as one;
no skeleton rescues a piece that has no turn.

## Choose the skeleton

Each skeleton places the turn somewhere different,
so the choice follows where the turn should hit.

- **Kishōtenketsu (起承転結).** Introduction, development, turn,
  conclusion; from the four lines of a Chinese quatrain,
  where the third line shifts the scene.
  The turn need not be a conflict: it is a change of viewpoint,
  after which the first two parts read differently.
  Fits a piece whose surprise is a reframing,
  "the cache was never the slow part".
- **The detective arc.** The symptom, the obvious suspect,
  the clue that clears the suspect, the reveal, the fix.
  Freytag's rising action, climax and falling action,
  told as an investigation.
  Fits a debugging story;
  the reader is invited to suspect along with the author,
  so the obvious suspect must be one the reader would also have chosen.
- **The fall and the rise ("man in a hole").** Things go wrong, get worse,
  then are put right.
  Reagan et al. found it among six shapes that dominate the emotional arcs of stories.
  Fits an outage or a migration, where the cost is the tension.
- **The rise and the fall ("Icarus").** An improvement succeeds,
  then its cost arrives.
  Fits the optimisation that backfired,
  where the success has to be believed before the fall can land.
- **A borrowed form, recast (換骨奪胎).** Take the shape of a story the reader already knows — a fable,
  a recipe, a trial, a well-known talk — and fill it with this material.
  From Huang Tingjian's method as recorded in the *Lengzhai yehua*:
  keep the sense and change the words, or take the sense into a new form.
  The borrowed thing is the shape; the sentences are written new.

- **The ending first (flash-forward, bookend).** Open on the turn itself,
  stated in a form the reader cannot yet understand — "the cache was never the slow part" — then tell how it came to be true,
  and close on the same line, now understood.
  The answer is given at the start; its meaning is what is withheld.
  Fits a piece whose turn is one sentence that sounds wrong out of context.

When two skeletons fit, take the one that puts the turn later and shows less in the title.

## The title and the opening ask

The title is the first sentence of the skeleton,
so it carries the question, the symptom or the belief,
never the meaning of the turn.
"Deploys failed every Monday morning" asks;
"deploys failed because the cron ran in UTC" answers,
and the reader who already holds the answer has no reason to read on.
A title that states the turn in a form that does not yet make sense still asks;
it is the ending-first skeleton's opening line.
The opening makes the question felt in the reader's own terms within a few sentences,
and differs from piece to piece.
The incident scene is where the notes begin,
which makes it the opening the material chose;
take it only after the ending-first line and the strangest observation have been tried and lost.

A reader who arrived from a search for the fix is better served by a page that leads with the fix.
That page is a how-to, scanned rather than read through,
and `document-structure` owns it.

## The ending returns

The ending goes back to the opening — the scene, the belief,
the symptom — and shows it again through what the turn revealed,
so the reader sees the distance travelled.
How it does so varies with the piece:
the opening line repeated and now understood,
the failing command run again and passing,
the one fact still unexplained.
A question put to the reader is one of these;
the same question at the foot of every post is a tic.
A list of lessons restates the body and ends the pull before the last line.

## After the outline

1. **Order test.** Compare the section order with the order of the notes.
   If they are identical, say which skeleton chose it and why the turn is last;
   otherwise the material chose it.
2. **Opening and ending test.** If the opening is the first event of the notes or the ending asks the reader about their own system,
   say why this piece needs it.
3. **Title test.** Read the title alone.
   If it states what the turn reveals, rewrite it as the question.
4. **Turn test.** Point at the section where the turn happens.
   It should be one section, slowed down before it,
   and not shared with a routine step.

## Where it applies

A piece takes a skeleton when two things hold:
it is read from the start rather than scanned,
and something in it changed what the author believed.

- A debugging story: the first hypothesis breaks.
- A talk or a lightning talk: the audience cannot skip ahead,
  so the skeleton carries the most weight there.
- A tool or a new feature introduced by the problem it changed,
  not by its options.
- A syntax or idiom post: the old form that seemed fine,
  and the one case where it was not; a small kishōtenketsu.
- A performance or migration write-up: the fall and the rise,
  or the rise and the fall.

A release note, a changelog, a README, a reference,
a how-to reached by search and a runbook are scanned for the answer,
and lead with it.
A tool introduction that lists options has no turn,
and a skeleton laid over it only delays the reader.

## What this is not for

Reference pages, how-tos, READMEs and runbooks are scanned,
and lead with the answer; `document-structure` owns them.
The rhythm inside a section — the openings of sections,
the beat of sentences, the questions held open — is `cognitive-rhythm`,
which runs on the skeleton this skill chose.
The tells of machine writing are `unmachine-prose`.

## Sources

- Gustav Freytag, *Die Technik des Dramas* (1863): rising action,
  climax and falling action,
  named here only as the frame of the detective arc.
- Andrew J. Reagan, Lewis Mitchell, Dilan Kiley,
  Christopher M. Danforth and Peter Sheridan Dodds,
  "The emotional arcs of stories are dominated by six basic shapes",
  EPJ Data Science 5, 31 (2016),
  epjds.epj.org/articles/epjdata/abs/2016/01/13688_2016_Article_93/13688_2016_Article_93.html;
  abstract read 2026-10-29: the six shapes,
  among them "man in a hole" and "Icarus".
- 起承転結: kotobank.jp/word/起承転結, read 2026-10-29,
  the composition of a quatrain (起 raises, 承 develops, 転 shifts the scene, 結 closes),
  earlier called 起承転合, later applied to renga, haikai and prose.
- 換骨奪胎: kotobank.jp/word/黄庭堅, read 2026-10-29,
  Huang Tingjian's method of building a new poem from an earlier poet's lines;
  hugkum.sho.jp/631363, read 2026-10-29,
  the two methods as recorded in the *Lengzhai yehua*: 換骨,
  keeping the sense in new words, and 奪胎,
  taking the sense into a new form.
