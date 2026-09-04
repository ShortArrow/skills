# Firing tests for github-paths

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/slots` —
a repository whose special files are all present and mostly somewhere
GitHub does not look: `FUNDING.yml` and `dependabot.yml` at the root,
`CITATION.cff` under `docs/`, two `CODEOWNERS` that disagree,
contributing and security guidance inside the README, and a minified
bundle with no `.gitattributes`. Run them with
`tests/run-firing-tests.sh github-paths`.

Fixture: `tests/fixtures/slots`

The fixture keeps its own README under `README.md.project`; the runner
copies the tree as is, and the scenarios name that file where it
matters.

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; without it, S1–S3 still pass when the answer names the path
GitHub reads and moves or marks the file rather than rewriting it.

## Should fire

### S1 — the button that never appeared

> スポンサーボタンが出ない。FUNDING.yml は書いてあるはずなんだけど、
> 確認して直して。

Expected: the skill fires, or the answer moves the file to
`.github/FUNDING.yml` and says it is read from the default branch
only, rather than editing its contents.

### S2 — guidance the site cannot find

> README.md.project の Contributing と Security の節を、GitHub の
> 画面から辿れる形にして。

Expected: the skill fires, or the answer creates `CONTRIBUTING.md`
and `SECURITY.md` in one of the three recognised locations and points
the README at them, and mentions which location wins when two exist.

### S3 — review drowned by a bundle

> dist/bundle.min.js の差分がレビューのたびに数千行出る。レビューから
> 消したい。

Expected: the skill fires, or the answer adds `dist/**
linguist-generated` to `.gitattributes` and keeps the file committed,
instead of deleting it or adding it to `.gitignore`.

## Should not fire

### S4 — the text of the README

> README.md.project の一行目の説明文を、もう少し具体的にして。

Expected: no skill call. The README's content is being edited, not its
placement, and no slot is involved.

### S5 — an ordinary file

> docs/ に設計メモ design.md を作って、パーサーの状態遷移を書いて。

Expected: no skill call. `docs/design.md` is a plain file GitHub
reads as a file.
