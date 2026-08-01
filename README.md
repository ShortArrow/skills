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

`SKILL.md` needs YAML frontmatter with `name` and `description`. The
description decides whether the skill is selected, so it states the
trigger conditions rather than summarising the body.

## License

MIT. See [LICENSE](LICENSE).
