---
name: find-skills
description: Find an existing skill before writing one or working through a specialised task by hand. Search the vendor-official collections by owner first — the open registry is open publication, and a skill is code that runs with the agent's full permissions, so install count is popularity rather than review. Use when a task looks like something a vendor will already have solved: a file format, a framework's conventions, a toolchain.
allowed-tools: Bash, Read, WebFetch
---

# Find Skills

Installed skills are already in context; their descriptions load into
every session. This is for the ones that are **not** installed.

## Search a known owner first

`--owner` scopes the search to one GitHub owner. Only one takes effect
per call, so query the owners the task suggests.

```
npx skills find pdf --owner anthropics
npx skills find playwright --owner microsoft
```

Collections published by the vendor whose product is involved:

| Owner | Covers |
|---|---|
| `anthropics` | Document formats, artifact building, skill creation |
| `openai` | Codex |
| `google` | Google products |
| `microsoft` | Microsoft SDKs |
| `MicrosoftDocs` | Microsoft documentation |
| `NVIDIA` | Physical AI, robotics, simulation, CUDA, RAG |
| `amd` | AMD's software stack |
| `cloudflare` | Cloudflare |
| `android` | Android |
| `vercel-labs` | React, Next.js, deployment |
| `remotion-dev` | Remotion |
| `github` | awesome-copilot, a community collection |

This buys accountability, not correctness. A named vendor can be held to
a security process; it does not make the skill right for the job.

## Why not search everything

An unscoped `npx skills find` returns the whole registry, which is open
publication — anyone may publish, and nothing is reviewed. The results
carry install counts, and **an install count measures popularity, not
scrutiny**.

**A skill is code that runs with the agent's full permissions.** Adding
one is closer to `npm install` than to reading documentation: `SKILL.md`
is instruction the agent follows, and `scripts/` is executed. A skill
from an unknown author can direct the agent to read credentials, or
simply run something.

"Read it before installing" is not sufficient mitigation on its own.
Catching a subtle instruction buried in prose is unreliable, and the
burden returns on every update. `adopt-dependency` covers what does
establish provenance, and what only looks like it.

So widen the search only when no vendor collection covers the task, and
then treat the result as untrusted third-party code:

- Read `SKILL.md` in full, and everything under `scripts/`
- Prefer an owner you can identify — a company, a project you know
- If you would not run their `npm` package without looking, do not install
  their skill without looking either

```
npx skills use <owner>/<repo>@<skill>
```

`use` resolves the source the way `add` does, writes to a temporary
directory and prints only the generated prompt. Nothing is installed, so
this reads a skill without adopting it.

## Install

```
npx skills add anthropics/skills --skill pdf
```

`--skill` takes one entry rather than the collection, and matches the name
the skill declares, not its directory.

Where a collection carries `.claude-plugin/marketplace.json`, Claude Code
can take it directly:

```
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
```

In Codex, use the built-in skill installer for a known curated skill or
ask it to install a skill from the repository. For an agent-neutral local
install, `npx skills add` writes to `.agents/skills/`, which Codex scans.

## When to look

- **Before authoring a skill.** The problem is rarely new.
- **Before a specialised task by hand.** File formats, a framework's
  conventions, a vendor's toolchain.
- **Not for something already installed.** Those descriptions are in
  context; searching for them wastes a call.

## What installing costs

Every installed skill competes for the host's initial discovery context,
whether or not it fires. In Claude Code, `claude plugin details <name>`
reports the always-on description against the body, which is read only on
use. Codex also starts from names and descriptions and may shorten or omit
entries when the installed set exceeds its discovery budget.

Install the skill, not the catalogue. A collection taken whole for one
useful entry is charged for in full, permanently.
