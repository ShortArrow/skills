---
name: unmachine-prose
description: |
  Write technical documentation that does not read as machine-generated, triggered by the moments that produce the tells: about to write "not X but Y", about to close a paragraph with a line that restates it, about to open with an announcement of the point, about to answer an objection nobody raised, about to end a sentence on an -ing clause that adds nothing, or about to fill a gap in the sources with a plausible guess. The tells are mostly structural, they differ between English and Japanese, five act on one sighting and the rest only when several stack in one passage. Use when writing a README, an ADR, a commit message, a design document, a note or a PR body, and when revising prose that reads as generic despite being correct. Also fires when writing or reviewing a bilingual documentation pair, and when delegating any such writing — the language-specific checklists must travel inside the delegation prompt, or they will not be applied.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Unmachine Prose

Nothing here is about disguising authorship.
Every pattern below is a way of saying less than it appears to,
and technical writing is worse for it regardless of who wrote it.

**The general choice is the tell.** Where a writer chose for this reader and this subject,
a model chose what fits any reader and any subject,
and the difference shows as a sentence that could sit in any document.
Every shape below is that default made visible,
and the repair is always to put the specific thing back: the fact,
the number, the name.

**The tells stack, and word lists rot.** Prose becomes recognisable when signals co-occur,
not from any one of them,
and the words in fashion change with every model release while the shapes persist.
Fix the density, not the dictionary.
Five shapes are marked below as acting alone: the trailer,
the manufactured contrast, the closer,
the run-up and the argument with no one.
A careful writer produces any of them by accident about never,
so one sighting is enough; everything else counts only with company.

**The two languages barely overlap.** English tells are syntactic — trailing participles,
`not X but Y`, em dashes.
Japanese has none of those constructions;
its tells sit in 文末,接続詞 and 段落の閉じ方,
and checking Japanese against the English list finds nothing and proves nothing.

---

# English

## Participial trailers

Acts alone.
The most reliable tell in technical English.
A clause hangs off the end of a sentence and appears to conclude something while adding nothing:

> The cache is invalidated on write, **ensuring consistency**.
> The script validates the marker, **preventing silent failures**.

Either it restates the sentence,
or it is a separate claim that deserves its own sentence and its own evidence.

Look for sentence-final `-ing`: ensuring, highlighting, underscoring,
reflecting, contributing to, allowing for, fostering, showcasing.

> The cache is invalidated on write.
> A reader arriving mid-write sees the old value,
> which is why the read path takes the lock.

## Excess parallelism

Balanced structure above the rate of natural writing, at word, phrase,
sentence and paragraph level.
The rule of three is the common case:

> It is fast, reliable, and easy to maintain.

Three adjectives imply a completeness never established.
Give the one that carries weight, and say why it holds.

## Negative parallelism

Acts alone.

> This is **not just** a config change, **it is** a change in ownership.
> The problem is **not** the syntax, **but** the assumption behind it.

The construction manufactures a reveal.
Nobody had claimed the first half,
so denying it costs nothing and lends the second half a weight it did not earn.
It has a two-sentence form,
a denial followed by the point it was staging ("This is not a refactor. It is a rewrite."),
and a clipped form where a bare negative hangs off the end (", not a workaround").
A real contrast, one where the reader did hold the belief being corrected,
occasionally needs it; three on one page means none of them are real.

## The closer

Acts alone.

> Writes go through the queue, and readers see each write in order.
>
> Order is everything here.

The second paragraph adds no fact;
it asks the reader to stop and admire the first.
Its cousins are the identical last line under every section,
and the sequence of sentence fragments where one sentence would do ("No lock. No queue. No surprises.").
A short sentence earns its emphasis by carrying something new;
the one that repeats is cut.

## The run-up and the aphorism

Acts alone.

> Before we get to the numbers, some context.
> At the end of the day, latency is the product.

The first sentence promises the point instead of making it;
the second inflates an ordinary observation into a maxim.
Both leave the reader waiting for the sentence that says what the numbers are.
Delete the run-up, and write the claim the maxim was standing in for:
"p99 latency is what the customer notices, so it is the number we report".

## Arguing with no one

Acts alone.

> It would be easy to blame the cache here.
> One option is to shard by tenant, but that doubles the operational cost.

Nobody blamed the cache, and nobody proposed sharding;
the paragraph is defending against a draft that was thrown away.
Delete the phantom objection.
If the sentence was carrying a real claim (the cache is not the cause; sharding was priced and declined),
state the claim without the opponent.
Keep an objection when the text names who raised it,
and an option when a reader would weigh it themselves.
When several of these stack in one section,
the section is arguing with its own outline.

## Significance inflation

> This **plays a crucial role** in the build.
> The change **underscores the importance** of validation.

In biomedical abstracts `delve` runs about 28× its 2022 rate,
`underscores` 14× and `showcasing` 11× (Kobak et al., 2025).
The vocabulary follows the habit:
asserting that something matters instead of showing what it does.

`serves as`, `stands as`, `functions as`, `represents`, `boasts`,
`features` — all `is` wearing a coat.
Use `is`.

## Formatting

**Inline-header bullets.** `- **Term**: description` is the most recognisable shape in machine-written documentation.
Keep it for genuine key-value data.
When the descriptions are sentences, write sentences.

**Bold by default.** Bolding every scannable term emphasises nothing.

**Title Case Headings.** Sentence case,
unless the project already differs.

**Em dashes.** Not forbidden, overused.
More than one per paragraph is a rhythm, and the rhythm is the tell.

## Content

**Elegant variation.** Swapping synonyms to avoid repetition damages technical writing specifically:
a `cache`, a `store` and a `layer` are three things.
Repeat the noun.

**Vague attribution.** `Industry reports suggest`, `best practice is`,
`experts argue`.
Cite it, measure it, or own it as your judgement.

**The guess dressed as a gap.** "The origin of the setting is unclear, but it was probably added for performance" concedes that nothing was found and then invents the answer.
Write the gap as a gap ("nothing in the history says why the setting exists"),
or leave it out; a guess is not made true by the admission in front of it.

**Hedging without information.** `This may potentially help in some cases` says nothing.
`This helps when the working set exceeds RAM` does.
Two hedges on one claim usually mean an earlier overstatement was softened twice instead of corrected once;
keep the one condition the evidence supports.

**Chat residue.** `Great question`, `Here is an overview`,
`I hope this helps`,
`Let me know if you want` inside a README or a PR body.
The document was written as a reply and shipped as a page.
Nothing here needs rewording: delete the greeting and the offer,
and keep what they were wrapped around.

---

# Language layers

The rule is language-neutral; what differs by language is layered on,
not mixed in.
Japanese: read `references/japanese.md` before writing or revising Japanese.
It carries the forms that exist only there and worked examples in Japanese.
A draft in another language uses the body alone.

Everything language-specific is in `references/japanese.md`:
the metaphors and personifications that ride in from English,
the 「〜ことで」 construction, the endings that withhold a judgement,
the paragraph that closes neatly every time,
the title that names only the first section,
and the lorem ipsum left behind when metaphors are deleted and nothing is put back.
It is written in Japanese because the reader checking a Japanese draft should be reading Japanese,
not a description of it.
---

## Bilingual pairs

The commonest accident in a bilingual documentation pair is writing one language and translating it into the other.
The instruction that produces it is innocent,
"make the same edit in both languages",
and under it the draft translated from English becomes the default rather than the exception.

- **Write each language from the shared list of facts.** Only terms are translated.
  Word order, metaphors and syntax that carry over from the other draft are the evidence that it was translated.
- **Check each language against its own list.** Passing one side because it "says the same thing" passes nothing;
  Japanese checked against the English list yields nothing.
- **When delegating the writing,
  put the checklist in the prompt.** A subagent or a colleague has not read this skill.
  The instruction is "the same facts, in each language's conventions",
  with the target language's checks attached, not "the same edit in both".

An instance: a bilingual README written as a pair left 「チェックアウトの中でしか動かない」「プロトコルを話す」「読んでいる場所によって違う」 on the Japanese side,
and nobody noticed until review.
Each is an English draft showing through — a shape nobody writes when reading the Japanese as Japanese.

## Checking your own draft

**English** — read the sentence endings down the page.
Participial trailers and significance inflation both land there.

Count per 200 words:

- sentence-final `-ing` clauses
- triplets
- `not X but Y`
- `- **Bold**:` lines
- em dashes
- one-sentence paragraphs in a row

**Japanese** — two reads, and a different count;
both are in `references/japanese.md`.

**Rewrite around the point,
not phrase by phrase.** First read the whole passage and note every shape it shows,
worst first, including the ones that only appear at paragraph scale (the same closer three times, three parallel examples).
Then write the passage again from what it was saying.
Replacing each flagged phrase in place leaves the shape that produced it,
and the result reads as edited rather than written.
Two checks afterwards: every claim the original supported is still there,
and nothing was added, no fact, figure,
date or source the original did not carry,
because a rewrite that changes shape is where a fact most often slips out or slips in.
If the author has written elsewhere,
their own prose outranks every rule here, dashes included.

**Thinness does not show in a count.** Formal Japanese ends most sentences in ます・です,
and that ratio passes ninety percent in prose that is perfectly good;
a threshold on ending distribution or sentence length flags text that has nothing wrong with it.
Instead, pick one sentence per paragraph and delete it. **A run of sentences whose deletion costs nothing is the lorem ipsum itself.** The ground left after a deleted metaphor shows up here.

One of these is style.
Several stacking is a signal.

## Length

Cut, and most of the above disappears together,
because these patterns are **what fills the page after the content has run out**.
The trailing participle, the triplet,
the closing paragraph — each is a way of continuing past the end of what there was to say.

If a third can go without a single fact going with it,
the word count was the tell.

## What is not a tell

Correct spelling.
A long word used precisely.
Consistent formatting.
Structure that follows the shape of the content.
Plain writing that is correct is not a target.

Nor is a flagged phrase when it is being quoted,
when it is part of a title or a name,
or when the sentence is about the phrase rather than using it.
Nor is text that predates the models that produced the habit.
And what marks a particular writer stays even where a rule above would touch it:
the odd concrete detail nobody would invent,
a judgement left undecided because the writer is undecided,
a digression, a correction made in the open,
a first-person choice they can account for.

Nor are the ordinary errors of a language: a doubled honorific,
a subject that never meets its predicate, の stacked three deep,
one term spelled two ways.
Humans make those at the same rate, and they are `plain-language`'s.
Apply both in turn; mixing them dulls each check.

## Sources

- blader/humanizer v3.0.0 (MIT, commit 9862685 of 2026-09-06),
  read 2026-09-17,
  which rests on Wikipedia's "Signs of AI writing" maintained by WikiProject AI Cleanup:
  the observation that a tell counts by how rarely a careful writer makes it on purpose,
  the general choice as the cause, the closer, the run-up, the aphorism,
  the argument with no one, the guess dressed as a gap, chat residue,
  and the rewrite that keeps every claim and adds none.
  The shapes are restated here in this catalogue's words with its own examples;
  humanizer's ranking of its own patterns is not reproduced,
  and the five marked as acting alone are this catalogue's choice.
- Dmitry Kobak, Rita González-Márquez, Emőke-Ágnes Horvát and Jan Lause,
  "Delving into LLM-assisted writing in biomedical publications through excess vocabulary",
  Science Advances 11(27), 2025-07-02 (arXiv 2406.07016):
  the excess-frequency ratios for `delves`,
  `underscores` and `showcasing`,
  checked against the published version on 2026-09-17.
