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

2026-10-15, claude-opus-5-5,
`MAX_TURNS=10 tests/run-firing-tests.sh dependency-licenses`,
first attempt: invalid.
The marketplace had been updated but the installed plugin was still 8e7ec81,
so the sessions had no `dependency-licenses`,
and the new hook commands named a script that cache lacked:
Python exited 2 and Bash calls were blocked in every scenario.
That led to a4c6a80 (a hook whose script is missing lets the call through).

2026-10-15, claude-opus-5-5,
the same command after `claude plugin update` to 12b55db,
with the skill listed with its description (checked in a fresh `claude -p`):

- S1, S2, S3: no Skill call (39 s / 58 s / 35 s, $0.30 / $0.38 / $0.31).
  The behaviour matched each expectation anyway.
  S1 named GPL-2.0-only against Apache-2.0 and the FSF's reading,
  changed nothing and proposed its own parser.
  S2 wrote `MIT OR Apache-2.0`, explained `OR` against `AND`,
  added `LICENSE-MIT`,
  and named the vendored GPL file and the badge-only directory as open issues.
  S3 refused to copy, named the missing license file and the badge as no grant,
  and noted that the upstream `fastq` it resembles is ISC.
- S4, S5: no Skill call.

5/5 on the expected side by the weak signal; 0/3 by the strong one.
The model answers these cases from what it already knows,
so the description is not what decides them;
the body's weight is in the cases this fixture does not reach:
a declared license that disagrees with the files, CC0 or NYSL,
an SBOM's `NOASSERTION` count, REUSE in CI.
