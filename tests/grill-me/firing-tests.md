# Firing tests for grill-me

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/export`:
a small nightly export script whose conventions are all written down in the repository,
so that every gap but one can be closed by reading.
Run them with `tests/run-firing-tests.sh grill-me`.

Fixture: `tests/fixtures/export`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the session reads before asking,
asks at most one question, attaches candidates and a default to it,
and finishes everything the answer does not change.
A session that answers S1 or S3 with a list of questions has failed the scenario whether or not the skill fired.

## Should fire

### S1 — a gap the repository closes

> 営業から、export.py の出力を Excel で開くと文字化けすると言われた。
> 直して。

Expected: the skill fires,
or the session reads `README.md` and `config.py`,
finds that the file is UTF-8 without a byte order mark and is opened in Excel,
switches the encoding to `utf-8-sig` with that reason,
and asks nothing.

### S2 — a gap only the user can close

> 出力先を営業チームの共有フォルダにして。

Expected: the skill fires,
or the session makes the output directory configurable,
keeps `./out` as the default, tests it,
and asks one question for the path,
naming that it is the only thing left.

### S3 — the questionnaire trap

> 実装に入る前に、知っておくべきことを全部質問して。

Expected: the skill fires,
or the session reads the repository first and replies with at most one question,
with candidates, or with none and a statement of what it will assume.
A numbered list of questions is a failure.

## Should not fire

### S4 — an unambiguous edit

> export.py の出力ファイル名に、
> config.py の DATE_FORMAT の形式で日付を入れて。

Expected: no skill call.
Every value the change needs is named in the request or in the code.

### S5 — read-only

> export.py はどのエンコーディングで書き出している？

Expected: no skill call.
Nothing is being decided.

## Recorded runs

None yet.
The scenarios were written on 2026-09-25 with the skill and have not been run.
