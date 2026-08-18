# Firing tests for tidy-first

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/leap`,
committed once, so a session can be asked for a commit that mixes a
structural move with a behaviour change. Run them with
`tests/run-firing-tests.sh tidy-first`.

A scenario passes only on the expected side. The Skill call is the
strong signal; two commits where one was asked for — the rename green
on its own, the fix in the next — passes S1–S3 without the call. What
fails is a single diff in which both the shape and the behaviour moved.

## Should fire

### S1 — a fix and a rename in one commit

> is_leap の 1900 年バグを直して、ついでに関数名を is_leap_year に
> 変えて、1 コミットにまとめて。

Expected: the skill fires, or the rename and the fix land as separate
commits with the reason stated.

### S2 — a move plus a signature change

> calc.py の関数を leap.py に移動して、days_in_february は year の
> 代わりに date を受け取るように変えて。まとめてコミットして。

Expected: the skill fires, or the move (tests untouched, still green)
is committed before the signature change (tests edited).

### S3 — cleanup "while here" inside a bug fix

> is_leap の 1900 年バグを直して。ついでに周りのコードも見やすく
> 整理しておいて。

Expected: the skill fires, or the "整理" is deferred to its own commit
or declined for this diff.

## Should not fire

### S4 — a pure structural change

> calc.py の関数を leap.py に移動して。振る舞いは変えないで。

Expected: no skill call. Nothing is being mixed; the request is already
one tidy.

### S5 — read-only

> git log を見せて。

Expected: no skill call.

## Recorded runs

2026-08-18, claude-fable-5, `tests/run-firing-tests.sh tidy-first`
(`claude -p --max-turns 6`, fresh sessions, fixture repository):

- S1, S2, S3: fired — `Skill(engineering-skills:tidy-first)` invoked
  (77 s / 106 s / 83 s, $0.75 / $0.77 / $0.77). S1 and S3 then hit the
  turn cap before committing; the fire is what the scenario measures,
  and it came before any edit.
- S4, S5: no fire (51 s / 8 s, $0.64 / $0.38). S4 moved the functions
  without invoking the skill — a pure move is already one tidy.

5 of 5 on the expected side.
