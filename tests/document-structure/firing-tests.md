# Firing tests for document-structure

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/guide` —
a setup guide that opens with the tool's history, whose headings are
"Overview", "Details" and "Notes", whose procedure is one paragraph
with three actions, whose four platforms with three fields each are
bulleted, and which calls the config file by two names. `CHANGELOG.md`
beside it is a plain, well-formed file. Run them with
`tests/run-firing-tests.sh document-structure`.

Fixture: `tests/fixtures/guide`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; without it, S1–S3 still pass when the revision moves the point
to the top, names the sections, numbers the steps and tabulates the
platforms rather than polishing sentences in place.

## Should fire

### S1 — the draft to make usable

> setup-guide.md、文章は間違ってないのに使いにくい。構成を直して。

Expected: the skill fires, or the revision leads with what to do,
replaces the three generic headings with ones that read as an
outline, splits the install/configure paragraph, numbers the
procedure one action per step, and turns the platform bullets into a
table.

### S2 — the procedure

> setup-guide.md のインストール手順、読みながら手を動かせる形にして。

Expected: the skill fires, or the answer produces numbered steps with
one action each, the result stated after the action that has one,
and the prerequisite (Node 20) before step 1.

### S3 — one more section

> setup-guide.md に、アンインストールの方法を書いた節を足して。

Expected: the skill fires, or the added section gets a heading that
names it, a first sentence that states what the reader ends up with,
and steps rather than a paragraph — and does not become a fourth
"Notes".

## Should not fire

### S4 — the changelog entry

> CHANGELOG.md に 0.3.1 の項を足して。内容は「空の設定ファイルで
> --strict が誤ってエラーになる不具合を修正」。

Expected: no skill call. The file's shape is already the shape a
changelog has, and one entry is being added to it.

### S5 — a date correction

> CHANGELOG.md の 0.2.1 の日付が間違っている。2026-07-14 に直して。

Expected: no skill call. A value changes; nothing about structure does.

## Recorded runs

2026-09-04, claude-fable-5, `MAX_TURNS=10 tests/run-firing-tests.sh
document-structure` (fresh sessions, guide fixture):

- S1, S2, S3 fired (56 s / 53 s / 56 s, $0.70 / $0.69 / $0.68). S1
  and S2 both replaced Overview / Details / Notes with headings that
  read as an outline (Prerequisites, Supported platforms, Install…,
  Config file, Exit codes), moved the Node requirement ahead of the
  procedure, numbered the steps one action each with the result after
  the action, tabulated the four platforms, unified "settings file"
  and "config" to one name, and cut the history to the one sentence a
  reader needs. Neither dropped a fact. S3 added an "Uninstall
  tinyparse" section with a first sentence stating the end state, four
  numbered steps and "Optional:" at the start of the optional ones,
  declined to invent a config file name the guide never gives, and
  left the three generic headings alone as out of scope.
- S4, S5: no Skill call.

5/5 on the expected side.
