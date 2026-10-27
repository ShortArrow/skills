# Firing tests for clean-docs

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/pullreq`:
the log and diff of a feature branch that moved a retry loop from the HTTP client into the queue worker,
beside `NOTES.md`, the author's session notes full of conversation-local labels ("option B", "the H1 finding", "the thing we discussed").
A body written from the notes carries those labels;
a body written from the commits does not.
Run them with `tests/run-firing-tests.sh clean-docs`.

Fixture: `tests/fixtures/pullreq`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the artifact names what changed, why,
and what is left,
is written from the commits and the diff rather than the notes,
and carries none of the notes' labels.

## Should fire

### S1 — the pull request body

> commits.txt と diff.patch がこのブランチの変更で、
> NOTES.md は作業中のメモ。
> この変更の PR 本文を書いて pr-body.md に保存して。

Expected: the skill fires,
or the body says what changed (the loop moved, the two settings, 4xx no longer retried, the raise instead of the returned response),
why (the decision belongs where the item is handled),
and what is left (give-up metrics), from the commits and the diff;
"option B", "H1" and "the thing we discussed" do not appear.

### S2 — the commit message

> diff.patch の変更をひとつのコミットにするとして、コミットメッセージを commit-message.txt に書いて。

Expected: the skill fires,
or the message carries a one-line subject and a body that says why in one or two sentences,
without the notes' labels and without a list of files.

### S3 — the follow-up issue

> NOTES.md の「TODO later」を issue にしたい。
> issue の本文を issue.md に書いて。

Expected: the skill fires, or the issue stands alone: what is missing,
where in the code, what done looks like,
with no reference to this PR by "this PR" or to the notes.

## Should not fire

### S4 — a count

> diff.patch で追加された行と削除された行の数を数えて。

Expected: no skill call.
A number is read off a file.

### S5 — a sort

> commits.txt の行を、コミットの種類（feat, fix, refactor, test）ごとにまとめ直して commits-by-type.txt に保存して。

Expected: no skill call.
Lines are regrouped; nothing durable is written for a reader.

## Recorded runs

2026-09-11, claude-fable-5-1,
`MAX_TURNS=10 tests/run-firing-tests.sh clean-docs` (fresh sessions, pullreq fixture, plugin cache at 4bbd905):

- S1, S2, S3 fired ($0.85 / $0.76 / $0.82).
  S1 wrote the body from the commits and the diff with what changed, why,
  the behaviour changes for callers and what is left,
  and said it had left the notes' labels out;
  the saved body carries none of them.
  S2 wrote a Conventional Commits subject with a body in the order now,
  before and why it was a problem, what the tests guarantee.
  S3 wrote an issue that stands alone:
  the behaviour as the diff shows it, the gap, a proposal,
  with no "this PR".
- S4, S5: no Skill call ($0.56 / $0.51).
  S4 noted that diff.patch does not `git apply` (the hunk counts are illustrative),
  which the fixture description now says.

5/5 on the expected side.

2026-10-27, claude-opus-5-5, the ADR policy as record 0000.
Prompt 「このリポジトリで ADR を始めて。」 in a fresh repository holding only a one-line README,
`claude -p --permission-mode acceptEdits --max-turns 15`,
three runs per arm;
the candidate was loaded with `--plugin-dir` and the installed writing-skills disabled.

- Before (plugin cache at 7f34d86): clean-docs fired 3/3.
  All three wrote the policy as `0001-record-architecture-decisions.md`,
  frozen once accepted and superseded by a new record,
  with an index in `docs/adr/README.md` and a `template.md`.
- After (the three lines on record 0000 added to "Design intent is a living document"):
  clean-docs fired 3/3.
  All three wrote the policy as record 0000 and said decision records start at 0001,
  kept the frozen records and the index,
  and placed standing reasons in living documents;
  one created `docs/design-intent.md`.
  None wrote a `template.md`,
  and one wrote in Japanese after the Japanese prompt;
  three runs a side do not tell whether either difference comes from the change.

2026-10-27, claude-opus-5-5, ADRs rewritten in place.
The candidate moved the ADR from the frozen records to the living design intent:
one file per decision, rewritten when the decision changes,
the replaced design moved to Alternatives, no date,
and a status of Draft, Accepted or Withdrawn.
It was loaded with `--plugin-dir`,
with the installed writing-skills disabled.

- The same ADR prompt, three runs: clean-docs fired 3/3.
  All three wrote the policy as record 0000, rewritten in place,
  with no date,
  the three statuses and an Alternatives table that turns down the frozen chain;
  two said a judgment only its moment explains goes in a commit message.
  The version before it froze accepted records in 3/3.
- `MAX_TURNS=10`, S1 to S5 once each: S1 and S3 fired,
  S4 and S5 stayed silent, S2 did not fire.
- S2 three more times on each side:
  the installed version (9ebb928) did not fire in 0/3,
  the candidate fired in 3/3, so 3/4 with the run above.
  Every run in both arms wrote a one-line Conventional Commits subject with a body.
