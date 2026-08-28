---
name: codex
description: Obtain a second Codex reading for a code review, codebase analysis, implementation question, bug investigation, or refactor. From another host, delegate the read-only analysis to the OpenAI Codex CLI. When already running in Codex, never launch a nested Codex CLI merely because this skill fired; analyse directly unless the user explicitly requested an independent second run.
---

# Codex

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code; a structured tool
interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`, a permission prompt with a "rest of the session" option and
`--allow-all` mean Copilot CLI; an "Ask questions" tool, a Task tool and a
Browser tool mean Cursor; `ask_user`, `read_file` and subagents exposed as
tools of their own name mean Gemini CLI. A host that matches none of these
takes the last row.

## When the current host is Codex

Do the requested read-only analysis in the current session. Do not launch
`codex exec` recursively merely because this skill fired. If the user
explicitly asks for an independent second reading, use a supported
subagent or a separate Codex run only when the host policy authorizes it,
then compare the two readings instead of silently merging them.

## From Claude Code or another host

Delegate reading to the Codex CLI; this covers Copilot, Cursor, Gemini
CLI and any other host. The sandbox is read-only, so this analyses and
reports; it never edits.

```
codex exec --full-auto --sandbox read-only --cd <project_directory> "<request>"
```

| Parameter | Meaning |
|---|---|
| `--full-auto` | Run without prompting |
| `--sandbox read-only` | Cannot write — safe for analysis |
| `--cd <dir>` | The project to read |
| `"<request>"` | What to ask. Any language. |

Any other host runs this command through whatever shell access it has.
Where the host has none, say so and do the reading in the current session;
never report a Codex reading that no Codex run produced.

## Examples

Review:

```
codex exec --full-auto --sandbox read-only --cd /path/to/project \
  "Review this project's code and point out what should be improved"
```

Investigate:

```
codex exec --full-auto --sandbox read-only --cd /path/to/project \
  "Find out why the authentication path raises an error"
```

## Procedure from another host

1. Take the request.
2. Identify the project directory — Codex reads only what `--cd` points at.
3. Run the command above.
4. Report the result, and say plainly where it disagrees with your own
   reading rather than silently merging the two.
