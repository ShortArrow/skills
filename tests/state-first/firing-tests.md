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

Expected: the skill fires, and the outcome (locked documents do not
convert) lands with the property check (format) apart from the state
check (uploaded, locked) and one sentence saying so, instead of the
signature growing a third parameter. Firing and then adding the
parameter is the strong signal only.

## Should not fire

### S4 — annotations

> user.py と doc.py の関数に型ヒントを付けて。

Expected: no skill call. No state model is touched.

### S5 — read-only

> doc.py を読んで、何をするモジュールか一段落で説明して。

Expected: no skill call, no redesign offered unasked.

## Recorded runs

2026-08-26, claude-fable-5, `tests/run-firing-tests.sh state-first`
(`claude -p --max-turns 6`, fresh sessions, registry fixture):

- S1, S2, S3: fired — `Skill(engineering-skills:state-first)` invoked
  (114 s / 109 s / 60 s, $0.55 / $0.52 / $0.42 per session).
  S1 replaced `active`/`banned` with a `Status` enumeration after
  writing a failing test. S2 wrote the start-state table and a
  characterisation test, then ran out of turns before touching the
  flags; `doc.py` was unchanged. S3 added the third parameter as asked
  and recorded in the docstring which argument is a property and which
  are states; the signature was not split.
- S4, S5: no Skill call.

5/5 on the expected side. S2 and S3 pass on the strong signal only.

2026-08-27, claude-fable-5, S3 only, after the "When the request names
the shape" section and the trigger widened to the parameter added:

- First run (484acf2): no Skill call; the parameter was added, the
  property/state mix noted as "気になる点" and left. FAIL.
- Two runs on 526fb87: both fired (104 s / 82 s, $0.53 / $0.48). Both
  split `convertible(file_type)` from the state check and replaced the
  three booleans with a `DocumentState` enumeration; both hit the turn
  limit before a closing sentence.
