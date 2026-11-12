# Firing tests for storyteller

The description is the implementation; these scenarios are its tests.
Fixture: `tests/fixtures/story` — `notes.md`,
a fictional investigation log in the order things happened,
with a turn in the middle (the leak was not in the process),
beside a short `README.md` and `CHANGELOG.md` for a small tool.
Run them with `tests/run-firing-tests.sh storyteller`.

A scenario passes only on the expected side.
The Skill call is the strong signal.

## Should fire

### S1 — a debugging story about to follow the notes

> notes.md の調査メモをもとに、技術ブログ記事の構成案を作って。

Expected: the skill fires,
or the outline names the turn and does not repeat the notes' order without saying why.

### S2 — a talk

> notes.md の内容で、社内 LT 5 分のスライド構成を考えて。

Expected: the skill fires.

### S3 — a tool introduction

> README.md の prio-run を紹介するブログ記事を書いて。

Expected: the skill fires,
or the article opens on the problem the tool changed rather than its options.

## Should not fire

### S4 — a scanned page

> README.md にインストール手順を足して。

Expected: no skill call.

### S5 — a changelog line

> CHANGELOG.md に 0.3.0 として「CPU の指定を HEAVY_JOB_CPUS から読む」を足して。

Expected: no skill call.

## Recorded runs

2026-10-29, behaviour before the skill, outside the runner:
an investigation log of a real incident,
kept out of the repository because it describes the author's machine,
with `claude -p "notes.md の調査メモをもとに、技術ブログ記事を書いて article.md に保存して。" --max-turns 10`,
three fresh sessions each side.
Its turn sat in the middle:
the tool that seemed frozen was not the thing that froze.

- Without the skill (19:06–19:11):
  3 of 3 put the sections in the log's order;
  2 of 3 stated the answer in the title;
  3 of 3 opened on the first day's incident scene;
  the most surprising finding was one step among the others in all three.
  `cognitive-rhythm` and `unmachine-prose` fired in two of them and changed none of this.
- First candidate (19:16–19:20): 3 of 3 titled the symptom;
  3 of 3 still opened on the incident scene;
  3 of 3 ended on the same question to the reader about their own system.
- Second candidate, with the ending-first skeleton and the ending varied (19:21–19:27):
  3 of 3 titled the symptom; none opened on the incident scene,
  two on the most surprising finding and one on the belief about to break;
  3 of 3 closed by returning to the opening line,
  with no question to the reader.
- A description that named more kinds of piece in its "Use when" (tool, feature and syntax introductions, performance and migration write-ups) and the ending-first skeleton among what it covers (19:39–19:58):
  6 of 6 opened on the incident scene again,
  whether the list of kinds sat in the body before the procedure or after it.
  The earlier description with that list kept in the body (19:58–20:03):
  0 of 3 opened on the incident scene.
  The earlier second-candidate text, rebuilt and run again (19:46–19:51):
  1 of 3.
  The description stays as it was; the kinds of piece live in the body.

2026-10-29, `PLUGIN_DIR=<candidate> MAX_TURNS=6 tests/run-firing-tests.sh storyteller` (`claude -p`, fresh sessions, fixture repository, 20:03–20:09, the version committed):

- S1, S2, S3: fired — `Skill(st-candidate:storyteller)` invoked.
- S4, S5: no fire.

5 of 5 on the expected side.
