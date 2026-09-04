---
name: i18n-parity
description: |
  Keep a multilingual site's pages in step, where the build cannot help. A page added in one language only, or edited in one language while its counterpart keeps the old text, renders perfectly and is wrong — the second is the quiet one. Covers judging staleness from commits rather than mtime, the exception that expires on its own so a legitimate one-sided edit is not a permanent hole, and the five ways this check silently passes when it is not working. Use when adding a language, when a translated page changed on one side only, or when writing the check itself.
allowed-tools: Bash, Read, Write, Edit
---

# Translation parity

Two failures never reach the build:

- a page exists in one language and not the others
- a page is edited in one language and its counterpart keeps the old text

The second is the dangerous one. The site still renders, the navigation is
intact, and the reader gets last month's answer in their language.

## Judge staleness from commits, not mtime

A checkout does not preserve modification times. Clone the repository on a
CI runner and every file is equally new, so an mtime comparison passes
there whatever the state. Compare `git log -1 --format=%ct` for each side
instead.

## One-sided edits are legitimate

Not every edit has a counterpart. A Japanese spacing fix, an English
article, a repair to prose that reads as translated in one language only —
none of these has anything to mirror. A check that forbids them will be
switched off within a month.

So the exception is **declared**, and declared as a **commit**, not as a
path:

```
content/ja/notes/usb-suspend.md a05d7ee99182d26ebd9ebdc243e445ff91a801ca
```

That line stops the pair being compared *while that commit is the newest
one touching the path*. The next commit to touch the file leaves the
exception matching nothing, and the check comes back. Pinning to a path
instead would be a permanent hole with no expiry.

Three things follow, each learned by being wrong about it:

- **Full hashes.** How far git abbreviates depends on the size of the
  repository, so an abbreviation that is unique in a checkout can be
  ambiguous on a runner. Resolve the declared revision through
  `git rev-parse --verify --quiet "$rev^{commit}"` and accept any length.
- **An exception covers everything that commit did to that file.** A
  one-sided prose repair carrying a fact that should have been mirrored is
  excused along with it. Keep such commits narrow; nothing enforces it.
- **Report which lines are still live.** An expired entry does nothing and
  is indistinguishable from a working one by reading. Print live, expired,
  and does-not-resolve on every run, and delete the expired.

Every entry needs its reason next to it. An entry with no reason is a
silenced check.

## Five ways this check passes without working

Each of these was a real green run.

| | |
|---|---|
| **A dirty working tree** | Staleness is read from commits, so a one-sided edit sitting unstaged is invisible: both sides still report the commit that touched them last, usually the same one. The honest answer on a dirty tree is *cannot tell yet* — refuse, do not pass |
| **A file git has never recorded** | `git log -1 --format=%ct` prints nothing and exits 0, so `|| echo 0` never fires. The empty value reaches `[` as a syntax error, the comparison is skipped, and the run is green |
| **Abbreviated revisions** | Matched locally, missed in CI, for the reason above |
| **A history rewrite** | Every declared revision stops resolving at once. Fail loudly on an unresolvable revision — silently ignoring it turns the whole file off |
| **No exec bit** | A `.sh` authored on Windows carries no executable bit, and CI exits 126. Invoke it as `bash scripts/check-...sh` rather than relying on the mode |

## Name the language the way the tag does

The check keys on a language identifier, usually a directory name, so
the two sides have to be spelled the same way or one of them is
invisible. The public spelling is BCP 47 (RFC 5646): subtags in the
order language, extended language, script, region, variant, extension,
private use — `ja`, `en-GB`, `zh-Hant-TW`. Tags are case-insensitive
and the casing "MUST NOT be taken to carry meaning", but the
convention is lowercase language, titlecase script, uppercase region,
and a check that compares strings inherits whatever casing the site
used. Normalise to the tag before comparing, and when the site's
directories are `ja` and `JA-JP`, that is the first finding.

## Scope it per section

Opt sections in rather than checking everything. A documentation section
mounted from beside the code it documents may be English under every
language by design, and forcing parity on it produces noise that trains
everyone to ignore the check.

## Where the script belongs

In the repository it checks, called from CI. It is short — a hundred lines
of shell — and it has to run for a person and for a runner, neither of
which has this skill installed.

## Sources

- RFC 5646, "Tags for Identifying Languages", BCP 47, IETF — subtag
  order (section 2.1) and case treatment; wording checked on
  2026-09-04. Obsoletes RFC 4646.
