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

The fixture's own note is `FIXTURE.md`, so that `README.md` can be the
project README GitHub would actually read; `package.json` is there as
a file GitHub reads as a file.

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

> README.md の Contributing と Security の節を、GitHub の画面から
> 辿れる形にして。

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

### S4 — a file GitHub reads as a file

> package.json の description を、もう少し具体的にして。

Expected: no skill call. `package.json` is npm's file, not one of
GitHub's slots, and its content is what changes.

### S5 — an ordinary file

> docs/ に設計メモ design.md を作って、パーサーの状態遷移を書いて。

Expected: no skill call. `docs/design.md` is a plain file GitHub
reads as a file.

## Recorded runs

2026-09-04, claude-fable-5, `MAX_TURNS=10 tests/run-firing-tests.sh
github-paths` (fresh sessions, slots fixture):

- S1, S2, S3 fired (47 s / 62 s / 36 s, $0.57 / $0.64 / $0.54). S1
  `git mv`-ed `FUNDING.yml` into `.github/` and said it is read from
  the default branch only; S2 created `.github/CONTRIBUTING.md` and
  `.github/SECURITY.md`, replaced the README sections with links, and
  chose `.github/` because `CODEOWNERS` already lived there; S3 wrote
  `dist/** linguist-generated` into `.gitattributes`, verified it with
  `git check-attr`, and left the file committed. Each also listed the
  other misplaced files as out of scope and untouched.
- S5: no Skill call.
- S4, as first written, edited the project README's opening line and
  fired: it made the edit as asked, then reported that the fixture's
  `README.md.project` is not a name GitHub reads as a README. That was
  true, and it was the fixture's own slot defect, so the fixture was
  renamed and S4 moved to `package.json`, a file GitHub does not read
  by name.
