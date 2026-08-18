# Firing tests for tdd-cycle

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/leap` —
`calc.py` with `is_leap` wrong for 1900, and a suite that does not
cover that class — so the session holds a bug with no failing test in
hand. Run them with `tests/run-firing-tests.sh tdd-cycle`.

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; the prescribed procedure without the call — a failing test
written and run before the edit — still passes S1–S3. What fails is an
edit made, or a fix declared, with no test that was red first.

## Should fire

### S1 — a bug about to be fixed at the suspected line

> calc.py の is_leap(1900) が True を返してしまう。該当行を直して。

Expected: the skill fires, or a test asserting `is_leap(1900)` is
False is added and seen to fail before `calc.py` changes.

### S2 — a change about to be verified by running and reading

> calc.py の is_leap を 400 年ルール対応に書き換えたので、python で
> 何年か試して出力を見て正しいか確認して。

Expected: the skill fires, or the confirmation is an assertion in the
suite rather than printed values read by eye.

### S3 — "tests later" about to enter a plan

> calc.py に days_in_month(year, month) を足す実装計画を書いて。テストは
> 後で足す方針で。

Expected: the skill fires, or the plan puts the failing test before the
implementation and says why "later" was declined.

## Should not fire

### S4 — no behaviour to assert

> calc.py の各関数に docstring を書いて。

Expected: no skill call. A docstring has no failing state.

### S5 — read-only

> このリポジトリのテストを実行して、結果を教えて。

Expected: no skill call, no ceremony. Running the suite is not a change.

## Recorded runs

2026-08-18, claude-fable-5, `tests/run-firing-tests.sh tdd-cycle`
(`claude -p --max-turns 6`, fresh sessions, fixture repository):

- S1, S2, S3: fired — `Skill(engineering-skills:tdd-cycle)` invoked
  (44 s / 54 s / 61 s, $1.08 / $0.74 / $0.70 per session).
- S4, S5: no fire (38 s / 28 s, $0.57 / $0.53).

5 of 5 on the expected side. Cost per session is dominated by the
system prompt: every installed skill's description rides along, so a
one-line prompt is ~37k input tokens before the model has said a word.
