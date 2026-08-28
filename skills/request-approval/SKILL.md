---
name: request-approval
description: |
  Obtain confirmation through the current host's approval mechanism for an action it would otherwise refuse — pushing, rewriting history, amending, resetting, reverting, deleting files or models or images, stopping a remote service, anything destructive, irreversible or outward-facing. Ordinary chat agreement may not satisfy a runtime approval gate. Use whenever such an action is wanted or pending, and whenever one has already been refused.
allowed-tools: AskUserQuestion, Bash, PowerShell, Read
---

# Request Approval

Approval has to arrive through the **current host's approval path** and
name what will actually happen. Agreement in ordinary conversation may not
be the signal the runtime gate reads.

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code; a structured
tool interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`, a permission prompt with a "rest of the session" option and
`--allow-all` mean Copilot CLI; an "Ask questions" tool, a Task tool
and a Browser tool mean Cursor; `ask_user`, `read_file` and subagents
exposed as tools of their own name mean Gemini CLI. A host that
matches none of these takes the last row.

| Host | Approval path |
|---|---|
| Claude Code | Call `AskUserQuestion`; a casual "yes" in chat does not satisfy the classifier |
| Codex | Use the approval request attached to the blocked or escalated tool call; include the exact action in its justification. Use a dedicated user-input tool when the runtime exposes one for that purpose |
| Copilot in VS Code | Ask through the `askQuestions` tool (`#vscode/askQuestions`); one question, with the action and its scale as the option labels. Autopilot answers the carousel automatically, so under Autopilot take the Any other host row |
| Copilot CLI | No question tool is documented (checked 2026-08-28); use the row below for the question itself. State the exact action and its scale in one chat message and stop. The permission prompt (Yes / Yes for the rest of the session / No and tell Copilot what to do differently) covers the tool call and is not a decision on the action |
| Cursor | Use the "Ask questions" tool: one question, with the targets and their scale as the option labels. The agent keeps working while the question waits, so stop it yourself until an answer arrives |
| Gemini CLI | Call `ask_user` with type `choice`, 2 to 4 options, the recommended one first and a "don't" option always present |
| Any other host | Ask one question in chat with the same labels, then stop and wait. Silence is not consent. Never write the question and the answer both yourself |

Do not simulate any of these paths in prose. If the host exposes no approval
mechanism for the action, stop and let the user perform it.

**Localize.** Write the question and the option labels in whatever
language the conversation is in. The examples here are English.

## The handshake

1. **Establish exactly what the action would do**, read back from the
   system rather than from memory. What that means per family is below.
2. **Use the host approval path** with one question stating the targets
   and their scale. In Claude Code, call `AskUserQuestion`: recommended
   option first, labels concrete — the branch, the count, the size — and
   always offer a "don't" option. In Codex, put the same facts in the
   tool-call justification or dedicated approval prompt.
   In Copilot in VS Code, Cursor and Gemini CLI, the same facts go
   into the host's question tool; in Copilot CLI and in any other
   host, into the one chat message that precedes the stop.
3. **Act on the selection**, then report what changed: the ref update,
   the freed space, the number of commits rewritten.

A selection covers the action it named. It does not extend to the next
one, or to a wider version of the same one.

## What to establish first

| Action | Read back before asking |
|---|---|
| push | branch, and `git log @{u}..HEAD --oneline`. No upstream: say so and show recent local commits |
| force push, history rewrite | how many commits change, whether the content is identical, and that other clones will need `git fetch && git reset --hard` |
| `commit --amend`, `reset --hard`, `rebase` | what is discarded, and whether it has been pushed |
| `revert` | which commit. A revert adds a commit and destroys nothing — say so, or the answer gets weighed against a risk that is not there |
| deleting files, models, images, volumes | the list, each size, the total, and whether it can be fetched again |
| stopping a service, a container, a remote process | what goes down, who else is on it, and how it comes back |

## Rules

- **Never `--force` or `--no-verify` unless the user asked.** Prefer
  `--force-with-lease`, and say in the option description that it refuses
  if the remote moved.
- **Do not ask about a risk that is not there.** Overstating turns the
  handshake into noise, and the next real one gets waved through.
- **If the action is still refused after approval, stop.** Say what was
  attempted and what it needs, and let the user run it. Do not reach for
  a different tool to get the same effect.
- **The question is the record.** Someone reading the transcript later
  should be able to tell what was authorised without reconstructing it.
