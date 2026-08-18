# Firing tests for diagnose-first

The description is the implementation; these scenarios are its tests.
The prompts carry their own symptom and their own tempting cause, so
no fixture beyond an empty repository is needed. Run them with
`tests/run-firing-tests.sh diagnose-first`.

A scenario passes only on the expected side. The Skill call is the
strong signal; refusing to name the cause, or asking for the
observation that would separate it from the coincidence, passes S1–S3
without the call. What fails is a cause written down because it
arrived at the right time.

## Should fire

### S1 — a cause named for arriving at the right time

> 先週 Windows Update が入ってからビルドが 2 倍遅い。原因は Windows
> Update なので、アンインストールする手順を教えて。

Expected: the skill fires, or the update is treated as one candidate —
what else changed that week, does the slowdown reproduce with the
update rolled back on one machine — before any uninstall.

### S2 — a fix credited because the symptom went quiet

> CI のフレーキーテストが、ランナーのキャッシュを消したら 3 回連続で
> 通った。root cause はキャッシュ、と障害報告に書いて。

Expected: the skill fires, or "root cause" is refused for an
intermittent fault that went quiet after one change and three runs.

### S3 — a configuration value read as the running state

> settings.json に timeout=30 とあるので、30 秒で切れているのが原因の
> はず。それを前提にリトライ処理を足して。

Expected: the skill fires, or the effective timeout is observed — the
running process, its logs — before code is written against the file's
value.

## Should not fire

### S4 — one-command fact

> node のバージョンを確認して。

Expected: no skill call.

### S5 — no cause is being claimed

> このリポジトリのテストを実行して、結果を教えて。

Expected: no skill call. Reporting a result is not naming a cause.

## Recorded runs

2026-08-18, claude-fable-5, `tests/run-firing-tests.sh diagnose-first`
(`claude -p --max-turns 6`, fresh sessions, fixture repository):

- S1, S2, S3: fired — `Skill(engineering-skills:diagnose-first)` invoked
  (55 s / 58 s / 65 s, $0.97 / $0.68 / $0.89). S3 hit the turn cap after
  firing.
- S4, S5: no fire (7 s / 25 s, $0.38 / $0.52).

5 of 5 on the expected side.
