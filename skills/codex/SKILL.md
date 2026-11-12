---
name: codex
description: Obtain a second Codex reading for a code review, codebase analysis, implementation question, bug investigation, or refactor. From another host, delegate the read-only analysis to the OpenAI Codex CLI. When already running in Codex, never launch a nested Codex CLI merely because this skill fired; analyse directly unless the user explicitly requested an independent second run.
---

# Codex

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code;
a structured tool interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`,
a permission prompt with a "rest of the session" option and `--allow-all` mean Copilot CLI;
an "Ask questions" tool, a Task tool and a Browser tool mean Cursor;
`ask_user`,
`read_file` and subagents exposed as tools of their own name mean Gemini CLI.
A host that matches none of these takes the last row.

## When the current host is Codex

Do the requested read-only analysis in the current session.
Do not launch `codex exec` recursively merely because this skill fired.
If the user explicitly asks for an independent second reading,
use a supported subagent or a separate Codex run only when the host policy authorizes it,
then compare the two readings instead of silently merging them.

## From Claude Code or another host

Delegate reading to the Codex CLI; this covers Copilot, Cursor,
Gemini CLI and any other host.
The sandbox is read-only, so this analyses and reports; it never edits.

```
codex exec --sandbox read-only --cd <project_directory> "<request>"
```

| Parameter | Meaning |
|---|---|
| `exec` | Run non-interactively (alias: `e`); `--full-auto` was removed by 0.164.0 and now exits 2 |
| `--sandbox read-only` | Cannot write — safe for analysis |
| `--cd <dir>` | The project to read |
| `"<request>"` | What to ask. Any language. |

`review` is the other non-interactive subcommand — `codex review --uncommitted` reads the working tree's changes.
It takes no subcommands of its own,
so a bare word after it is the prompt:
`codex review help` asks for a review of "help" rather than printing usage.
It consults the model exactly as `exec` does,
so anything said here about a returned reading applies to it too.

Two refusals that look like a failed reading and are not,
both met on codex-cli 0.164.0:

- **Outside a Git repository it refuses to start** — "Not inside a trusted directory and `--skip-git-repo-check` was not specified." Add `--skip-git-repo-check` only when the target genuinely is not a repository;
  for a repository, the message means `--cd` is pointing somewhere else.
- **A piped stdin is appended to the prompt.** The help says so,
  and a run with a prompt argument and a pipe open reports "Reading additional input from stdin…".
  Redirect from `/dev/null` when calling it inside a shell pipeline,
  or the surrounding command's output silently becomes part of the request.

The sandbox is enforced by the operating system,
not by the model's cooperation,
which means the guarantee does not depend on the request being polite.
Verified twice in a throwaway repository under `--sandbox read-only`:
PowerShell `Set-Content`, `cmd /c echo`, `python`, `git commit`,
a write to `%TEMP%` outside the working directory,
and `New-Item -ItemType Directory` all ran and all were refused with "Access to the path … is denied".
No write landed.

Two cautions from testing it rather than trusting it:

- **Read the file, not the exit code.** One of those denied writes was a PowerShell `Set-Content` followed by another statement,
  and the exec reported **exit 0** while the file stayed unchanged.
- **A model saying "denied" is not evidence.** An adversarial verifier reported a run in which the model declined to attempt any route and still reported "write denied" for every one.
  That observation is the verifier's and was not reproduced here.
  Only the executed commands and the file's contents establish what happened — a report is a claim,
  not an observation, as `adversarial-verify` has it.

Any other host runs this command through whatever shell access it has.
Where the host has none,
say so and do the reading in the current session;
never report a Codex reading that no Codex run produced.

## Examples

Review:

```
codex exec --sandbox read-only --cd /path/to/project \
  "Review this project's code and point out what should be improved"
```

Investigate:

```
codex exec --sandbox read-only --cd /path/to/project \
  "Find out why the authentication path raises an error"
```

## Procedure from another host

1. Take the request.
2. Identify the project directory — Codex reads only what `--cd` points at.
3. Run the command above.
4. Report the result, and say plainly where it disagrees with your own reading rather than silently merging the two.
