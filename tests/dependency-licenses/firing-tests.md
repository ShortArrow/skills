# Firing tests for dependency-licenses

The description is the implementation; these scenarios are its tests.
Each runs in a fresh session inside a copy of `tests/fixtures/notices`:
an Apache-2.0 package with a vendored file whose header says GPL-2.0-only,
and a copied directory whose README shows an MIT badge and which carries no license file.
Run them with `tests/run-firing-tests.sh dependency-licenses`.

Fixture: `tests/fixtures/notices`

A scenario passes only on the expected side:
over-firing on S4/S5 is a failure just as under-firing on S1–S3 is.
The Skill call is the strong signal;
without it S1–S3 still pass when the reply names the license problem before the edit lands.

## Should fire

### S1 — a GPL-2.0-only file about to be wired into an Apache-2.0 package

> vendor/parse-color.js を src/index.js から使って、'#ff8000' みたいな文字列からも変換できるようにして。

Expected: the skill fires,
and the reply names that `vendor/parse-color.js` is GPL-2.0-only while the package is Apache-2.0,
that the FSF reads the two as incompatible,
and does not ship the combination silently: it writes its own parser,
or stops and asks.

### S2 — a dual license about to be written as prose

> package.json の license を MIT と Apache の両方にしておいて。

Expected: the skill fires,
and the field becomes the SPDX expression `MIT OR Apache-2.0`,
not `MIT/Apache-2.0` and not `AND`,
with the MIT text added beside the Apache one.

### S3 — code with only a badge about to be copied in

> third_party/fastq は README に MIT バッジが付いてるから、
> src に取り込んで使えるようにして。

Expected: the skill fires,
and the reply says the directory carries no license file,
that a badge is a declaration and not the license,
and that with no license there is no permission;
it asks for the source of the code or its license text before copying.

## Should not fire

### S4 — translation

> README.md を英訳して README.en.md に保存して。

Expected: no skill call.
Nothing is being licensed.

### S5 — a rename

> src/index.js の toHex を formatHex にリネームして、
> README の例も合わせて。

Expected: no skill call.
The code's licensing does not change.

## Recorded runs

None yet.
