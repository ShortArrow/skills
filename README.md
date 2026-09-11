# skills

Personal [Agent Skills](https://agentskills.io) for Claude Code, Codex,
GitHub Copilot, Cursor and Gemini CLI.
Each skill's `description` in its `SKILL.md` is the summary the host reads;
the table below links to them.

## Install in Claude Code

```
/plugin marketplace add ShortArrow/skills
```

Then install whichever set applies.

Claude Code sends the model one listing of every loaded skill and caps it at 1% of the context window (8,000 characters at 200k).
The descriptions here are deliberately long,
about 28,000 characters across the four plugins,
so with more than one plugin installed the least-used skills are listed by name only and never fire on their description.
Raise the cap in `~/.claude/settings.json`, or install one plugin:

```json
{ "skillListingBudgetFraction": 0.05 }
```

| Plugin | Skills |
|---|---|
| `screenshot-skills` | [any-screenshot](skills/any-screenshot/SKILL.md), [windows-screenshot](skills/windows-screenshot/SKILL.md), [avalonia-screenshot](skills/avalonia-screenshot/SKILL.md), [flaui-screenshot](skills/flaui-screenshot/SKILL.md), [hyperv-screenshot](skills/hyperv-screenshot/SKILL.md) |
| `writing-skills` | [clean-docs](skills/clean-docs/SKILL.md), [unmachine-prose](skills/unmachine-prose/SKILL.md), [plain-language](skills/plain-language/SKILL.md), [document-structure](skills/document-structure/SKILL.md), [reader-map](skills/reader-map/SKILL.md), [cognitive-rhythm](skills/cognitive-rhythm/SKILL.md), [regulated-claims](skills/regulated-claims/SKILL.md), [pdf-transcribe](skills/pdf-transcribe/SKILL.md), [i18n-parity](skills/i18n-parity/SKILL.md), [measured-claims](skills/measured-claims/SKILL.md), [request-approval](skills/request-approval/SKILL.md) |
| `product-skills` | [new-combination](skills/new-combination/SKILL.md) |
| `engineering-skills` | [plan-delegate-verify](skills/plan-delegate-verify/SKILL.md), [adversarial-verify](skills/adversarial-verify/SKILL.md), [assumption-breaking](skills/assumption-breaking/SKILL.md), [tdd-cycle](skills/tdd-cycle/SKILL.md), [test-design](skills/test-design/SKILL.md), [tidy-first](skills/tidy-first/SKILL.md), [diagnose-first](skills/diagnose-first/SKILL.md), [design-by-contract](skills/design-by-contract/SKILL.md), [slice-first](skills/slice-first/SKILL.md), [github-paths](skills/github-paths/SKILL.md), [csharp-architect](skills/csharp-architect/SKILL.md), [tui-debug](skills/tui-debug/SKILL.md), [windows-sandbox](skills/windows-sandbox/SKILL.md), [hyperv-clean-vm](skills/hyperv-clean-vm/SKILL.md), [peer-sessions](skills/peer-sessions/SKILL.md), [grill-me](skills/grill-me/SKILL.md), [tool-call-syntax](skills/tool-call-syntax/SKILL.md), [codex](skills/codex/SKILL.md), [find-skills](skills/find-skills/SKILL.md), [adopt-dependency](skills/adopt-dependency/SKILL.md), [library-design](skills/library-design/SKILL.md), [state-first](skills/state-first/SKILL.md), [assurance-case](skills/assurance-case/SKILL.md), [agent-harness](skills/agent-harness/SKILL.md), [timed-wait](skills/timed-wait/SKILL.md) |

## Install in Codex

Ask Codex's built-in skill installer to install the repository,
or use the agent-neutral installer:

```
npx skills add ShortArrow/skills
```

The latter installs under `.agents/skills/`,
one of the repository and user locations Codex scans.
Select individual skills instead of the whole catalogue when only a few apply.
Restart Codex if a new install does not appear.
The installer and discovery locations were checked against the [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills) on 2026-08-23.

## Install anywhere

```
npx skills add ShortArrow/skills -g
```

`-g` writes to `~/.agents/skills/`, which Codex,
Copilot (CLI, coding agent, VS Code),
Cursor and Gemini CLI read as a user-level location.
Without `-g` it writes the project's `.agents/skills/` instead.

| Host | User directory | Project directory |
|---|---|---|
| Claude Code | `~/.claude/skills` | `.claude/skills` |
| Codex | `~/.codex/skills`, `~/.agents/skills` | `.agents/skills` |
| Copilot in VS Code | `~/.copilot/skills`, `~/.agents/skills`, and `~/.claude/skills` | `.github/skills`, `.claude/skills`, `.agents/skills` |
| Copilot CLI | `~/.copilot/skills`, `~/.agents/skills` | `.github/skills`, `.claude/skills`, `.agents/skills`; `/add-dir` loads `.github/skills` |
| Cursor | `~/.cursor/skills`, `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills` | `.agents/skills`, `.cursor/skills`, `.claude/skills`, `.codex/skills` |
| Gemini CLI | `~/.gemini/skills`, `~/.agents/skills` (the alias wins ties) | `.gemini/skills`, `.agents/skills` |

The directories above were checked against official documentation on 2026-08-28.
How a skill that names a host's tools stays correct on the others is in [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## Other marketplaces

Third-party collections are added the same way rather than copied in.
Vendoring them would mean carrying their licences and their release cadence.

```
claude plugin marketplace add anthropics/skills
```

These carry `.claude-plugin/marketplace.json`,
so `marketplace add` takes them directly.

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

In Claude Code, every installed skill costs always-on tokens in every session,
and the listing budget above decides which descriptions the model sees at all,
so take the plugin that matches the work rather than the whole catalogue.

## Collections that are not marketplaces

These hold skills but declare no marketplace,
so `marketplace add` will not resolve them.
[vercel-labs/skills](https://github.com/vercel-labs/skills) installs from any git source into Claude Code,
Codex, Cursor, OpenCode and some seventy other agents.

```
npx skills add openai/skills
```

| Repository | Covers |
|---|---|
| [openai/skills](https://github.com/openai/skills) | Catalogue for Codex |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | React, Next.js and deployment practice |
| [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills) | Community collection |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion — programmatic video in React |

`--skill` takes one entry instead of the collection,
which matters when the collection is large.

```
npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices
```

The name it resolves is the one the skill declares,
not its directory — above,
`vercel-react-best-practices` lives in `skills/react-best-practices`.

The command shown under **Install in Codex** reaches this repository the same way,
which is also how to use these skills from an agent that has no plugin system.

By default it writes to `.agents/skills/` in the current project and symlinks Claude Code at it;
`--agent claude-code` writes to `.claude/skills/` instead.
Either way it records what it took in `skills-lock.json`.

## The format elsewhere

`SKILL.md` is not specific to Claude Code.
The same folder-with-a-manifest shape is used across agents.
Instructions that name tools or approval mechanisms are still host-specific:
these skills retain Claude Code's existing paths and branch to each host's documented capability,
with a last row for hosts that expose none.

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

## Contributing

Layout, the description budget, host branches, sources,
the checks and the firing tests:
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
The reasoning behind those shapes:
[docs/design-intent.md](docs/design-intent.md).

## License

MIT.
See [LICENSE](LICENSE).
