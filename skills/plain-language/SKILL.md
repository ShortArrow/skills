---
name: plain-language
description: |
  Sentences that read one way, triggered by the moments that produce ones that do not: about to join two claims with "but" or "so" (が, ので) in one sentence, about to let a subject and its predicate disagree across a long modifier, about to place a modifier where it could attach to two heads, about to stack three genitives ("the X of the Y of the Z", の three deep), about to spell the same term two ways in one document, about to add a second courtesy marker to a request, about to write "here" (こちら) as the text of a link, or about to say a thing twice in one phrase ("first of all initially", 約 10 分程度). A reader scans before reading, and a sentence whose parse is ambiguous is wrong even when every word is right. Use when writing or revising prose in any language — a README, an announcement, a UI string, an email, an article — and when reviewing a translation. Japanese has its own forms of each of these, and the body says where they are.
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Plain language

A reader does not start at the top.
They scan the headings and the first lines,
decide whether the page is worth reading, and only then read.
So a text fails in two ways: **a sentence that is misread**,
and **a structure that is not read**.
Both can be fixed, and the fixes differ.
This skill takes the sentence; `document-structure` takes the page.

The rules below are practice, and the same in every language.
What differs by language is in the layer files,
which carry their own sources.

## Language layers

The rule is language-neutral; what differs by language is layered on,
not mixed in.
Japanese: read `references/japanese.md` before writing or revising Japanese.
It carries the forms that exist only there and worked examples in Japanese.
A draft in another language uses the body alone.

## The moments this replaces

| About to… | Instead |
|---|---|
| join two claims in one sentence with "but", "so", "and" (が, ので) | one sentence per claim. A sentence stretched by a connective always reads once it is cut |
| put a long modifier between the subject and its predicate | read the subject and the predicate alone. If they do not agree, the sentence is broken, not the modifier |
| stack three genitives ("the review of the settings of the new platform") | two at most; open the third into a verb ("we reviewed the new platform's settings") or cut the sentence |
| place a modifier where it can attach to two heads | put it next to the head it belongs to. Long modifiers first, short ones last |
| add a second courtesy marker ("we would like to kindly ask that you please") | one marker per sentence. Most sentences need none |
| spell one term two ways ("log in" / "login", ユーザー / ユーザ) | pick one, apply it everywhere, and record the choice in the repository |
| put the conclusion in the last paragraph | first. The reader decides after the conclusion whether to read the reasons (`document-structure`) |
| write "here" (こちら) as the text of a link | the link text names its destination. A scanning reader picks up only the links |
| double a meaning ("first of all initially", "approximately about ten minutes") | drop the duplicate. If the meaning did not shrink, the word was spare |

## One sentence says one thing

A long sentence is not hard to read because it is long.
It is hard because **the claims are joined by connectives,
and the reader has to decide where each one ends**.

> The config file is read at startup,
> but environment variables take precedence when set,
> so in production we recommend overriding it with environment variables.

That is three facts in one sentence.
Cut, and which is a rule and which is advice becomes visible:

> The config file is read at startup.
> When an environment variable is set, it takes precedence.
> In production, override the file with environment variables.

"But" is the dangerous one: it can mark a contrast or merely continue,
and the reader decides which while reading.
For a contrast, say "however" or "yet"; for a continuation,
cut the sentence.

## The subject meets its predicate

When the modifier grows long,
the writer loses the skeleton of the sentence too.

> The purpose of this feature is so that users can start work without changing any settings.

"The purpose is so that" does not close.
Take the skeleton out and it shows at once:
"the purpose is to let users…" or "the feature exists so that users…".

The check is mechanical. **Read the subject and the predicate aloud,
and skip every modifier in between.**

## A modifier attaches to one head

Free word order lets a modifier reach two heads.

> We wrote the new authentication platform setup guide.

Is the platform new, or the guide?
Obvious to the writer, opaque to the reader.
Move the modifier next to its head, punctuate, or reorder.

- **Next to the head it modifies.** "the setup guide for the new authentication platform"
- **Long modifiers first, short ones last.** Reversed,
  the short one floats free.
- **Punctuate where the attachment changes.** A comma placed for breath moves the attachment.

Stacked genitives are the same problem.
"The evaluation of the performance of the new product of our company" strings ownership,
membership and object on one preposition,
and the reader guesses which binds to which.
A verb settles it: "how our new product performed when we evaluated it".

## Courtesy is not stacked

A second courtesy marker reads as the writer's nervousness,
not as politeness.

| Stacked | Plain |
|---|---|
| we would like to kindly ask that you please contact support | please contact support |
| please kindly refer to the documentation | see the documentation |
| we humbly request your kind cooperation | please cooperate |

Technical writing rarely needs more than one marker,
and every marker added takes information out of the sentence.
Japanese has a whole grammar of these; the layer file carries it.

## One spelling per term

A term spelled two ways reads as two things.
The axes are few: hyphenation ("e-mail" / "email"),
compound spacing ("log in" / "login"), capitalisation, abbreviation,
and the numeral versus the word.
Either choice is fine; **not choosing is the only error**.
Record the choice in the repository's documents and keep it in the present tense,
as `clean-docs` says.

## Built to be scanned

Conclusion first, headings that carry the thread on their own,
one topic per paragraph.
Those three are the same in every language,
and `document-structure` holds them, with numbered procedures,
tables against bullets, and heading depth.
One thing this skill adds at the sentence scale:
**a list's items share one grammar**.
Noun phrases with noun phrases, sentences with sentences ending alike;
a list that mixes them makes unlike things look parallel.

## What not to fix

A colloquial sentence whose meaning is single.
The vocabulary of the field.
A term repeated on purpose,
because the synonym would read as a different thing.
A long sentence that says one thing and never crosses a connective.

**Plain is not short.** Plain is not misread.

## Connections

`unmachine-prose` is a different axis:
it removes the signs of machine writing (uniform sentence endings, personification carried in from another language, filler after the content ran out).
This skill fixes errors humans make at the same rate;
a doubled courtesy is not a machine tell, and a plain,
correct sentence is not `unmachine-prose`'s business.
Apply both in turn; mixing them dulls each.

Where a document belongs (living and present-tense, or a frozen record) is `clean-docs`.
Keeping a Japanese page and its counterpart in step is `i18n-parity`.
Whether a claim may be made at all is `regulated-claims`.
Whether the reader can place each sentence on the map of what came before is `reader-map`.
