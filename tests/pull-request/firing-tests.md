# Firing tests for pull-request

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/pullreq`:
the log and diff of a feature branch that moved a retry loop from the HTTP client into the queue worker,
beside `NOTES.md`, the author's session notes.
Run them with `tests/run-firing-tests.sh pull-request`.

Fixture: `tests/fixtures/pullreq` (shared with `clean-docs`; the two skills fire on the same body for different reasons, and both firing on S1 is expected)

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the body carries only what the diff cannot show,
links repository code at a commit instead of quoting it,
and names the function and line where a failure occurs.

## Should fire

### S1 — the body from the diff

> commits.txt と diff.patch がこのブランチの変更。
> gh pr create でこのブランチの PR を作って。
> 本文には変更したファイルの一覧と、今回やらなかったことも入れておいて。

Expected: the skill fires,
or the pull request is opened as a draft with a body of at most 120 characters before any full body is written,
and the body then written to a file omits the file list and the not-included list,
and says why the loop moved, which convention it follows,
and when the change shows.
The fixture has no remote, so the command itself fails;
what is judged is the order the session attempts,
read from the transcript.

### S2 — the pasted evidence

> pr-body.md に「動作確認」の節を足して、テストを走らせたときのログ全文を貼っておいて。

Expected: the skill fires,
or the answer replaces the log with one line naming the condition and the observed result.

### S3 — the quoted code

> pr-body.md で、変更前の retry ループのコードをコードブロックで引用して説明して。

Expected: the skill fires,
or the answer links the lines at the commit they were read at instead of quoting them.

### S6 — a reply that asks the reviewer to count

> review.md の 1 つ目のコメントに返す返信を書いて。

Expected: the skill fires,
and the reply first states what the diff makes the worker do — five attempts,
waits of 2, 4, 8 and 16 seconds between them,
and a single attempt on a 4xx response — and then asks only whether what the reviewer saw differed from that.
A reply that asks the reviewer how many requests were sent,
or at what interval, fails.

### S7 — a reply that points at another comment

> review.md の 2 つ目のコメントは 1 つ目と同じ原因だった。
> 2 つ目に返す返信を書いて。

Expected: the skill fires,
and the reply says the cause in one sentence and links the first comment by its permalink.
A reply that only says the answer is in the other comment,
by number or by "above", fails.

## Should not fire

### S4 — a commit message

> diff.patch の変更に対するコミットメッセージを 1 行で書いて。

Expected: no skill call.
A commit subject line is `clean-docs`'s, not a pull request body.

### S5 — read-only

> diff.patch で retry の回数を決めている設定名は何？

Expected: no skill call.
Nothing is being written.

## Recorded runs

### 2026-11-16 — the reply rules (S6, S7)

The section "A reply to a review" was added after two replies in another repository's review went wrong:
one asked the reviewer how many windows were open and what they were titled,
which the code decided,
and one answered a comment only by repeating another comment's number.
That run's transcript was not read here;
whether the skill fired in it is not known.

Each side ran with `MAX_TURNS=10`,
the installed writing-skills plugin disabled and the version under test loaded with `--plugin-dir`:
the original from the commit before the change,
the candidate from the working tree.
S6 and S7 ran three times on each side, S1–S5 once.

| Scenario | Before | After |
|---|---|---|
| S6 | fired 3/3; all three replies stated the attempts and the waits before asking | fired 3/3; the same |
| S7 | fired 3/3; one reply linked the first comment with "answered there" and no cause, two gave the cause | fired 3/3; all three gave the cause in one sentence with the link |
| S1–S5 | 5/5 on the expected side | 5/5 on the expected side |

S6 did not reproduce the failure on this fixture:
the original already put the prediction first,
so the first rule rests on the failed run alone and is unverified here.
The installed plugin reads this working tree directly,
so a "before" run that does not load the original with `--plugin-dir` measures the candidate.
