# Firing tests for reader-map

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/rationale` — a design note whose sentences parse and whose headings outline,
and which still loses its reader:
the spool is described before it is defined,
a paragraph goes back to the spool without saying so,
the old version's settings screen intrudes on the new rule,
an answering word lands at the end of the next sentence with subject and object swapped,
two causes are written as one, a cause has no mechanism,
"重要なのは" announces a bolded point, one claim is made twice,
and the Windows agent is "confirmed" in a document that later says it was never started.
`settings.md` beside it is a plain settings table.
Run them with `tests/run-firing-tests.sh reader-map`.

Fixture: `tests/fixtures/rationale`

Prerequisite: the fresh session reads skills from the plugin cache,
which holds the last pushed commit.
Before the skill is pushed,
copy `skills/reader-map` to `~/.claude/skills/reader-map` for the run and remove it afterwards;
the runner accepts the skill with or without a plugin prefix.

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the revision defines the spool before describing it,
marks the paragraph that returns to it,
moves or drops the old-version sentence,
brings the answering word to the front, separates the two causes,
adds the mechanism, drops the announcement and the bold,
says the claim once,
and narrows the Windows sentence to what was checked.

## Should fire

### S1 — the draft that still loses its reader

> design-note.md、文も見出しも直したのに、
> 読んだ人が「途中で何の話か分からなくなる」と言う。
> 直して。

Expected: the skill fires,
or the revision puts what the spool is before its properties,
marks or moves the paragraph that returns to the spool inside 重複の扱い,
moves or drops the 旧版 sentence,
brings 再起動前に書き込まれたエントリ to the front of its sentence,
and does not rewrite sentences that already read in one pass.

### S2 — two paragraphs the reader loses

> design-note.md の「重複の扱い」、
> 2 段落目と 3 段落目のあたりで何の話か分からなくなると言われた。
> 直して。

Expected: the skill fires,
or the revision brings 再起動前に書き込まれたエントリ to the front of its sentence as the subject,
and either marks the fsync paragraph as a return to the spool or moves it there,
without rewriting the sentences that already read in one pass.
(Until 2026-09-11 this scenario asked for a retry paragraph to be added from given facts. It fired twice while the fixture was hard-wrapped and stopped firing, three runs in a row, once the fixture was wrapped one sentence per line and read as tidy: a paragraph of supplied facts dropped into a tidy note is not a moment where a reader is lost, so the scenario moved to the two paragraphs where one is.)

### S3 — the argument has holes

> design-note.md の「重複の扱い」と「対応プラットフォーム」、
> レビューで「論理に穴がある」と言われた。
> どこが穴か指摘して直して。

Expected: the skill fires,
or the answer names the two causes written as one,
the cause without a mechanism, the point announced and bolded,
the claim made twice,
and the Windows sentence that the last paragraph contradicts — and fixes each rather than smoothing the prose around them.

## Should not fire

### S4 — a settings row

> settings.md に `send.retry_max` の行を足して。
> 既定値は 5、説明は「送信の再試行回数の上限」。

Expected: no skill call.
A row joins a table that already has the shape a table has.

### S5 — a default value

> settings.md の `send.interval` の既定値が間違っている。`15s` に直して。

Expected: no skill call.
A value changes; nothing about the prose does.

## Recorded runs

2026-09-10, claude-fable-5-1,
`MAX_TURNS=10 tests/run-firing-tests.sh reader-map` (fresh sessions, rationale fixture; the skill was not yet pushed, so `skills/reader-map` was copied to `~/.claude/skills/reader-map` for the run and removed afterwards):

- S1, S2, S3 fired (67 s / 80 s / 122 s, $0.81 / $0.87 / $1.02).
  S1 defined the spool before its properties,
  moved the fsync paragraph back into the spool section,
  dropped the 旧版 sentence as not on the paragraph's subject,
  made 再起動前に書き込まれたエントリ the subject at the front of its sentence,
  split the two causes of slowness into a section of their own with a mechanism for each,
  deleted the Windows claim the last paragraph contradicts,
  and put the objective once at the top instead of announced,
  bolded and restated.
  It flagged the one mechanism it had supplied (転送量が増える) as not in the original.
  S2 added 送信の再試行 between スプール and 重複の扱い,
  opened with what the retry scheme is before the numbers,
  kept to the facts given,
  and named the Windows contradiction as out of scope without touching it.
  S3 listed five holes — the Windows contradiction,
  the two causes written as one, the cause without a mechanism,
  the announced-and-bolded point restated with つまり,
  and one the fixture had not planted on purpose:「一件も失わない」 against the spool section's 古いエントリから捨てる,
  which it narrowed to the priority the text supports — then fixed each and left two design questions (whether 通番 survives a restart, what the fsync choice costs) to the author rather than smoothing them over.
- S4, S5: no Skill call (39 s / 19 s).
  One row added; one value changed.

5/5 on the expected side.

2026-09-10, claude-fable-5-1, same command,
after the body was rewritten in English with the Japanese forms and examples moved to `references/japanese.md` and the description widened from Japanese to any language:

- S1, S2, S3 fired (92 s / 65 s / 136 s, $0.98 / $0.76 / $1.18).
  S1 and S3 opened `references/japanese.md` on their own before editing;
  S2, which only added a paragraph, did not.
  S1 made the same set of moves as the first run.
  S2 placed the retry paragraph after the one on dropping old entries and opened it on the contrast (kept rather than dropped),
  adding only 「捨てずに」 to the facts given.
  S3 found four holes, one new:
  the old version's flaw (double counting) and the redesign's premise (double delivery is absorbed) contradict unless the absorption is conditional on the sequence numbers,
  which it made explicit.
- S4, S5: no Skill call (21 s / 21 s).

5/5 on the expected side.

2026-09-11, claude-fable-5-1, same command,
after the description was shortened from 1,093 to 957 characters to fit under Copilot CLI's 1,024-character cap,
and after the fixture had been wrapped one sentence per line:

- S1, S3 fired; S4, S5: no Skill call.
- S2, as the retry paragraph: no Skill call, twice.
  Restoring the dropped "when writing" trigger (now "when writing or adding to one", 992 characters) and rerunning all five:
  S1, S3 fired, S4, S5 quiet, S2 quiet a third time.
  The sessions placed the supplied facts sensibly and said so,
  but did not treat the note as one a reader gets lost in,
  and the note no longer looks like one:
  since the fixture was wrapped one sentence per line it reads as tidy,
  and a paragraph of given facts dropped into a tidy note is not the moment this skill names.
  The scenario moved to the two paragraphs where a reader is lost (the return to the spool without a signal, the answering word at the end of the sentence) and fired when rerun alone:
  the sentence was reordered with its subject first,
  the fsync paragraph moved to the spool section,
  and the other tells were named as out of scope.

5/5 on the expected side after the move.

