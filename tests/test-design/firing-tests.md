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

Expected: the skill fires, or the row stays with a test, because a
forbidden transition is a class and the guard is the thing under test.

## Should not fire

### S4 — translation

> requirements.md を英訳して requirements.en.md に保存して。

Expected: no skill call. Nothing is being derived.

### S5 — renumbering

> test-spec.md の TC 番号を 1 から連番に振り直して。

Expected: no skill call. The cases are unchanged.
