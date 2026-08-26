# Firing tests for state-first

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/registry`
— a user registry with a branch per case and a document with three
booleans — so the session holds code whose states were never listed.
Run them with `tests/run-firing-tests.sh state-first`.

Fixture: `tests/fixtures/registry`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; the states listed before the change, or a flag set replaced by
one enumeration, still passes S1–S3 without the call. What fails is one
more branch, one more flag, or one more parameter added where it was
asked for.

## Should fire

### S1 — an exception clause about to become a branch

> user.py の register に、退会済み（active が False）のユーザーが同じ
> メールで登録し直したら復活させる処理を足して。ただし banned の人は除く。

Expected: the skill fires, or the start states (absent, active,
inactive, banned) and the single success state are written before the
edit and the function is reshaped around them rather than gaining a
branch.

### S2 — a fourth flag

> doc.py の Document に is_archived フラグを足して、アーカイブ済みは
> 変換できないようにして。

Expected: the skill fires, or the three booleans and the new one are
replaced by one enumeration of the states a document can be in.

### S3 — a property and a state in one signature

> doc.py の can_convert に、ロック中も変換不可になるよう is_locked
> 引数を足して。

Expected: the skill fires, or the property check (format) is separated
from the state check (uploaded, locked) instead of the signature
growing a third parameter.

## Should not fire

### S4 — annotations

> user.py と doc.py の関数に型ヒントを付けて。

Expected: no skill call. No state model is touched.

### S5 — read-only

> doc.py を読んで、何をするモジュールか一段落で説明して。

Expected: no skill call, no redesign offered unasked.
