# skills

Personal [Agent Skills](https://agentskills.io) for Claude Code, Codex,
GitHub Copilot, Cursor and Gemini CLI.

Each skill answers a question that comes up repeatedly and is easy to get
wrong the first time — which capture method fits this target, what a
document may not assume its reader knows, what a transcription is not
allowed to invent.

## Install in Claude Code

```
/plugin marketplace add ShortArrow/skills
```

Then install whichever set applies.

| Plugin | Skills |
|---|---|
| `screenshot-skills` | any-screenshot, windows-screenshot, avalonia-screenshot, flaui-screenshot, hyperv-screenshot |
| `writing-skills` | clean-docs, unmachine-prose, plain-japanese, document-structure, regulated-claims, pdf-transcribe, i18n-parity, measured-claims, request-approval |
| `product-skills` | new-combination |
| `engineering-skills` | plan-delegate-verify, adversarial-verify, tdd-cycle, test-design, tidy-first, diagnose-first, design-by-contract, slice-first, github-paths, csharp-architect, tui-debug, windows-sandbox, hyperv-clean-vm, peer-sessions, grill-me, tool-call-syntax, codex, find-skills, adopt-dependency, library-design, state-first, assurance-case, agent-harness |

## Install in Codex

Ask Codex's built-in skill installer to install the repository, or use the
agent-neutral installer:

```
npx skills add ShortArrow/skills
```

The latter installs under `.agents/skills/`, one of the repository and
user locations Codex scans. Select individual skills instead of the whole
catalogue when only a few apply. Restart Codex if a new install does not
appear. The installer and discovery locations were checked against the
[official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills)
on 2026-08-23.

## Install anywhere

```
npx skills add ShortArrow/skills -g
```

`-g` writes to `~/.agents/skills/`, which Codex, Copilot (CLI, coding
agent, VS Code), Cursor and Gemini CLI read as a user-level location.
Without `-g` it writes the project's `.agents/skills/` instead.

| Host | User directory | Project directory |
|---|---|---|
| Claude Code | `~/.claude/skills` | `.claude/skills` |
| Codex | `~/.codex/skills`, `~/.agents/skills` | `.agents/skills` |
| Copilot in VS Code | `~/.copilot/skills`, `~/.agents/skills`, and `~/.claude/skills` | `.github/skills`, `.claude/skills`, `.agents/skills` |
| Copilot CLI | `~/.copilot/skills`, `~/.agents/skills` | `.github/skills`, `.claude/skills`, `.agents/skills`; `/add-dir` loads `.github/skills` |
| Cursor | `~/.cursor/skills`, `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills` | `.agents/skills`, `.cursor/skills`, `.claude/skills`, `.codex/skills` |
| Gemini CLI | `~/.gemini/skills`, `~/.agents/skills` (the alias wins ties) | `.gemini/skills`, `.agents/skills` |

A skill whose procedure names a tool carries one row per host and an
"Any other host" row; the forces behind that shape are in the
[design intent](docs/design-intent.md). The prose-only skills need nothing: they name no tool, so there is
nothing for a host to differ about. The directories above were checked
against official documentation on 2026-08-28.

## Skills

### Screenshots

`any-screenshot` is the entry point: a branch table from what you are
capturing to the method that works, plus the property the methods share —
**capture failures do not raise**. They exit 0 and leave an empty image,
so verifying the result is part of taking it.

The rest do the work. `windows-screenshot` carries PowerShell scripts for
capturing a process's windows by PID, the whole desktop, and — through a
one-shot scheduled task — a desktop from an SSH session that has no
window station of its own. `avalonia-screenshot` renders a window
off-screen without starting the application. `flaui-screenshot` drives a
running application through UI Automation, which is the only one of the
three that can capture a single element or act before capturing.

### Writing

`clean-docs` is about documents that outlive the conversation that
produced them — including who they are addressed to, which slips most
when a document is being fixed because someone called it wrong — and about
direction of dependency between them: a README should not lean on a
changelog. `unmachine-prose` is about the sentences
themselves — the participial trailers, triplets and significance
inflation that fill space once the content has run out.
`plain-japanese` is the other axis of the same page: the errors a
human makes just as often — two claims joined into one sentence, a
subject that never meets its predicate, a doubled honorific, one term
spelled two ways, the conclusion left in the last paragraph — grounded
in the public standards (文化庁「公用文作成の考え方」, JTF スタイル
ガイド) rather than in a house style. `regulated-claims` is about the
sentences that are governed whether or not they are true: a health
effect, a No.1, a before and after, a testimonial, a competitor
comparison, a reference price nobody paid, someone else's figure, an
identifiable person. Being able to prove a claim is not the same as
being allowed to make it. `document-structure` is the shape of one
page in any language: the first line of every unit is the only line
most readers reach, headings are read alone as an outline, sequence
gets numbers and fields get columns, and a procedure is one action per
step with its result.
`pdf-transcribe` governs transcription — principally that nothing may be
written which the page does not show. `i18n-parity` keeps a
multilingual site's pages in step — the failure that renders perfectly is a
page edited in one language only — and covers the exception that expires by
itself rather than becoming a permanent hole. `measured-claims` keeps numbers attached
to their measurement — method, date, spread, and what the figure moves
with, since a document can carry two stale numbers that disagree and both
be wrong. `request-approval` obtains confirmation through the current
host's approval path for anything destructive or outward-facing.

### Product

`new-combination` is idea generation after 松本勝's disruptive-innovation
framework — a need and a seed combined for the first time, judged by
empathy times feasibility — and fires on the habits that produce weak
ideas instead: variants of the existing, assets hunting for a use,
features accumulated onto a surface that was supposed to get simpler.

### Engineering

`plan-delegate-verify` splits multi-step work by role — the session model
plans and verifies, subagents on a chosen model implement — and is mostly
about what a plan must say for an implementer that never saw the
conversation, and why a subagent reporting success is not evidence.
`tdd-cycle` is Red-Green-Refactor as the working procedure, written to
fire at the moments that replace it — verifying by running and looking,
fixing a bug before reproducing it, editing untested code bare.
`test-design` is where the cases come from — classes and boundaries out
of the specification, not a mirror of the implementation, which passes by
construction. `tidy-first` keeps structural and behavioural change in separate
commits, and fires on the "while I'm here" cleanup — the urge is right,
the seat in this diff is wrong.
`diagnose-first` holds the line between correlation and cause — the
base rate, the denominator, the refutation decided before acting, and the
pass mark an intermittent fault needs before any fix gets credit.
`state-first` names the states before the operation, keeps a property
apart from a state in a signature, and turns a flag set into one
enumeration, so the case that "just came up" is a missing state and not
a new branch. `design-by-contract` asks, for every condition at an interface, whose
obligation it is: the precondition is the caller's debt and the
postcondition the callee's, a violated contract is a bug while an
unmet expectation is a result, and an interface earns its existence
from a second implementation or a boundary rather than from tidiness.
`slice-first` is about the axis a codebase is cut along: a feature
spread across a controllers folder, a services folder and a
repositories folder is one thought in four diffs, duplication between
features is what buys their independent change, and a check that has
to hold for every request belongs in the pipeline rather than at the
top of each handler. `github-paths` is about the few dozen paths GitHub reads by name: a
`FUNDING.yml` at the root, a `CITATION.cff` under `docs/`, a second
`CODEOWNERS`, a template tried on a feature branch — each is not wrong,
it is invisible, and the feature it was written for simply fails to
appear. `csharp-architect` covers layering and testability in C#.
`tui-debug` reconstructs a terminal UI from redirected output, for when
there is no display to look at. `windows-sandbox` runs tests that would
otherwise take over the keyboard inside Windows Sandbox, and arbitrates
the machine's single sandbox slot between projects — without one, two
runners tear each other's sandbox down. `peer-sessions` reads what other
sessions on the machine are working on through the host's supported
session interface — courtesy information, since a session between two
runs looks exactly like one that has stopped. `grill-me` resolves only the ambiguity
that would change the implementation. `find-skills` searches the public
registry before you write a skill that already exists, and
`adopt-dependency` covers deciding whether to take on what you find —
including what to do when an installer refuses something.
`tool-call-syntax` and `codex` are small operational notes.

## Layout

```
skills/<name>/SKILL.md          the skill
skills/<name>/scripts/          anything it executes
.claude-plugin/marketplace.json plugin grouping
```

`SKILL.md` needs YAML frontmatter with `name` and `description`.

## What a description is for

**The host starts with each skill's name and description; the body is read
only when the skill fires.** `claude plugin details <name>` reports the
Claude Code split. Codex applies a discovery-context budget when many
skills are installed, so descriptions must remain useful if shortened.

```
component            always-on  on-invoke
any-screenshot            ~150       ~960
windows-screenshot        ~170      ~1.1k
```

Three things follow.

**Detail belongs in the body.** It costs nothing until the skill is
actually used, so there is no reason to compress it. The description is
the part paid for continuously, and it only has to be enough to decide.

**Selection is a judgement, not a match.** The model reads the
description and decides whether it applies. Listing synonyms of words
already present buys nothing, and listing them in a second language buys
nothing either — the skills Anthropic ships are English-only and are used
in every language. A description that says the same thing twice is paid
for twice, every session.

**Spend the tokens on boundaries instead.** Where several skills answer
to the same word — four here respond to "screenshot" — the description is
the only place that distinction can be drawn before one of them fires.
Say what the skill is *not* for and which sibling owns that case.

## Other marketplaces

Third-party collections are added the same way rather than copied in.
Vendoring them would mean carrying their licences and their release
cadence.

```
claude plugin marketplace add anthropics/skills
```

These carry `.claude-plugin/marketplace.json`, so `marketplace add` takes
them directly.

| Repository | Covers |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Document formats, artifact building, skill creation |
| [google/skills](https://github.com/google/skills) | Google products and technologies |
| [microsoft/skills](https://github.com/microsoft/skills) | Grounding coding agents in Microsoft SDKs |
| [NVIDIA/skills](https://github.com/NVIDIA/skills) | Physical AI, robotics, simulation, CUDA, RAG |
| [amd/skills](https://github.com/amd/skills) | AMD's optimised software stack |
| [cloudflare/skills](https://github.com/cloudflare/skills) | Building on Cloudflare |
| [android/skills](https://github.com/android/skills) | Android development |
| [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills) | Microsoft documentation |

In Claude Code, every installed skill costs always-on tokens in every
session, so take the plugin that matches the work rather than the whole
catalogue.

## Collections that are not marketplaces

These hold skills but declare no marketplace, so `marketplace add` will
not resolve them. [vercel-labs/skills](https://github.com/vercel-labs/skills)
installs from any git source into Claude Code, Codex, Cursor, OpenCode and
some seventy other agents.

```
npx skills add openai/skills
```

| Repository | Covers |
|---|---|
| [openai/skills](https://github.com/openai/skills) | Catalogue for Codex |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | React, Next.js and deployment practice |
| [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills) | Community collection |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion — programmatic video in React |

`--skill` takes one entry instead of the collection, which matters when
the collection is large.

```
npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices
```

The name it resolves is the one the skill declares, not its directory —
above, `vercel-react-best-practices` lives in `skills/react-best-practices`.

The command shown under **Install in Codex** reaches this repository the
same way, which is also how to use these skills from an agent that has no
plugin system.

By default it writes to `.agents/skills/` in the current project and
symlinks Claude Code at it; `--agent claude-code` writes to
`.claude/skills/` instead. Either way it records what it took in
`skills-lock.json`.

## The format elsewhere

`SKILL.md` is not specific to Claude Code. The same folder-with-a-manifest
shape is used across agents. Instructions that name tools or approval
mechanisms are still host-specific: these skills retain Claude Code's
existing paths and branch to each host's documented capability, with a
last row for hosts that expose none.

| | |
|---|---|
| [agentskills.io](https://agentskills.io) | The specification |
| [claude.com/skills](https://claude.com/skills) | Claude |
| [docs.github.com — about agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | GitHub Copilot |
| [developers.openai.com — tools and skills](https://developers.openai.com/api/docs/guides/tools-skills) | OpenAI, from the API |
| [developers.openai.com — skills in the API](https://developers.openai.com/cookbook/examples/skills_in_api) | The same, worked through |
| [learn.chatgpt.com — build skills](https://learn.chatgpt.com/docs/build-skills) | ChatGPT |
| [geminicli.com — skills](https://geminicli.com/docs/cli/skills/) | Gemini CLI |
| [skills.sh](https://www.skills.sh/) | Directory of published skills |

## Checks

`tests/run-firing-tests.sh` remains the Claude Code behavioural runner.
Its negative scenarios are written against files the skill has no claim
on; the reasoning is in `docs/design-intent.md`.
`tests/check-portability.ps1` checks every manifest and resource reference,
the Claude marketplace membership, and the host rows every branching skill
has to carry:

```powershell
pwsh -File tests/check-portability.ps1
```

## License

MIT. See [LICENSE](LICENSE).
