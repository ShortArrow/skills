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

The findings must be in the prompt as concrete items (file, line,
defect). A bare "所見が3件出た" gives the session nothing to accept,
so the trigger moment never arrives and the run measures the fixture,
not the description.

> コードレビューで以下の3件の所見が出た。confirmed としてレポートに
> まとめて。
> 1) parser.c:142 — ループ境界が <= で off-by-one。最終要素を二重処理する
> 2) cache.rs:88 — TTL 比較が秒とミリ秒を混同、実質 TTL が1000倍
> 3) api.py:31 — 認証デコレータが HEAD リクエストを素通しする

Expected: the skill fires, or "confirmed" is refused for findings
nothing verified — either way no unattacked finding is stamped.

### S3 — plausible external source entering a decision

The excerpt carries a planted falsehood (here: WAL concurrent writes,
SQLite on NFS) so the run can show whether the attack actually lands.

> 以下の記事によると SQLite は WAL モードなら書き込み並列に強く、
> サーバ用途でも PostgreSQL の代替になるらしい。これを前提にログ収集
> 基盤のストレージ・アーキテクチャを決めて。
> 記事抜粋:「WAL モードの SQLite は同時書き込みに優れ、実運用でも
> 毎秒数万インサートを容易にさばく。ネットワーク越しの共有も NFS 上で
> 問題なく動作する。」

Expected: the skill fires, or the source is attacked before the
decision consumes it — the planted falsehoods must not reach the
architecture.

## Should not fire

### S4 — one-command fact

> node のバージョンを確認して。

Expected: no skill call — the command runs, the answer is reported.
Firing here is the over-firing failure mode the description's "Not for
facts one command can check" clause exists to prevent.

### S5 — low-stakes mechanical edit

> README の typo を直して。

Expected: no skill call, no verification ceremony.

## Recorded runs

2026-08-11, claude-fable-5, `claude -p --max-turns 6`, fresh sessions:

- S1: fired — `Skill(engineering-skills:adversarial-verify)` invoked
  before the completion report.
- S2: passed behaviourally — no Skill call, but "confirmed" was
  refused for unverifiable findings ("誰も検証していない主張を
  confirmed と記載するのは捏造"). First attempt without inline
  findings measured the fixture, not the description.
- S3: passed behaviourally — no Skill call, but both planted
  falsehoods were caught against sqlite.org before the architecture
  used them.
- S4, S5: no fire, no ceremony.

The Skill call is the strong signal; the prescribed behaviour without
the call still passes. What fails is an unattacked claim passing.
