---
name: unmachine-prose
description: Write technical documentation that does not read as machine-generated. The tells are mostly structural, they differ between English and Japanese, and they are recognised when several stack in one passage rather than from any single word. Use when writing a README, an ADR, a commit message, a design document, a note or a PR body, and when revising prose that reads as generic despite being correct. Also fires when writing or reviewing a bilingual documentation pair, and when delegating any such writing — the language-specific checklists must travel inside the delegation prompt, or they will not be applied.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Unmachine Prose

Nothing here is about disguising authorship.
Every pattern below is a way of saying less than it appears to,
and technical writing is worse for it regardless of who wrote it.

**The tells stack.** A corpus of 7,600 catalogued signals concludes that prose becomes recognisable when signals co-occur,
not from any one of them.
Fix the density, not the dictionary.

**The two languages barely overlap.** English tells are syntactic — trailing participles,
`not X but Y`, em dashes.
Japanese has none of those constructions;
its tells sit in 文末,接続詞 and 段落の閉じ方,
and checking Japanese against the English list finds nothing and proves nothing.
The Japanese list is `references/japanese.md`, written in Japanese.
Read it when the draft is Japanese, and read only it.

---

# English

## Participial trailers

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

> This is **not just** a config change, **it is** a change in ownership.
> The problem is **not** the syntax, **but** the assumption behind it.

The construction manufactures a reveal.
A real contrast occasionally needs it;
three on one page means none of them are real.

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

**Inline-header bullets.** `- **Term**:
description` is the most recognisable shape in machine-written documentation.
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

**Vague attribution.** `Industry reports suggest`, `best practice is`.
Cite it, measure it, or own it as your judgement.

**Hedging without information.** `This may potentially help in some cases` says nothing.
`This helps when the working set exceeds RAM` does.

---

# Japanese

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

**Japanese** — two reads, and a different count;
both are in `references/japanese.md`.

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

Nor are the ordinary errors of a language: a doubled honorific,
a subject that never meets its predicate, の stacked three deep,
one term spelled two ways.
Humans make those at the same rate, and they are `plain-language`'s.
Apply both in turn; mixing them dulls each check.
