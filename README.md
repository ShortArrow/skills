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
about 34,000 characters across the four plugins (`python tests/skill-doctor.py` prints the current total),
so with more than one plugin installed the least-used skills are listed by name only and never fire on their description.
Raise the cap in `~/.claude/settings.json`, or install one plugin:

```json
{ "skillListingBudgetFraction": 0.05 }
```

| Plugin | Skills |
|---|---|
| `screenshot-skills` | [any-screenshot](skills/any-screenshot/SKILL.md), [windows-screenshot](skills/windows-screenshot/SKILL.md), [avalonia-screenshot](skills/avalonia-screenshot/SKILL.md), [flaui-screenshot](skills/flaui-screenshot/SKILL.md), [hyperv-screenshot](skills/hyperv-screenshot/SKILL.md) |
| `writing-skills` | [clean-docs](skills/clean-docs/SKILL.md), [pull-request](skills/pull-request/SKILL.md), [unmachine-prose](skills/unmachine-prose/SKILL.md), [plain-language](skills/plain-language/SKILL.md), [document-structure](skills/document-structure/SKILL.md), [reader-map](skills/reader-map/SKILL.md), [cognitive-rhythm](skills/cognitive-rhythm/SKILL.md), [regulated-claims](skills/regulated-claims/SKILL.md), [pdf-transcribe](skills/pdf-transcribe/SKILL.md), [i18n-parity](skills/i18n-parity/SKILL.md), [measured-claims](skills/measured-claims/SKILL.md), [request-approval](skills/request-approval/SKILL.md) |
| `product-skills` | [new-combination](skills/new-combination/SKILL.md) |
| `engineering-skills` | [plan-delegate-verify](skills/plan-delegate-verify/SKILL.md), [adversarial-verify](skills/adversarial-verify/SKILL.md), [assumption-breaking](skills/assumption-breaking/SKILL.md), [tdd-cycle](skills/tdd-cycle/SKILL.md), [test-design](skills/test-design/SKILL.md), [tidy-first](skills/tidy-first/SKILL.md), [diagnose-first](skills/diagnose-first/SKILL.md), [design-by-contract](skills/design-by-contract/SKILL.md), [slice-first](skills/slice-first/SKILL.md), [github-paths](skills/github-paths/SKILL.md), [architect](skills/architect/SKILL.md), [tui-debug](skills/tui-debug/SKILL.md), [windows-sandbox](skills/windows-sandbox/SKILL.md), [hyperv-clean-vm](skills/hyperv-clean-vm/SKILL.md), [dockur-windows](skills/dockur-windows/SKILL.md), [peer-sessions](skills/peer-sessions/SKILL.md), [grill-me](skills/grill-me/SKILL.md), [tool-call-syntax](skills/tool-call-syntax/SKILL.md), [codex](skills/codex/SKILL.md), [find-skills](skills/find-skills/SKILL.md), [adopt-dependency](skills/adopt-dependency/SKILL.md), [library-design](skills/library-design/SKILL.md), [state-first](skills/state-first/SKILL.md), [assurance-case](skills/assurance-case/SKILL.md), [agent-harness](skills/agent-harness/SKILL.md), [repair-skill](skills/repair-skill/SKILL.md), [timed-wait](skills/timed-wait/SKILL.md) |

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
Each host's own directories,
and how a skill that names a host's tools stays correct on the others,
are in [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## Other collections

Added rather than copied in:
vendoring would mean carrying their licences and their release cadence.
`find-skills` has the same list by owner, for searching one.

```
claude plugin marketplace add anthropics/skills
npx skills add openai/skills
```

| Repository | Covers |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Document formats, artifact building, skill creation |
| [openai/skills](https://github.com/openai/skills) | Catalogue for Codex |
| [google/skills](https://github.com/google/skills) | Google products and technologies |
| [microsoft/skills](https://github.com/microsoft/skills) | Grounding coding agents in Microsoft SDKs |
| [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills) | Microsoft documentation |
| [NVIDIA/skills](https://github.com/NVIDIA/skills) | Physical AI, robotics, simulation, CUDA, RAG |
| [amd/skills](https://github.com/amd/skills) | AMD's optimised software stack |
| [cloudflare/skills](https://github.com/cloudflare/skills) | Building on Cloudflare |
| [android/skills](https://github.com/android/skills) | Android development |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | React, Next.js and deployment practice |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion — programmatic video in React |
| [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills) | Community collection |

Three overlap this catalogue's Japanese layers.
Run one of them on a draft, not several.

| Repository | Covers |
|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | A rewrite pass over finished prose in any language: twenty-five tells ranked by strength, resting on Wikipedia's "Signs of AI writing". Overlaps `unmachine-prose`, which constrains at the moment of writing and restates most of the same shapes |
| [coji/natural-japanese](https://github.com/coji/natural-japanese) | Japanese business documents: a writing constitution, corpus-calibrated catalogues of machine tells and translationese, document types, and a morphological linter |
| [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) | A rewrite pass over machine-generated Japanese: breaks up inanimate subjects and figurative verbs, strips emoji, sentence-final colons, aside parentheses and the half-width spaces around English words, and flattens excess bold, bullets and negated contrasts, with a standard-library Python linter |

## Contributing

Layout, the description budget, host branches, sources,
the checks and the firing tests:
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
The reasoning behind those shapes:
[docs/design-intent.md](docs/design-intent.md).

## License

MIT.
See [LICENSE](LICENSE).
