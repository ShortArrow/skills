# Firing tests for slice-first

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/catalog`
— a catalog cut by technical role, where one feature lives in three
folders, both services open with the same hand-written checks, and the
two repositories are near-copies. Run them with
`tests/run-firing-tests.sh slice-first`.

Fixture: `tests/fixtures/catalog`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; without it, S1–S3 still pass when the answer names the axis
the change is fighting, declines the extraction until the two move for
the same reason, or puts the check where a new handler cannot skip it.

## Should fire

### S1 — one feature, three folders

> 商品に在庫数（stock）を持たせて、入庫で増やせるようにして。

Expected: the skill fires, or the answer says the feature spans
controller, service and repository because the cut runs across it, and
puts the new code together rather than one piece per folder.

### S2 — the lookalike extraction

> product_service と order_service の先頭の検証がまったく同じだから、
> BaseService に共通化して両方継承させて。

Expected: the skill fires, or the answer separates the actor check
(cross-cutting: belongs in the pipeline every request passes) from the
per-feature required-field checks (coincidental: two features that
agree today), and declines the base class.

### S3 — the check that has to hold everywhere

> actor が無いリクエストを弾く処理、新しいサービスを書くたびに
> 書き忘れるので、全部のサービスで必ず通るようにして。

Expected: the skill fires, or the answer puts the check in one place
the requests already pass through, so a new handler cannot omit it,
rather than adding the same line to each service.

## Should not fire

### S4 — type hints

> repositories の各メソッドに型ヒントを付けて。

Expected: no skill call. Nothing about the cut changes.

### S5 — read-only

> このコードベースの構成を一段落で説明して。

Expected: no skill call, and no restructuring offered unasked.
