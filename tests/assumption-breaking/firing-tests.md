# Firing tests for assumption-breaking

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/vault`:
a share-link service whose specification and handler agree,
and whose goal still fails.
Revocation is "immediate" while the CDN header lets a copy serve for an hour;
a link stores a path, so rename followed by download hands out a different file;
the rate limit is counted per token;
tokens "cannot be guessed" and are written in full to a log that support staff read;
and a failing log service lets a download proceed unlogged.
`cli.py` is an unrelated listing tool for the scenarios that must not fire.
Run them with `tests/run-firing-tests.sh assumption-breaking`.

Fixture: `tests/fixtures/vault`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal; without it,
S1–S3 still pass when the answer lists the specification's premises before attacking them,
walks more than one axis (time, ordering, actor, resource, dependency),
names the cases where every component is correct and the goal fails,
and separates what it reproduced from what it only hypothesises.

## Should fire

### S1 — what the author did not think of

> spec.md と handler.py を読んで、設計者が想定していない壊れ方を探して。

Expected: the skill fires,
or the answer names the CDN cache against "immediate" revocation,
rename-then-download as two valid operations that break the link's meaning,
the per-token rate limit, and the token in the support-readable log,
sorted into confirmed and hypothesis, with the axes named.

### S2 — a guarantee to check

> spec.md の「失効は即時」という保証は成り立っている？確認して。

Expected: the skill fires,
or the answer writes down what "immediate" rests on (the origin is the only copy),
attacks that premise with the cache header,
and reports the one-hour window as a specification-satisfied,
goal-violated case rather than a handler bug.

### S3 — a threat section

> spec.md に脅威シナリオの節を足して。

Expected: the skill fires,
or the added section covers at least four distinct axes rather than four variants of token theft,
includes the everything-correct failures,
and marks which scenarios were reproduced against handler.py and which are hypotheses.

## Should not fire

### S4 — an option on the CLI

> cli.py に `--json` オプションを足して、
> リンクを JSON で出せるようにして。

Expected: no skill call.
A feature is added to a tool that has no frame worth attacking.

### S5 — a wording fix

> cli.py の argparse の description を "List share links" から "List active share links" に変えて。

Expected: no skill call.
A string changes.

## Recorded runs

(none yet)
