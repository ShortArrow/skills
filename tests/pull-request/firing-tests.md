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

None yet.
The scenarios were written on 2026-09-17 with the skill and have not been run.
