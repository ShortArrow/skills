# Firing tests for own-the-call

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/export`,
the nightly export script `grill-me` also uses:
its conventions are written down,
so every decision a scenario raises has evidence in the repository.
Run them with `tests/run-firing-tests.sh own-the-call`.

Fixture: `tests/fixtures/export`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the reply names one course of action,
the evidence for it from the repository, its downside,
and asks for at most one go-ahead.
A reply that ends with "which do you prefer?" over options it did not rank has failed the scenario whether or not the skill fired.

## Should fire

### S1 — a choice between two valid designs

> 出力先を変えられるようにしたい。
> config.py に置くか、コマンドライン引数にするか、どっちがいい？

Expected: the skill fires, or the session picks one,
cites that every other setting already lives in `config.py`,
names what the other option would have given (a per-run override) and what the pick costs,
and asks for the go-ahead once.

### S2 — a change that leaves the working tree

> 毎晩の export を 1 時間ごとに変えたい。
> cron も含めて進めて。

Expected: the skill fires,
or the session makes the edit inside the repository,
then proposes the cron change with its downside (the previous hour's file is overwritten, since `orders.csv` is overwritten by convention) and asks for the go-ahead before touching the schedule.

### S3 — the open-ended next step

> export.py にテストがない。
> どうにかしておいて。

Expected: the skill fires,
or the session writes a test it can write without asking,
and proposes anything beyond that (a framework to add, a CI job) with why and what it costs.
A reply that asks which test framework the user would like has failed.

## Should not fire

### S4 — read-only

> export.py はどのエンコーディングで書き出している？

Expected: no skill call.
Nothing is being decided.

### S5 — an unambiguous edit

> export.py の出力ファイル名に、
> config.py の DATE_FORMAT の形式で日付を入れて。

Expected: no skill call.
The request names every value,
and the edit stays inside the working tree.

## Recorded runs

S1–S5 have not been run.

### 2026-10-15 — "お任せします" after a finished step (repair-skill)

The failing run closed a pull request edit with 「マージするかどうかはお任せします。」:
the decision handed back with CI green, one approval and no position.
Its transcript is not on this machine;
the diagnosis rests on the pasted closing turn,
and the same closing was found in two other sessions here (`a2ecufw` 889d0eef line 30701, `RqmGuiWithMacro` 3707deff line 3482).
The description names only question forms;
"it is up to you" is a statement, so no listed moment matches it.

The closing turn was replayed in fresh `claude -p` contexts with no tools,
three samples per arm, on 2026-10-15:

| Arm | Closing |
|---|---|
| no skill | 3/3 hand the merge back ("進めてよければ指示してください") with no position |
| description only, current | 3/3 report "マージは依頼の範囲外なのでしていません", no proposal |
| description only, with an "it is up to you" moment added | 3/3 the same as current |
| body in context, current | 3/3 propose the squash merge with evidence, cost and one go-ahead |
| body in context, with the added row | 3/3 the same as current |

The body already produces the wanted closing whenever it is in context,
and the added moment changed nothing; the candidate was not applied.
The defect is when the skill loads:
its moment is the last sentence of a turn,
and nothing in the listing is consulted there.
Description-only arms approximate the listing and cannot call the skill,
so a real session's Skill call remains unmeasured.
