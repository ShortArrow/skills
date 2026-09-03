# Firing tests for plain-japanese

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/announce`
— a release note whose sentences join two claims with が and ので,
whose 目的は…ためです never closes, whose の stacks three deep, and
which spells ユーザー two ways and links に こちら. Run them with
`tests/run-firing-tests.sh plain-japanese`.

Fixture: `tests/fixtures/announce`

A scenario passes only on the expected side: over-firing on S4/S5 is a
failure just as under-firing on S1–S3 is. The Skill call is the strong
signal; without it, S1–S3 still pass when the sentences are split at
the claim boundary, the subject is made to meet its predicate, the
doubled honorific is reduced, the spelling is fixed one way, and the
link text names its destination.

## Should fire

### S1 — a draft to tidy

> announce.md を読みやすく直して。

Expected: the skill fires, or the revision splits the multi-claim
sentences, fixes 目的は…ためです, reduces お伺いさせていただきます and
ご覧になられて, settles ユーザー / ユーザ one way, and replaces こちら
with text that names the destination.

### S2 — the conclusion is buried

> announce.md、大事なことが最後にあって読まれない気がする。構成を直して。

Expected: the skill fires, or the answer moves what the reader must do
to the top, makes the headings name their content, and keeps one topic
per paragraph.

### S3 — UI strings

> ui.md の文言、意味が取りにくいものを直して。

Expected: the skill fires, or the fixes name the actual defects: 「失敗
しましたが」の逆接の誤用, 「の」の三連, こちら as link text, and the
サーバ / サーバー split.

## Should not fire

### S4 — a code change

> announce.md に書かれている同期間隔の既定値を、設定ファイルの記述と
> 突き合わせて確認して。

Expected: no skill call. Nothing about the prose is being changed.

### S5 — translation direction

> announce.md を英訳して announce.en.md に保存して。

Expected: no skill call. The Japanese is not being revised.
