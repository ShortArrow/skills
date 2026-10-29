# Firing tests for heavy-jobs

The description is the implementation; these scenarios are its tests.
Fixture: `tests/fixtures/heavyjob` — a README that says the suite and the benchmarks fill every core for fifteen and twenty minutes,
and two stand-in scripts that print and exit,
so a run that launches them costs nothing.
Run them with `tests/run-firing-tests.sh heavy-jobs`.

Whether a lowered job keeps the sessions beside it responsive was verified in another repository on a real CI runner,
not here; these scenarios measure only whether the skill fires.

A scenario passes only on the expected side.
The Skill call is the strong signal;
a launch already lowered (`start /low`, `nice`) without the call still passes S1–S3.

## Should fire

### S1 — a full suite about to run at the agent's priority

> テストを全部流して、結果を教えて。

Expected: the skill fires,
or `run-tests.sh` is launched at a lowered priority.

### S2 — the agent about to be lowered instead of the job

> ベンチマークを回すと PC が固まるので、このシェルの優先度を下げてから bench.sh を実行して。

Expected: the skill fires,
or the shell is left as it is and `bench.sh` is launched lowered.

### S3 — a core mask about to be hard-coded

> bench.sh を後ろ半分のコアだけで走らせるコマンドを書いて。

Expected: the skill fires,
or the command reads the machine's setting instead of a mask typed for this machine.

## Should not fire

### S4 — prose only

> README の英語を自然に直して。

Expected: no skill call.

### S5 — read-only, no launch

> run-tests.sh が何をしているか説明して。

Expected: no skill call.
Reading a script is not running it.

## Recorded runs

2026-10-29, `PLUGIN_DIR=<candidate> MAX_TURNS=6 tests/run-firing-tests.sh heavy-jobs` (`claude -p`, fresh sessions, fixture repository, 13:33–13:38, neither variable set):

- S1, S2, S3: fired — `Skill(hj-candidate:heavy-jobs)` invoked.
  S1 read both variables and launched `run-tests.sh` through `cmd //c start "" //b //low … //wait`.
  S2 left the shell as it was,
  launched `bench.sh` at `//low` and said why the shell was not lowered.
  S3 computed the mask from the core count at run time instead of writing a fixed one.
- S4, S5: no fire.

5 of 5 on the expected side.
