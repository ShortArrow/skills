# Firing tests for consultation-path

The description is the implementation; these scenarios are its tests.
Run each prompt in a fresh session and check whether the skill fires (a `Skill(consultation-path)` call, or the transcript shows the consult-then-refute procedure being followed).

Prerequisite: the plugin cache must contain this skill — refresh the shortarrow-skills marketplace (`/plugin` → update, or restart the session after the marketplace re-syncs) before judging a failure.

`tests/run-firing-tests.sh consultation-path` runs every scenario below and reports the side each landed on.
By hand, one scenario:

```powershell
claude -p "<prompt>" --output-format json > out.json
# then inspect out.json for a Skill tool_use with skill consultation-path
```

A scenario passes only on the expected side;
over-firing on S5–S7 is a failure just as under-firing on S1–S4 is.

## Should fire

### S1 — a second reading is asked for on a design the user already has a view on

The user's own position must be in the prompt,
because the skill exists to keep that position from being overwritten by fluency.

> キャッシュ層を Redis にするか、プロセス内 LRU で足りるか迷ってる。
> 俺はプロセス内で足りると思ってる。
> 他のモデルの意見も聞いて、俺の読みと合わせたい。

Expected: the skill fires.
The consulted reading is obtained and reported **beside** the user's position,
not merged into it, and the agent's own read is given after the user's,
not before.

### S2 — two readings already disagree and the turn is about to pick one

> codex は「この実装は N+1 クエリを踏んでる」と言ってる。
> おまえは踏んでないと読んだんだったよね。
> どっちが正しい？

Expected: the skill fires.
The disagreement is settled by attacking both readings,
not by the agent judging between them,
and "両方とも誤り" / unresolved is an available outcome.

### S3 — a consulted model's output is about to be adopted wholesale

> copilot に設計レビューさせたらこう返ってきた。
> これで進めていい？「現状のレイヤ構成は DDD 違反であり、ドメイン層がインフラ層に依存している。
> リポジトリインターフェースをアプリケーション層に移すべき」

Expected: the skill fires,
or the claim is attacked before it is adopted — specifically,
the named dependency direction is checked against the actual imports rather than taken on the consulted model's word.

### S4 — the user asks for options to compare against their own view

> この移行方針、選択肢を出してくれ。
> 自分の中の意見と突き合わせたい。

Expected: the skill fires.
The options are given without the agent's pick ordered first,
and the agent's own lean is withheld until the user has said theirs.

## Should not fire

### S5 — a fact one command checks

> codex の入ってるバージョン教えて。

The consultee's own version is the clearest case:
it is a fact the binary prints,
and consulting a model about it would be asking a second opinion on `--version`.

Expected: the skill does not fire; the command runs.

### S6 — a single reading with no second opinion asked for and no disagreement

> この関数の計算量を教えて。

Expected: the skill does not fire.
A question with one right answer and no competing reading is answered,
not consulted on.

### S7 — the user asks for the agent's own call, not a panel

> おまえの判断で決めて、理由だけ書いて。

Expected: the skill does not fire.
`own-the-call` governs: the agent decides and reports the evidence.
Spending three model calls on a decision the user delegated is the over-firing failure this scenario measures.
