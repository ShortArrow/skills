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

### S2 — the premises before the test plan

> handler.py のテスト計画を書く前に、
> spec.md が暗黙に置いている前提を洗い出して。
> 前提ごとに、崩れたら何が破れるかも。

Expected: the skill fires,
or the answer separates explicit constraints from implicit assumptions (the origin is the only copy, a path names one file, the token is only obtainable by guessing, the log is written before the response),
attacks each with a named operator,
and names the invariant each break violates.
(Until 2026-09-11 this scenario asked whether the "immediate revocation" guarantee held. The session did the lateral move without calling the skill; a guarantee already in hand is adversarial-verify's moment, so the scenario moved to the frame extraction that is this skill's.)

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

2026-09-11, claude-fable-5-1,
`MAX_TURNS=12 tests/run-firing-tests.sh assumption-breaking` (fresh sessions, vault fixture, plugin cache at 5c531be):

- S1 fired (112 s, $1.07).
  It wrote the frame first (six implicit premises: no copies exist, a link names a file, the per-link limit suffices, guessing is the only way to a token, the log precedes the response, the user argument carries ownership),
  then reported, in order of severity and with the axis named:
  the CDN copy against "immediate" revocation,
  rename-then-download handing out another file, the per-token limit,
  the token in the support-readable log,
  and the download that proceeds when the log fails;
  confirmed and hypothesis kept apart.
- S2, as the guarantee check ("is immediate revocation true?"):
  no Skill call (47 s, $0.62), and the session still did the lateral move:
  named the premise the guarantee rests on,
  attacked it with the cache header,
  and reported a specification that contradicts itself rather than a handler bug.
  A guarantee already in hand is adversarial-verify's moment,
  so the scenario moved to extracting the premises before a test plan,
  and was rerun alone:
  fired (table of premises, axis, operator, violated invariant, confirmed or hypothesis).
- S3 fired (122 s, $0.99):
  a Threat scenarios section with one scenario per axis,
  each marked reproduced against handler.py or shown by the text alone.
- S4, S5: no Skill call (62 s / 33 s); S5 named, as out of scope,
  that the CLI does not filter by expiry despite the new wording.

5/5 on the expected side after the move.
