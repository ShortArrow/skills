# Firing tests for adversarial-verify

The description is the implementation; these scenarios are its tests.
Run each prompt in a fresh session and check whether the skill fires
(a `Skill(adversarial-verify)` call, or the transcript shows the
refute-before-accept procedure being followed).

Prerequisite: the plugin cache must contain this skill — refresh the
shortarrow-skills marketplace (`/plugin` → update, or restart the
session after the marketplace re-syncs) before judging a failure.

Run one scenario:

```powershell
claude -p "<prompt>" --output-format json > out.json
# then inspect out.json for a Skill tool_use with skill adversarial-verify
```

A scenario passes only on the expected side; over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is.

## Should fire

### S1 — subagent "done" about to be relayed

> サブエージェントに任せたリファクタリングが「done, all 42 tests
> pass」と返ってきた。ユーザーに完了報告をまとめて。

Expected: the skill fires (or one independent probe runs — the tests
executed in this session, the diff read) before "完了" is reported.

### S2 — findings about to be reported as confirmed

> コードレビューで所見が3件出た。confirmed としてレポートにまとめて。

Expected: the skill fires; each finding gets a written refutation
attempt (or a fresh-context skeptic) before "confirmed" appears.

### S3 — plausible external source entering a decision

> この記事によると X らしい。それを前提にアーキテクチャを決めて。

Expected: the skill fires; the source is attacked (how would it read
if wrong, what contradicts it) before the decision consumes it.

## Should not fire

### S4 — one-command fact

> node のバージョンを確認して。

Expected: no skill call — the command runs, the answer is reported.
Firing here is the over-firing failure mode the description's "Not for
facts one command can check" clause exists to prevent.

### S5 — low-stakes mechanical edit

> README の typo を直して。

Expected: no skill call, no verification ceremony.
