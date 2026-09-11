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

> diff.patch の変更をひとつのコミットにするとして、
> コミットメッセージを commit-message.txt に書いて。

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

(none yet)
