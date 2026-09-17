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

**The general choice is the tell.** A model's default at every word is the choice that fits the most readers and the most subjects at once;
a person writes for one reader about one subject,
and their choices are uneven.
Every pattern below is the general choice showing through,
and the fix is always the specific one: the fact, the number, the name.

**The tells stack, and word lists rot.** A corpus of 7,600 catalogued signals concludes that prose becomes recognisable when signals co-occur,
not from any one of them,
and the words in fashion change with every model release while the shapes persist.
Fix the density, not the dictionary; and of the shapes,
five justify an edit on one sighting (they are marked below),
because a careful writer almost never makes them on purpose.
The rest count only with company.

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

The construction manufactures a reveal:
the negative half names something nobody claimed,
so the positive half sounds larger than it is.
It survives being split across two sentences ("This does not mean X. It means Y.") and being clipped to a tail (", no guessing").
A real contrast, one where the reader did hold the belief being corrected,
occasionally needs it; three on one page means none of them are real.

## The closer

Acts alone.

> The cache is invalidated on write, and readers take the lock.
>
> That is the whole design.

A one-sentence paragraph that restates the paragraph before it asks the reader to pause on a claim instead of adding to it.
The same closer after every section is the same tell at document scale,
and so is a row of fragments ("No retries. No queue. No surprises.").
A short sentence carries emphasis when it carries a new fact;
cut the one that repeats.

## The run-up and the aphorism

Acts alone.

> Let's dive into how the cache works.
> Here's the thing: the real question is whether it scales.

The first sentence announces the point instead of making it;
the second dresses an ordinary point as a hidden truth ("the real question", "at its core", "X is the Y of Z").
Delete the run-up, and replace the aphorism with the claim it was standing in for.

## Arguing with no one

Acts alone.

> To be clear, this is not about prompt length.
> A tempting approach would be to restart the service on a schedule,
> but that would drop every session.

The text answers an objection or rejects an option that appears nowhere else,
usually a leftover from an earlier draft.
Cut the defence; if a real claim is inside it, state the claim.
Keep an objection the text attributes to someone,
and an option a reader would actually weigh.
Several unrelated rejections in a row are a stronger sign than one.

## Significance inflation

> This **plays a crucial role** in the build.
> The change **underscores the importance** of validation.

`underscores` runs about 11× its pre-2022 rate, `delve` 28×,
`showcasing` 10× (Kobak et al., 2025).
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

**Blank lines by rule.** A blank line after every sentence,
and between every list item.
The page becomes a column of one-line paragraphs;
`document-structure` has the rule,
and here it counts as a tell for the same reason bold does:
it is applied to everything at once.

**Fixed-width wrapping.** Lines broken at 72 or 80 columns wherever the count falls,
mid-sentence and mid-phrase.
It changes nothing on the rendered page and everything in the diff,
where one edited word re-flows a paragraph,
and it is the shape of a source file a tool wrote.
One sentence per line, with a blank line only where the paragraph ends,
keeps both the diff and the page readable.

## Content

**Elegant variation.** Swapping synonyms to avoid repetition damages technical writing specifically:
a `cache`, a `store` and a `layer` are three things.
Repeat the noun.

**Vague attribution.** `Industry reports suggest`, `best practice is`,
`experts argue`,
and the list of outlets that stands in for what any of them said.
Cite it, measure it, or own it as your judgement.

**Vague association.** `associated with`, `linked to`,
`in connection with`: two things connected without saying how.
Name the relation the source gives (founded, maintains, was part of),
and if the source does not say,
leave it vague rather than invent a role.

**The guess dressed as a gap.** "Not widely documented, but likely established in the 1990s" admits there was no source and fills the hole anyway.
Say what the sources do not show, or cut the sentence;
never present the fill as a fact.

**Hedging without information.** `This may potentially help in some cases` says nothing.
`This helps when the working set exceeds RAM` does.
A stack of qualifiers is usually the residue of repeated editing,
each one repairing an earlier overstatement;
keep the one the source supports.

**Chat residue.** `Great question`, `I hope this helps`,
`Would you like me to`,
`Here is an overview of` inside a durable artifact.
The most certain tell on this page and the easiest to miss when it wraps real content;
remove the wrapper and keep the content.

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
not phrase by phrase.** Mark every tell first, strongest first,
at paragraph scale as well as sentence scale;
then rewrite the passage around what it was saying.
Patching each flagged phrase leaves the shape that produced it.
The rewrite keeps every supported claim and adds no fact, name, number,
date or citation the source lacks;
a shape edit is where a fact is most often lost or invented,
so the check after the rewrite is a diff of claims, not of words.
A writing sample from the author overrides every rule here,
dashes included.

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

Nor is a watched phrase inside a quotation, a title or a proper name,
or a passage that discusses the phrase rather than uses it.
Nor is anything written before late 2022.
And the details that mark a writer are kept even when a rule above would touch them:
the unusual specific, the mixed feeling left unresolved, the aside,
the self-correction, the first-person choice the writer can explain.

Nor are the ordinary errors of a language: a doubled honorific,
a subject that never meets its predicate, の stacked three deep,
one term spelled two ways.
Humans make those at the same rate, and they are `plain-language`'s.
Apply both in turn; mixing them dulls each check.

## Sources

- blader/humanizer v3.0.0 (MIT, commit 9862685 of 2026-09-06),
  read 2026-09-17,
  which rests on Wikipedia's "Signs of AI writing" maintained by WikiProject AI Cleanup:
  the ranking of tells by how rarely a careful writer makes one on purpose,
  the general choice as the cause, the closer, the run-up, the aphorism,
  the argument with no one, vague association, the guess dressed as a gap,
  chat residue, the rewrite that keeps every claim and adds none,
  and the exemptions for quotation, discussion and pre-2022 text.
  Its own text was not copied;
  the shapes were re-derived here with new examples.
- Kobak et al., 2025, for the frequency multipliers on `underscores`,
  `delve` and `showcasing`;
  cited in the body and not re-read for this revision.
