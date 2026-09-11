# Firing tests for cognitive-rhythm

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/essay` — an article that is correct and dense and flat:
an agenda opening,「本節では」 at every section head and 「次は〜を見る」 at every foot,
a quotation before the problem it names,
three properties listed and left, uniform assertions,
two sentences about the text itself, one declared device,
and a close that is a general rule.
`reference.md` and `install.md` beside it are pages a reader scans.
Run them with `tests/run-firing-tests.sh cognitive-rhythm`.

Fixture: `tests/fixtures/essay`

Prerequisite: the fresh session reads skills from the plugin cache,
which holds the last pushed commit.
Before the skill is pushed,
copy `skills/cognitive-rhythm` to `~/.claude/skills/cognitive-rhythm` for the run and remove it afterwards.

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the revision opens with a tension rather than an agenda,
replaces 「本節では」 with a question, an unease or an admission,
drops the 「次は〜」 forecasts,
puts the quotation after the failure it names,
lands the three properties on the shop example,
deletes the sentences about the text itself and the declared device,
varies the beat, and closes on the opening scene rather than on a rule.

## Should fire

### S1 — dense and flat

> essay.md、内容は正しくて密度もあるのに、
> 平坦で読み進める気がしないと言われた。
> 直して。

Expected: the skill fires,
or the revision does the things listed above and keeps every fact the article carried.

### S2 — one more section

> essay.md に、無効化の遅延（元データの更新から写しが追いつくまでの時間）
> を扱う節を一つ足して。

Expected: the skill fires,
or the added section opens with a question the reader would ask or an unease the previous section left,
not with 「本節では」; states what the delay is through an instance before a rule;
leaves one question open into the next section;
and does not end with a forecast.

### S3 — the preachy close

> essay.md の「まとめ」、説教くさいと言われた。
> 直して。

Expected: the skill fires,
or the close lands on the shop example or the reader's own experience instead of 「べきである」,
leaves one question open, and does not restate the three headings.

## Should not fire

### S4 — a reference row

> reference.md に `cache.ttl` の行を足して。
> 既定値は `300s`、説明は「エントリの有効期間」。

Expected: no skill call.
A row joins a table.

### S5 — a procedure

> install.md の手順、読みながら手を動かせる形にして。

Expected: no skill call.
A procedure is scanned, not read through; `document-structure` owns it,
and this skill has nothing to add.

## Recorded runs

2026-09-10, claude-fable-5-1,
`MAX_TURNS=10 tests/run-firing-tests.sh cognitive-rhythm` (fresh sessions, essay fixture; the skill was not yet pushed, so `skills/cognitive-rhythm` was copied to `~/.claude/skills/cognitive-rhythm` for the run and removed afterwards):

- S1, S2, S3 fired (133 s / 132 s / 54 s, $1.09 / $1.10 / $0.68).
  S1 replaced the agenda with the shop's wrong-price order and let 「元データは正しかったのに」 carry the piece,
  opened 境界 and 観測 with the question the previous section left,
  deleted every 「次は〜を見る」,
  moved the Karlton quotation after the felt problem,
  landed 粒度・依存・寿命 one by one on the shop scene,
  deleted the sentences about the text and the declared device,
  varied sentence length with 「あったに違いない」-style hesitations,
  and closed on the opening scene with one question left open.
  S2 added 遅延 between 観測 and まとめ,
  entered from what 観測 left (a timestamp on the comparison),
  took its material from the shop example only,
  received and then overturned the reader's 「遅延をゼロにすればよい」,
  ended with two questions open and no forecast,
  updated the agenda's count from three to four,
  and listed the existing sections' 「本節では」 and 「次は〜」 as out of scope.
  S3 landed the three headings on the shop incident,
  replaced 「べきである」 with the trade-off stated as a property of the subject,
  and closed on one open question, naming the same out-of-scope tells.
- S4: no Skill call (17 s).
  One row added.
- S5: no cognitive-rhythm call (65 s).
  The session invoked `document-structure` instead and rewrote the procedure one action per step with its result — the boundary the description draws,
  observed.

5/5 on the expected side.

2026-09-10, claude-fable-5-1, same command,
after the body was rewritten in English with the Japanese forms and examples moved to `references/japanese.md` and the description widened from Japanese to any language:

- S1, S2, S3 fired (94 s / 173 s / 48 s, $0.95 / $1.17 / $0.68),
  and all three opened `references/japanese.md` on their own.
  S1 made the same moves as the first run.
  S2 added 遅延 between 境界 and 観測,
  entered on the question the previous section left (does deciding the unit make the copy fresh at once?),
  took its scene from the shop example,
  planted a belief to break (「次は新しい値が入るに違いない」),
  stepped back for one paragraph, and left a question open at the end.
  S3 landed the three headings on the shop incident,
  replaced the rule with the dependency (without a version nothing else can be checked),
  and closed on one open question,
  naming the remaining tells as out of scope.
- S4: no Skill call (21 s).
  S5: no cognitive-rhythm call (58 s);
  the session invoked `document-structure` and rewrote the procedure.

5/5 on the expected side.

2026-09-11, claude-fable-5-1, same command,
after the description was shortened from 1,115 to 993 characters to fit under Copilot CLI's 1,024-character cap (the Japanese example phrases and the parenthetical explainers went; every trigger stayed):

- S1, S2, S3 fired; S4, S5: no cognitive-rhythm call.

5/5 on the expected side.

