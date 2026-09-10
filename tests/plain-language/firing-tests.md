# Firing tests for plain-language

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/announce`.
`announce.md` is a Japanese release note whose sentences join two claims with が and ので,
whose 目的は…ためです never closes, whose の stacks three deep,
and which spells ユーザー two ways and links に こちら.
`release-notes.md` is its English counterpart,
drafted separately from the same facts,
with the same classes of defect in English forms:
claims joined by "but" and "so", "the purpose is so that",
four genitives in a row, "please kindly", "click here",
"log-in" beside "login", and "first of all initially".
`ui.md` holds a handful of Japanese UI strings with the same defects at sentence scale.
Run them with `tests/run-firing-tests.sh plain-language`.

Fixture: `tests/fixtures/announce`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the sentences are split at the claim boundary,
the subject is made to meet its predicate,
the doubled courtesy is reduced, the spelling is fixed one way,
and the link text names its destination.
For S1 and S3 the session should also open `references/japanese.md`;
for S2 it should not need to.

## Should fire

### S1 — a Japanese draft to tidy

> announce.md を読みやすく直して。

Expected: the skill fires,
or the revision splits the multi-claim sentences, fixes 目的は…ためです,
reduces お伺いさせていただきます and ご覧になられて,
settles ユーザー / ユーザ one way,
and replaces こちら with text that names the destination.

### S2 — an English draft to tidy

> release-notes.md reads clumsily.
> Tidy the sentences without changing what they say.

Expected: the skill fires,
or the revision cuts the but/so chain into one claim per sentence,
closes "the purpose is so that", opens the four genitives into a verb,
reduces "please kindly" and "we would like to kindly ask that you please",
settles "log-in" / "login" one way,
drops "first of all initially" and "approximately about",
and replaces "click here" with text that names the destination.

### S3 — UI strings

> ui.md の文言、意味が取りにくいものを直して。

Expected: the skill fires,
or the fixes name the actual defects:「失敗しましたが」の逆接の誤用,
「の」の三連, こちら as link text, and the サーバ / サーバー split.

## Should not fire

### S4 — a value check

> announce.md に書かれている同期間隔の既定値を、
> 設定ファイルの記述と突き合わせて確認して。

Expected: no skill call.
Nothing about the prose is being changed.

### S5 — translation direction

> announce.md を英訳して announce.en.md に保存して。

Expected: no skill call.
The Japanese is not being revised, and the translation is a new text,
not a revision of one.

## Recorded runs

2026-09-04, claude-fable-5,
`MAX_TURNS=10 tests/run-firing-tests.sh plain-japanese` (fresh sessions, announce fixture),
when this skill was `plain-japanese` with a Japanese body and S2 asked for the buried conclusion to be moved:

- S1, S2, S3: fired — `Skill(writing-skills:plain-japanese)` invoked.
- S4, S5: no Skill call.

5/5 on the expected side.
