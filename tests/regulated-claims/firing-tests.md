# Firing tests for regulated-claims

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/landing`
— a cushion's product page carrying a physiological claim, a No.1 line,
a before and after, a testimonial doing the work of evidence, a named
competitor comparison, a reference price nobody paid, a chart lifted
from a government report, and a named reviewer whose photo was taken
from her social account. `notes.md` records what the team actually has,
and it contradicts the page almost line for line. Run them with
`tests/run-firing-tests.sh regulated-claims`.

Fixture: `tests/fixtures/landing`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; without it, S1–S3 still pass when the answer names the claim
classes rather than only the missing evidence, and separates what a
measurement could fix from what no measurement rescues.

## Should fire

### S1 — a page about to ship

> landing.md をレビューして、公開前に直すべきところを挙げて。

Expected: the skill fires, or the review names the governed classes —
the health claim against an undeclared classification, No.1 without a
stated basis, the before-and-after presented as typical, the
testimonial carrying the efficacy claim, the untested competitor
comparison, the reference price never charged, the lifted figure, and
the named person whose consent covers a different use.

### S2 — polishing the strongest line

> 「肩こり・腰痛が改善します」の見出し、もっと刺さる表現にして。

Expected: the skill fires, or the answer says the sentence cannot be
strengthened because its class is the problem: what may be said is
fixed by how the product is classified, and the fix is a different
claim rather than a better adjective.

### S3 — the number looks fine

> No.1 の根拠はアンケートにあるので、そのまま出して問題ないか確認して。

Expected: the skill fires, or the answer separates the two failures:
38 self-selected buyers with no comparative question do not support a
ranking claim, and even with a survey the basis, scope and date belong
next to the claim.

## Should not fire

### S4 — a factual product note

> spec.md の中材の記述を、notes.md にある「三層構造は自社設計」に
> 合わせて補って。

Expected: no skill call. The spec sheet asserts dimensions and
materials, and describing the construction makes no governed claim.

### S5 — formatting

> spec.md の表の列幅がそろっていないので整形して、最後の 2 文を
> 表の下の注記として箇条書きにして。

Expected: no skill call. Nothing in the file is a claim, and nothing
about it changes.

The first pair of these scenarios pointed at `landing.md`, and both
sessions fired: they completed the edit and then listed the governed
claims elsewhere on the page as out of scope. That is the skill
working, not over-firing, so the negatives moved to the file that
carries no claim.

## Recorded runs

2026-09-04, claude-fable-5, `MAX_TURNS=10 tests/run-firing-tests.sh
regulated-claims` (fresh sessions, landing fixture):

- S1, S2, S3 on 5c33223: fired — `Skill(writing-skills:regulated-claims)`
  invoked. S1 named the classes rather than the missing evidence; S2
  said the headline's class is the problem and no adjective fixes it;
  S3 separated "38 self-selected buyers cannot support a ranking" from
  "a survey still needs its basis beside the claim".
- S4, S5 on 5c33223, pointed at `landing.md`: both fired. Each did the
  requested edit and listed the governed claims elsewhere as out of
  scope, and one demoted a headline while formatting. The first
  behaviour is the skill working; the second is the scope rule
  a15412a added.
- S4, S5 on a15412a, pointed at `spec.md`: no Skill call (25 s / 58 s,
  $0.29 / $0.40).

5/5 on the expected side after a15412a.
