# Firing tests for test-design

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/attachment`
— a requirement that names every upper bound and no lower bound, and a
test specification derived from it with the gaps that shape produces —
so the session holds a suite that looks complete and is not. Run them
with `tests/run-firing-tests.sh test-design`.

Fixture: `tests/fixtures/attachment`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; the derived cases without the call still pass S1–S3 when they
name the lower bound, the request with no role, a two-violation input
and the untested table row. What fails is a suite or a verdict that
repeats the shape of the fixture.

## Should fire

### S1 — a test list about to be derived from a requirement

> requirements.md からテスト仕様書を書いて。実務でそのまま使える粒度で。

Expected: the skill fires, or the cases include a lower size bound, a
request with no role, an input that violates two rules at once, and a
test for the forbidden double send.

### S2 — a suite about to be judged complete by its size

> test-spec.md は網羅できてる？足りなければ何が足りないか挙げて。

Expected: the skill fires, or the answer counts classes against the
requirement and names the lower bound, the missing invalid role, the
absent combined violation, the undecidable TC-14 and the state row with
no TC.

### S3 — error paths about to be skipped as unlikely

> test-spec.md の状態遷移のところ、二重送信は UI でボタンを disable
> するから起きない。その行は消して、正常系だけ残して。

Expected: the skill fires, and the row goes as asked with one sentence
naming the class now uncovered (the state machine's own guard against
a second send) and what would reach it. Deleting silently, or refusing,
is the strong signal only.

## Should not fire

### S4 — translation

> requirements.md を英訳して requirements.en.md に保存して。

Expected: no skill call. Nothing is being derived.

### S5 — renumbering

> test-spec.md の TC 番号を 1 から連番に振り直して。

Expected: no skill call. The cases are unchanged.

## Recorded runs

2026-08-26, claude-fable-5, `tests/run-firing-tests.sh test-design`
(`claude -p --max-turns 6`, fresh sessions, attachment fixture):

- S1, S2, S3: fired — `Skill(engineering-skills:test-design)` invoked
  (202 s / 107 s / 62 s, $0.76 / $0.48 / $0.43 per session).
  S1 wrote a specification with a lower size bound, the caller with no
  role, a decision table with two-violation rules, the double send, and
  TC-14 moved to an open question. S2 named every gap listed above.
  S3 deleted the row as asked, kept the failure transitions, and offered
  a TC for the state-machine guard as the alternative; the guard was
  named, the row did not stay.
- S4, S5: no Skill call.

5/5 on the expected side. S3 passes on the strong signal only.

2026-08-27, claude-fable-5, S3 only, after the "When the request
removes a class" section (484acf2): fired (44 s, $0.39); the row was
deleted and the reply named the class now uncovered, the state
machine's own guard, and two paths that reach it (double click before
the disable lands, callers that bypass the View).
