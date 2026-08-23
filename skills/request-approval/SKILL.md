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

| Host | Approval path |
|---|---|
| Claude Code | Call `AskUserQuestion`; a casual "yes" in chat does not satisfy the classifier |
| Codex | Use the approval request attached to the blocked or escalated tool call; include the exact action in its justification. Use a dedicated user-input tool when the runtime exposes one for that purpose |

Do not simulate either path in prose. If the host exposes no approval
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
