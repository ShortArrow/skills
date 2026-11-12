# Dependencies

The plugins this catalogue installs from someone else's repository,
with the review `adopt-dependency` and `dependency-licenses` ask for,
against the commit each entry in `.claude-plugin/marketplace.json` pins.
A bump of the pin is a fresh review, written over the entry.

## security-audit

- **Source.** `cloudflare/security-audit-skill`, ref `main`,
  pinned at `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`.
  Taken unchanged, so no submodule;
  `tests/test_upstream_pins.py` holds the pin against the remote.
- **Identity.** The repository is owned by the GitHub organisation cloudflare,
  and its merge commits are signed by GitHub's web-flow key `B5690EEEBB952194`,
  verified by the API.
  The non-merge commits are unsigned,
  so what is established is that the merges happened on GitHub under that organisation,
  not who wrote the lines.
- **License.** MIT, Copyright (c) 2025-2026 Cloudflare, Inc.
  One LICENSE file, no other license text and no SPDX headers in the skill,
  so the declared and the concluded license agree.
  Nothing is combined into this catalogue's own code;
  it is installed as its own plugin, which the notice travels with.
- **Executable content.** `validate-findings.cjs` and `validate-coverage-ledger.cjs` require only `fs`,
  `path` and `util`, take one path argument and exit with a code.
  No network, no `child_process`, no environment read.
  Every `spawnSync` and every write is in the two `.test.cjs` files,
  against temporary directories.
- **Not done.** Upstream's own test suites were not run:
  the sandbox declines to execute freshly downloaded code,
  and that was left in place.

## yomiyasu

- **Source.** The fork `ShortArrow/yomiyasu`, ref `shortarrow`,
  pinned at `003c30eb5fa89120902f00002012e82af2f20fd7`,
  the commit the submodule `vendor/yomiyasu` records.
  The fork is upstream `nanaism/yomiyasu` v3.0.0 plus one paragraph and the folder `references/local/`;
  editing upstream's `SKILL.md` instead would conflict at every upstream release.
- **License.** MIT, Copyright (c) 2026 nanaism,
  with `UNICODE-LICENSE.txt` alongside.
- **Tests.** Three of upstream's tests fail on Windows,
  identically on the fork and on a clean upstream v3.0.0 worktree:
  two from line endings converted to CRLF on checkout,
  one in the retry test.
- **Not recorded.** No adoption review of identity or executable content was written when the plugin was added.
