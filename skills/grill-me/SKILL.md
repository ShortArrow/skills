---
name: grill-me
description: Resolve only implementation-critical ambiguity.
---

## Host tools

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code; a structured
tool interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`, a permission prompt with a "rest of the session" option and
`--allow-all` mean Copilot CLI; an "Ask questions" tool, a Task tool
and a Browser tool mean Cursor; `ask_user`, `read_file` and subagents
exposed as tools of their own name mean Gemini CLI. A host that
matches none of these takes the last row.

Use the host's native capabilities; do not emit another host's tool names
as calls.

- Claude Code: `Read`, `Grep`, `Glob`, `LS`, `AskUserQuestion`,
  `TodoWrite`, `Agent`, `EnterPlanMode`, `ExitPlanMode`
- Codex: repository search and read tools, a dedicated user-input tool when
  available, and the plan tool when a plan materially helps. Use subagents
  only when the user or governing repository instructions authorize them
- Copilot in VS Code: `askQuestions` for the question, plus the repository
  search and read tools. Use `runSubagent` only when the user or governing
  repository instructions authorize delegation
- Copilot CLI: no question tool is documented (checked 2026-08-28); ask in
  chat. The built-in agents reached with `/agent` are subject to the same
  authorization
- Cursor: the "Ask questions" tool, the repository read and search tools,
  and the Task tool under the same authorization
- Gemini CLI: `ask_user` with type `choice` for the question, `read_file`
  and the search tools for the codebase, and subagents exposed as tools of
  their own name under the same authorization
- Any other host: the repository read and search tools it does expose, and
  the question in chat. Do not name another host's tool to stand in for a
  missing one

## Rules

* Infer from the codebase before asking
* Ask only high-impact decisions
* One question at a time
* Prefer choices over open-ended questions
* Avoid asking about established conventions
* Avoid speculative requirements
* Stop when implementation is safe

