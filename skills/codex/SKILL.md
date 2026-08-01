---
name: codex
description: Run a code review, an analysis, or a question about a codebase through the OpenAI Codex CLI. Use when asked to review code, analyse a whole codebase, explain an implementation, investigate a bug, suggest a refactor, or look into a problem that has resisted a direct approach — that is, when a second independent reading is worth more than continuing alone.
---

# Codex

Delegates reading to the Codex CLI. The sandbox is read-only, so this
analyses and reports; it never edits.

```
codex exec --full-auto --sandbox read-only --cd <project_directory> "<request>"
```

| Parameter | Meaning |
|---|---|
| `--full-auto` | Run without prompting |
| `--sandbox read-only` | Cannot write — safe for analysis |
| `--cd <dir>` | The project to read |
| `"<request>"` | What to ask. Any language. |

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

## Procedure

1. Take the request.
2. Identify the project directory — Codex reads only what `--cd` points at.
3. Run the command above.
4. Report the result, and say plainly where it disagrees with your own
   reading rather than silently merging the two.
