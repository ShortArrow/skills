# Firing tests for repair-skill

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/brokenskill`:
a project whose `daily-summary` skill fetches one page of 100 records and stops,
repeats the same `--limit 100` command in its body's example,
and reported success on a run that fetched 100 of 125 issues;
`session.jsonl` is that run's transcript.
Run them with `tests/run-firing-tests.sh repair-skill`.

Fixture: `tests/fixtures/brokenskill`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the answer reads the transcript before editing,
names the transcript line and the skill line of the defect,
fixes both the script and the body's example,
and runs the 125 and 25 record cases before and after.

## Should fire

### S1 — the session id

> session.jsonl が失敗したセッションのログ。
> daily-summary が失敗しているようなので直しておいて。

Expected: the skill fires, or the answer reads the steps first,
names the paging defect at the fetch step,
fixes `fetch.py` and the example in SKILL.md,
and shows 125 and 25 both fetched after the change.

### S2 — the script-only fix

> fetch.py が 1 ページ目で止まる。
> 全ページ取るように直して。

Expected: the skill fires,
or the answer fixes the script and also the `--limit 100` example in SKILL.md,
and reruns the case that used to pass.

### S3 — the flaky skill

> daily-summary が昨日は動いたのに今日は途中で止まった。
> 何が違うのか調べて直して。

Expected: the skill fires,
or the answer opens session.jsonl rather than patching the step that happened to fail.

## Should not fire

### S4 — a new skill

> issue にラベルを付ける skill を .claude/skills/label-issues に新しく作って。

Expected: no skill call.
Nothing has failed; there is no run to read.

### S5 — read-only

> daily-summary の SKILL.md は何をする手順？

Expected: no skill call.
Nothing is being repaired.

## Recorded runs

None yet.
The scenarios were written on 2026-09-17 with the skill and have not been run.
