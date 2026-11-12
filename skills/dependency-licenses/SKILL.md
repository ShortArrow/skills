---
name: dependency-licenses
description: |
  What a dependency's license permits and what using it owes, triggered by the moments a license is taken on trust: about to add, upgrade or vendor a package, or copy code from elsewhere, without reading the license files it carries; about to take a license from a badge, a sidebar or a registry page; about to read `MIT OR Apache-2.0` as both, a `WITH` exception as the bare license, or `GPL-2.0-only` as or-later; about to combine Apache-2.0 code with GPL-2.0-only code, or GPLv2-only code with GPLv3; about to treat code with no license as free to use; about to write a license field or file header that is not an SPDX expression; about to ship a binary, bundle or container without the notices and source its dependencies require; about to guess at a license question no tool settled. Whether third-party code is safe to install is adopt-dependency's; this skill is whether it may be used and what that use owes. Use when a license check fails and before a release or an SBOM.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch
---

# Dependency licenses

A license is a grant with conditions.
What governs a dependency is the text inside the artifact you ship,
at the version you ship,
and the conditions attach to what you do with it: copy it, change it,
combine it, distribute it.
So the question is never "what license is this project";
it is **what does this artifact say, and what does our use of it owe**.

## The moments this replaces

| About to… | Instead |
|---|---|
| add, upgrade or vendor a dependency without opening its license files | read the files in the artifact at that version; a relicense between versions is an upgrade's change too |
| take the license from a badge, a sidebar or a registry page | treat those as the declared license and check them against the files; record the concluded one |
| read `MIT OR Apache-2.0` as both, or `GPL-2.0-or-later WITH Classpath-exception-2.0` as plain GPL | parse the expression (below) and record which branch of an `OR` the project elects |
| link Apache-2.0 code into a GPL-2.0-only program, or combine GPLv2-only with GPLv3 code | stop: the FSF reads both as incompatible; look for an or-later grant or another dependency |
| copy code from a repository that has no license | treat it as no permission; ask the author or leave it |
| write `"license": "MIT/Apache"` or a header in prose | write an SPDX expression; a custom license is a `LicenseRef-` with its text beside it |
| ship a binary, bundle or image with no third-party notices | generate the notices and the SBOM from what is shipped, not from the manifest |
| allow a license globally to clear one package | add a per-package exception, as `adopt-dependency` does for its guards |
| decide a compatibility or custom-license question by guess | write down the evidence and hand the call to whoever owns licensing for the project |

## Declared is not concluded

SPDX names the two things that are usually confused.
The **declared** license is "simply the license identified in text in one or more files" of the package:
the `license` field, the badge, the header.
The **concluded** license is what someone arrived at after analysing the package,
"together with the results from any scanning tools",
as the license that actually governs it.
They differ more often than a badge suggests:
a package declares MIT and vendors a GPL file;
a manifest says Apache-2.0 and the LICENSE file is a modified BSD;
a registry shows nothing and the files are clear.

Two values look alike and are not.
`NONE` means there is no license;
`NOASSERTION` means nobody determined it,
and a missing field implies `NOASSERTION`.
An SBOM full of `NOASSERTION` records that the work was not done,
not that the dependencies are unencumbered.

Where a conclusion overrides the declaration,
keep the reason with it and tie it to the files it rests on. cargo-deny's `clarify` entry is the pattern:
it assigns an expression to a crate and holds only while the listed license files still match their hashes,
so the override expires when the evidence changes.

## Read the expression

An SPDX license expression is a small language,
and its operators carry obligations:

| Expression | Means |
|---|---|
| `MIT OR Apache-2.0` | either, at the recipient's choice; record which one the project takes |
| `MIT AND BSD-2-Clause` | both, at once; every notice is owed |
| `GPL-2.0-or-later WITH Classpath-exception-2.0` | the license as modified by the exception; the exception is the part that permits the use, so it is never dropped |
| `GPL-2.0-only` / `GPL-2.0-or-later` | the version is closed or open; the difference decides whether GPLv3 code can join it |
| `LicenseRef-Acme-EULA` | a license the list does not carry; its text has to be in the package |

Precedence runs `+`, `WITH`, `AND`, `OR` from tightest to loosest,
so `A OR B AND C` is `A OR (B AND C)`; write the parentheses anyway.
Operators are case-sensitive, identifiers are not.
`GPL-2.0` without `-only` or `-or-later` is a deprecated identifier:
it stays valid but says nothing about later versions,
so look at the file to learn which was meant.

Where each ecosystem keeps the declaration:

| Ecosystem | Field | Note |
|---|---|---|
| npm | `license` in `package.json` | an SPDX expression; `SEE LICENSE IN <file>` for a custom one; `UNLICENSED` means no grant at all |
| Cargo | `license`, or `license-file` for a nonstandard license | crates.io reads an SPDX 2.3 expression; the old `/` separator is deprecated for `OR` |
| Python | `license` and `license-files` in `[project]` (PEP 639) | the core metadata field `License-Expression` holds an SPDX expression; the `License ::` classifiers are deprecated |
| NuGet | `PackageLicenseExpression` or `PackageLicenseFile` | `PackageLicenseUrl` is deprecated; a package that only links a URL points at text that can change after it was published |
| Go | none | pkg.go.dev detects licenses from LICENSE-like files with `licensecheck`; a modified text may go undetected |

## No license is no permission

A repository with no license grants nothing.
As choosealicense.com puts it,
the absence "generally means you have no permission from the creators of the software to use, modify, or share the software." GitHub's terms let others view and fork a public repository,
which is not permission to use it.
A snippet from an answer site,
a gist or a blog carries the license of where it was published, or none;
find which before it enters the code.

## Compatibility is about the combined work

Two licenses are compatible when the combination can be distributed meeting both at once.
The question arises when code is combined into one program and distributed;
the FSF reads static linking and modules sharing an address space as one program,
and processes talking over pipes,
sockets or command lines as separate programs,
while noting that the line is ultimately a legal question.
A permissive component can usually join a copyleft whole,
and the whole is then distributed under the copyleft license;
the reverse is where combinations fail.

The cases that come up most,
from the FSF's license list and GPL FAQ and the Apache Software Foundation's own page:

| Combining | Result |
|---|---|
| Apache-2.0 code into a GPL-3.0 program | allowed; the combination is distributed under GPL-3.0 |
| GPL-3.0 code into an Apache-2.0 program | not allowed; the Apache project would have to become GPL-3.0 |
| Apache-2.0 code with GPL-2.0-only code | incompatible: Apache-2.0's patent termination and indemnification terms are restrictions GPLv2 does not permit |
| Apache-2.0 code with GPL-2.0-or-later code | allowed by taking the GPL-2.0-or-later code under GPL-3.0 |
| GPL-2.0-only code with GPL-3.0 code | incompatible; combining them would violate section 6 of GPLv2 |
| GPL-2.0-or-later code with GPL-3.0 code | allowed; GPL-3.0 is one of the versions the grant permits |

Every row above that says GPLv3 holds for AGPLv3 too,
per the FSF's compatibility matrix.
This is why `-only` and `-or-later` are not a detail:
the same GPLv2 code is compatible or not with an Apache-2.0 dependency depending on that suffix.

## Each license has a known weak spot

Some trouble comes from the license alone, before any combination:

| License | Weak spot | What to do |
|---|---|---|
| MIT, ISC, BSD | the text says nothing about patents, so a contributor grants no patent license expressly; the FSF recommends Apache-2.0 for substantial programs "since it blocks patent treachery" | for the project's own substantial code prefer Apache-2.0, whose section 3 grants a patent license and ends it for whoever sues over the work; for a dependency, record that no patent grant came with it |
| GPL-2.0-only | cannot be combined with Apache-2.0 or GPL-3.0 code (above) | check the suffix before planning the combination; ask the author about or-later if it is the only blocker |
| NYSL | has no SPDX identifier (License List 3.29.0) | write `LicenseRef-NYSL` with its text in `LICENSES/LicenseRef-NYSL.txt`; every tool will call it unknown, so the allow list names it explicitly |
| CC0-1.0 | a waiver that "overtly, fully, permanently, irrevocably and unconditionally" surrenders all copyright and related rights worldwide, with a fallback license where a waiver fails; section 4(a) says patent rights are not waived or licensed; the FSF does not recommend it for software for that reason | do not put it on the project's own code as a shorthand for "anyone may use this": it cannot be taken back and keeps patents in hand; for a dependency, record that patents were expressly withheld |
| AGPL-3.0 | a modified version used over a network must offer its source to those users; Google's published policy is that AGPL code "MUST NOT be used at Google" | deny by default in anything run as a service; allow only where offering the source is part of the plan |
| a modified license (a listed text with a clause added or changed) | it is not the listed license: SPDX's matching guidelines say text with "additional text or clauses" is not a match; its terms, the warranty disclaimer included, are whatever the new text says | give it a `LicenseRef-`, read the whole text, and hand the decision to a person; a scanner's near-match is the mistake to avoid |

## The obligation follows the use

Read which act triggers each condition before deciding what is owed.
For most permissive licenses the act is redistribution,
and the condition is that the copyright notice and the license text travel with the copy.
That is easy to lose in exactly the step that ships:
a bundler that strips comments strips the notice,
a multi-stage container build that copies only the binary leaves the license files behind,
a single-file publish folds a hundred packages into one executable.
For copyleft licenses the act may also oblige the corresponding source,
and AGPL-3.0's section 13 extends it:
a modified version must offer its source to the users who interact with it over a network.
A dependency used only to build or test, and never shipped,
owes far less than one that is in the artifact;
classify each by whether it ships.

## Hold the policy in a check

Write the policy as an allow list that denies everything it does not name,
with exceptions scoped to one package and version,
and run it in CI on every change to the lockfile.
A license appearing for the first time then fails the build,
which is the moment someone should decide about it.
For Rust, cargo-deny does this (`[licenses] allow`, `exceptions`, `clarify`);
the other ecosystems need a tool that reads their field,
or a scanner such as ScanCode over the files.
A scanner reports a match with a confidence;
a low one is a question for a person, not a pass.

## An SBOM records the conclusion

Generate the SBOM from the artifact you ship,
so it lists what is actually in it:
`syft <image> -o spdx-json=sbom.spdx.json` reads an image or directory,
and Microsoft's `sbom-tool generate` writes SPDX 2.2 by default and SPDX 3.0 with `-mi SPDX:3.0`.
The licenses in it are only as good as the conclusions behind them;
count the `NOASSERTION` entries before calling it done.

## The project's own license

Give every file its license by machine-readable header,
the way the REUSE specification 3.3 lays it out:

```
// SPDX-FileCopyrightText: 2026 Example Contributors
// SPDX-License-Identifier: MIT OR Apache-2.0
```

The license texts go in `LICENSES/<identifier>.txt` at the root.
A file that cannot hold a comment, an image or a JSON file,
takes an adjacent `<file>.license`,
and a large directory can be covered from `REUSE.toml` instead.
Vendored third-party files keep their own header,
so the repository says file by file which code is whose.

The REUSE tool (6.2.0) does the work and the check:

```bash
reuse annotate --copyright="Example Contributors" --license="MIT OR Apache-2.0" -r src
reuse download --all     # the texts of every license used but missing from LICENSES/
reuse --no-multiprocessing lint # fails on any file whose copyright or license is not stated
reuse spdx -o reuse.spdx # an SPDX document of the repository's own files
```

Run the lint in CI so a file added without a header fails the build:
`fsfe/reuse-action@v6` in a GitHub workflow (`with: args: --no-multiprocessing lint`),
the `fsfe/reuse` image elsewhere,
or the `reuse` pre-commit hook to catch it before the commit.
Pass `--no-multiprocessing`,
a global option that goes before the subcommand, in CI:
in this catalogue's owner's experience `reuse lint` often fails in CI for no reason anyone could find without it,
and the documentation describes the option only as disabling a "performance enhancer".
`reuse spdx` writes `NOASSERTION` as each file's concluded license unless `--add-license-concluded` is given,
which is the declared-versus-concluded distinction above,
kept honest by default.

## What a tool cannot decide

Some questions have no answer in a table: a custom license,
a license with an added clause,
an incompatibility a design change might avoid,
a dependency relicensed between the version in use and the next.
Write down what the files say, at which version,
and which use is planned,
and hand the decision to whoever owns licensing for the project.
Reporting a guess as a conclusion is the failure this skill exists to prevent.

## Checklist

- [ ] Every new or upgraded dependency's license was read from its files at that version
- [ ] Each declaration that disagreed with the files has a recorded conclusion tied to them
- [ ] Every `OR` has its elected branch recorded,
  every `WITH` kept with its license
- [ ] No GPL-2.0-only code is combined with Apache-2.0 or GPL-3.0 code
- [ ] Nothing was copied from a source with no license
- [ ] The policy is an allow list run in CI,
  with per-package exceptions only
- [ ] The project's own files pass `reuse lint`, in CI
- [ ] The shipped artifact carries its notices,
  and the source where a license asks for it
- [ ] The SBOM is generated from the artifact,
  and its `NOASSERTION` entries are counted
- [ ] Undecided questions went to a person with the evidence,
  not into the code with a guess

## How this connects

`adopt-dependency` asks whether third-party code is what it claims to be and safe to install;
this skill asks whether it may be used and what that use owes.
Both run when a dependency is added,
and neither answers the other's question.
`measured-claims` applies to every date below:
a license list and a compatibility page are read on a day.

## Sources

All read on 2026-10-15.

- SPDX Specification 3.0.1,
  Annex B "SPDX license expressions" (Normative): operators, precedence,
  `LicenseRef-`, case rules.
- SPDX Specification 2.3.1,
  clause 7.13 "Concluded license" and 7.15 "Declared license":
  the definitions quoted above and the meanings of `NONE` and `NOASSERTION`.
- SPDX License List 3.29.0 of 2026-09-16, spdx.org/licenses:
  deprecated identifiers such as `GPL-2.0` remain valid but should no longer be used.
- REUSE Specification 3.3 of 2024-11-14, reuse.software/spec-3.3:
  `LICENSES/`, `SPDX-FileCopyrightText`,
  `.license` files and `REUSE.toml`.
- SPDX Specification 3.0.1,
  Annex "License matching guidelines and templates":
  added text or clauses is not a match.
- REUSE tool 6.2.0 documentation,
  reuse.readthedocs.io (`annotate`, `download`, `lint`, `spdx`, and the global `--no-multiprocessing`),
  and reuse.software/dev: `fsfe/reuse-action@v6`,
  the `fsfe/reuse` image and the pre-commit hook.
- npm Docs, "package.json", `license`; the Cargo Book,
  "The Manifest Format", `license` and `license-file`;
  PEP 639 (Final) and the PyPA core metadata it now lives in;
  Microsoft Learn, "NuGet pack and restore as MSBuild targets",
  license properties; pkg.go.dev "License Policy".
- Free Software Foundation,
  "Various Licenses and Comments about Them" (gnu.org/licenses/license-list.html, page dated 2026-04-22):
  Apache-2.0 is compatible with GPLv3 and not with GPLv2;
  GPLv2 by itself is not compatible with GPLv3;
  the Expat ("MIT") entry's advice to prefer Apache-2.0 for substantial programs;
  the CC0 entry's advice against CC0 for software for want of a patent grant.
- Free Software Foundation,
  "Frequently Asked Questions about the GNU Licenses" (gnu.org/licenses/gpl-faq.html, page dated 2026-01-13):
  "Is GPLv3 compatible with GPLv2?",
  the compatibility matrix and its note that GPLv3 entries hold for AGPLv3,
  and "What is the difference between an aggregate and other kinds of modified versions?"
- Apache Software Foundation,
  "Apache License v2.0 and GPL Compatibility" (apache.org/licenses/GPL-compatibility.html):
  Apache-2.0 software can be included in GPLv3 projects, not the reverse.
- Apache License, Version 2.0, section 3 "Grant of Patent License".
- Creative Commons, CC0 1.0 Universal legal code, sections 2 "Waiver",
  3 "Public License Fallback" and 4(a).
- Google Open Source, "AGPL Policy" (opensource.google/documentation/reference/using/agpl-policy).
- GNU Affero General Public License version 3,
  section 13 "Remote Network Interaction".
- choosealicense.com, "No License".
- cargo-deny, "licenses" configuration: `allow`, `exceptions`,
  `confidence-threshold`, `clarify`.
- anchore/syft README and microsoft/sbom-tool README:
  output formats and SPDX versions.

The advice to pass `--no-multiprocessing` in CI is this catalogue owner's practice,
not documented behaviour.
The compatibility rows are the license stewards' published readings,
not legal advice;
a question they do not settle goes to the project's counsel.
