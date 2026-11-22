---
name: guard-private-names
description: Install a git pre-push hook into one clone that refuses a push whose commits carry the name of a repository the signed-in gh account keeps private, or of a ghq clone GitHub does not confirm as public, or a private host from ~/.ssh/config, or an IPv4 address that names a machine. Use when about to make a repository public, create one as public, or push for the first time to a public remote from a clone without the hook; or when asked to guard a clone against leaking private repository names, hosts or addresses. The hook is copied into the clone's own hooks directory, which git never pushes. It checks names and addresses only, not credentials or other secrets.
---

# Guard private names

A public repository that names a private one leaks that the private one exists,
and what it is called often says what it is for.
A host name from an ssh config or an address on a private network leaks the same way,
and says where the work is done.
This skill installs a pre-push hook that refuses such a push before it leaves the machine.

## Install

```
python <this skill's directory>/scripts/install.py <clone>
```

It copies `pre-push`, `repo-names.py` and `words.txt` into `<git-common-dir>/hooks` of the clone.
That directory is never pushed,
so the clone's history and its remote gain nothing,
and a clone made on another machine needs its own install.
Run it again after this skill is updated: it replaces a copy it wrote,
and an old copy keeps the old rules.

The hook needs Python on `PATH` and `gh` signed in.
When `gh` cannot list the names, every push from that clone is refused,
and so is a push git cannot read,
because a check that passes when it could not look is not a check.
`ghq` is read when it is installed.

## When it stops instead

It changes nothing and exits 1 in three cases,
because the copy would never run or a hook it did not write would be lost:

| Found | Why it stops |
|---|---|
| `core.hooksPath` in the clone's own config (husky and similar set it) | git never reads the clone's hooks directory |
| `core.hooksPath` in the global config, and no `pre-push` there containing `hooks/pre-push` | that `pre-push` does not call the clone's own, so the copy would never run |
| a `pre-push` in the clone's hooks directory that this script did not write | replacing it would drop whatever it does |

A global `core.hooksPath` whose `pre-push` does call the clone's `hooks/pre-push` is accepted,
and the script says the hook runs from there.
The match is on that text, so a call written differently stops it,
and a mention only in a comment passes it.

When it stops, report what it found and leave the clone as it is.
The person who owns the clone joins the hook by hand:
in the `pre-push` that does run,
add a line that calls `python <path>/repo-names.py "$@"` with the same standard input,
where `<path>` holds `repo-names.py` and `words.txt` copied from `scripts/`.

## What a refusal means

A refusal lists each place and an 8-character id, never the value,
because the message lands in terminals, agent transcripts and CI logs.
Remove the value from the commits and push again; in a document,
an address becomes one from the documentation ranges and a host becomes `host.example.invalid`.

Two things stay with the person at the keyboard:

- **Seeing the value.** `python <hooks>/repo-names.py --explain ID` prints a repository name or an ssh host.
  An address has no list to look it up in,
  so it is read at the place the refusal names.
  An agent does not run `--explain` or read the place out:
  the value would land in the transcript the id exists to keep it out of.
  Nor does it offer the command in a form the host runs inside the session,
  such as Claude Code's `!` prefix,
  since that output enters the transcript too.
- **Allowing a value.** A name,
  host or address that is not a leak goes on its own line in the clone's `info/repo-names-allowed`,
  which is never pushed.
  An agent does not edit that file;
  widening what passes is the owner's call.

Never push past it with `--no-verify`.

## How a name is matched

Each repository name is split into words at case changes,
separators and digits,
and each word is looked up in `scripts/words.txt`, an English word list:

- A name with a word outside the list is matched however its words are joined and cased:
  `MyQzxTool` is found as `my-qzx-tool` and `MYQZXTOOL`.
- A name of two or more listed words is matched only exactly as written,
  since its words joined otherwise are ordinary prose.
- A name that is one listed word is not checked.

The private `Host` and `HostName` values of `~/.ssh/config` join the names under the same rule:
an alias with no dot, a name ending in `.local`, `.lan`, `.internal`,
`.home` or `.ts.net`, and an address.
A public name such as `github.com` is not taken:
it would stop every push that mentions it,
and an allow file that has to be filled for the obvious invites switching the check off.
A line with `*` or `?` is skipped, since a pattern names no host.

Every IPv4 address is refused except those that name no machine:
`127.0.0.0/8`, `0.0.0.0`,
a netmask from `255.0.0.0` to `255.255.255.255`,
and the documentation ranges of RFC 5737, `192.0.2.0/24`,
`198.51.100.0/24` and `203.0.113.0/24`.
A dotted run inside a longer one,
such as the build number `10.0.26300.1`, is not an address.
Nor are four numbers joined to a letter or a `~` in front,
such as the version in `OpenSSH.Server~~~~0.0.1.0`.

Matches are whole words,
in the tree of every pushed tip and in the lines every other pushed commit adds,
so a name added and later removed is still refused.
The message of every pushed commit and annotated tag is read too,
merge messages included,
since they carry the branch and repository merged.
Where the remote's tip was never fetched, as before a force push,
every pushed commit not on the remote's branches is read.

## Sources

- Git 2.50.1, githooks(5),
  sections `pre-push` (the arguments and the lines on standard input) and the description of `core.hooksPath` in git-config(1):
  a set `core.hooksPath` replaces the hooks directory.
- RFC 5737, "IPv4 Address Blocks Reserved for Documentation":
  the three ranges a document uses in place of a real address.
- ssh_config(5), the `Host` and `HostName` keywords and the `*` and `?` of a pattern.
- wordfreq 3.1.1 (Robyn Speer), the source of `scripts/words.txt`;
  the list and its license, CC BY-SA 4.0,
  are described in the file's header.
