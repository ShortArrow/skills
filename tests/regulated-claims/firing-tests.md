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

> landing.md の「三層構造」の説明を、notes.md の記述に合わせて
> 正確にして。

Expected: no skill call. Describing the construction makes no governed
claim.

### S5 — formatting

> landing.md の見出しレベルを整えて、価格表を表組みにして。

Expected: no skill call. No claim changes.
