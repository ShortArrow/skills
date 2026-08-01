---
name: find-skills
description: Search the published skill registry before writing a skill or working through a specialised task by hand. `npx skills find <query>` returns matches across every public collection ranked by installs, and `npx skills use` prints one without installing it. Use when a task looks like something someone will already have solved — a file format, a framework's conventions, a vendor's tooling — and before starting to author a new skill.
allowed-tools: Bash, Read, WebFetch
---

# Find Skills

Installed skills are already in context; their descriptions are loaded
into every session. This is for the ones that are **not** installed.

## Search

```
npx skills find pdf
npx skills find playwright --owner microsoft
```

Results are ranked by install count and carry a skills.sh link:

```
anthropics/skills@pdf 169.7K installs
└ https://skills.sh/anthropics/skills/pdf
```

It runs without a TTY and exits 0, so the output can be read directly.

## Read before installing

**A skill runs with the agent's full permissions.** Install count is
popularity, not review. Read `SKILL.md` first — and anything under
`scripts/`, which is where a skill can execute rather than instruct.

```
npx skills use anthropics/skills@pdf
```

`use` resolves the source the same way `add` does, writes to a temporary
directory and prints only the generated prompt. Nothing is installed.

## Install

```
npx skills add anthropics/skills --skill pdf
```

`--skill` takes one entry rather than the collection, and the name it
matches is the one the skill declares, not its directory.

For a collection carrying `.claude-plugin/marketplace.json`, Claude Code
can take it directly instead:

```
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
```

## When to look

- **Before authoring a skill.** The problem is rarely new. Adopting an
  existing one and narrowing it beats starting from nothing.
- **Before a specialised task by hand.** File formats, a framework's
  conventions, a vendor's toolchain — all well covered.
- **Not for something already installed.** Those descriptions are in
  context; searching for them wastes a call.

## What installing costs

Every installed skill's description is loaded into **every session**,
whether or not it fires. `claude plugin details <name>` reports the
split between that and the body, which is read only on use.

So install the skill, not the catalogue. A collection added whole for one
useful entry charges for all of it, permanently.
