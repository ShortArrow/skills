---
name: guard-private-names
description: Install a git pre-push hook into one clone that refuses a push whose commits carry the name of a repository the signed-in gh account keeps private, or of a ghq clone GitHub does not confirm as public. Use when about to make a repository public, create one as public, or push for the first time to a public remote from a clone without the hook; or when asked to guard a clone against leaking private repository names. The hook is copied into the clone's own hooks directory, which git never pushes. It checks names only, not credentials or other secrets.
---

# Guard private names

A public repository that names a private one leaks that the private one exists,
and what it is called often says what it is for.
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

A refusal lists each place and an 8-character id, never the name,
because the message lands in terminals, agent transcripts and CI logs.
Remove the name from the commits and push again.

Two things stay with the person at the keyboard:

- **Seeing the name.** `python <hooks>/repo-names.py --explain ID` prints it.
  An agent does not run it:
  the name would land in the transcript the id exists to keep it out of.
- **Allowing a name.** A name that is an ordinary word and not a leak goes on its own line in the clone's `info/repo-names-allowed`,
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

Matches are whole words,
in the tree of every pushed tip and in the lines every other pushed commit adds,
so a name added and later removed is still refused.

## Sources

- Git 2.50.1, githooks(5),
  sections `pre-push` (the arguments and the lines on standard input) and the description of `core.hooksPath` in git-config(1):
  a set `core.hooksPath` replaces the hooks directory.
- wordfreq 3.1.1 (Robyn Speer), the source of `scripts/words.txt`;
  the list and its license, CC BY-SA 4.0,
  are described in the file's header.
