# skills

Personal [Agent Skills](https://agentskills.io) for Claude Code.

Each skill answers a question that comes up repeatedly and is easy to get
wrong the first time — which capture method fits this target, what a
document may not assume its reader knows, what a transcription is not
allowed to invent.

## Install

```
/plugin marketplace add ShortArrow/skills
```

Then install whichever set applies.

| Plugin | Skills |
|---|---|
| `screenshot-skills` | any-screenshot, windows-screenshot, avalonia-screenshot, flaui-screenshot |
| `writing-skills` | clean-docs, pdf-transcribe, request-push |
| `engineering-skills` | csharp-architect, tui-debug, grill-me, tool-call-syntax, codex |

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
produced them, and about direction of dependency between them: a README
should not lean on a changelog. `pdf-transcribe` governs transcription —
principally that nothing may be written which the page does not show.
`request-push` asks before publishing.

### Engineering

`csharp-architect` covers layering and testability in C#.
`tui-debug` reconstructs a terminal UI from redirected output, for when
there is no display to look at. `grill-me` resolves only the ambiguity
that would change the implementation. `tool-call-syntax` and `codex`
are small operational notes.

## Layout

```
skills/<name>/SKILL.md          the skill
skills/<name>/scripts/          anything it executes
.claude-plugin/marketplace.json plugin grouping
```

`SKILL.md` needs YAML frontmatter with `name` and `description`.

## What a description is for

**The description is loaded into every session; the body is read only
when the skill fires.** `claude plugin details <name>` reports the split.

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

- [anthropics/skills](https://github.com/anthropics/skills)
- [openai/skills](https://github.com/openai/skills)
- [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills)
- [microsoftDocs/skills](https://github.com/MicrosoftDocs/Agent-Skills/tree/main/skills)
- [cloudflare/skills](https://github.com/cloudflare/skills)
- [android/skills](https://github.com/android/skills)

## License

MIT. See [LICENSE](LICENSE).
