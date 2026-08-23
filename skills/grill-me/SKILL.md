---
name: grill-me
description: Resolve only implementation-critical ambiguity.
---

## Host tools

Use the host's native capabilities; do not emit another host's tool names
as calls.

- Claude Code: `Read`, `Grep`, `Glob`, `LS`, `AskUserQuestion`,
  `TodoWrite`, `Agent`, `EnterPlanMode`, `ExitPlanMode`
- Codex: repository search and read tools, a dedicated user-input tool when
  available, and the plan tool when a plan materially helps. Use subagents
  only when the user or governing repository instructions authorize them

## Rules

* Infer from the codebase before asking
* Ask only high-impact decisions
* One question at a time
* Prefer choices over open-ended questions
* Avoid asking about established conventions
* Avoid speculative requirements
* Stop when implementation is safe

