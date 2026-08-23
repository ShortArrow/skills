---
name: plan-delegate-verify
description: |
  Split multi-step work across model tiers: the session model writes the plan, subagents on a chosen model carry out the items, and the session model verifies the result against the plan it wrote. Use when about to plan an implementation, when a task decomposes into items that could run in parallel, or when work will be handed to subagents at all. Covers delegating the fact-gathering without delegating the judgement, what the plan must contain for an implementer that never saw the conversation, why a subagent's "done" is not evidence, what changes when the plan is a test plan and the artefact is itself the pass mark, and when the overhead costs more than the work.
allowed-tools: Agent, Read, Bash, PowerShell, Edit, Write, TodoWrite
---

# Plan, delegate, verify

Four roles, and they are roles rather than models:

| Role | Owns |
|---|---|
| **Scout** | Facts, with citations. No judgement, no recommendation |
| **Planner** | Decomposition, the order, and the check that decides each item is done |
| **Implementer** | One item at a time, in a subagent, with no say over what done means |
| **Verifier** | Whether the result meets the plan — not whether the diff looks reasonable |

Planner and verifier are the same session. That is the point: the tier
trusted with judgement decides what to build and whether it was built, and
never does the typing.

## Host adapter

In Claude Code, preserve the existing assignment, overridable per call:

```
Agent(prompt: "...", model: "opus")     # scout
Agent(prompt: "...", model: "opus")     # implementer
```

The session model is planner and verifier and does neither the reading
nor the typing. Scouts and implementers default to `opus`; set `model`
on the Agent call to move either. Without it the subagent inherits the
session model, which spends the judgement tier on enumeration.

In Codex, use the runtime's subagent tools only when the user or governing
repository instructions explicitly authorize delegation. Prefer the
inherited model unless the user asked for a particular model or tier. If
subagents are unavailable or unauthorized, keep the same planner,
implementer, and verifier responsibilities as separate phases in the
current session; do not pretend a subagent ran.

## Gathering the facts is delegable; deciding from them is not

Writing a plan takes an inventory first — the public surface, the tests
that already exist, the values the specification fixes, where the
boundaries are declared. Reading twenty files to find six facts spends the
planner's context on material it will not use again, and the planner needs
the conclusion, not the file dumps. Send scouts.

What a scout returns is **what exists, with citations**: path and line,
the actual value, the actual name. What it must not return is a
recommendation. An agent that comes back with "these three cases should be
tested" has written the part of the plan the planner exists to write, and
the planner will find it hard not to accept a list that already looks
finished.

Two things worth asking for that a scout will not volunteer:

- **What it looked for and did not find.** Absence is a fact the plan needs
  — no test covers this path, the specification fixes no value here — and
  it never appears in a report of what was found.
- **Where it was unsure.** A scout that guessed rather than read has
  produced a fact indistinguishable from the others.

Split scouts by **question**, not by directory. Three agents each asking
something different — what the wire format fixes, what the existing tests
already assert, what the error paths are — miss different things. Three
agents each given a third of the tree miss the same thing three times.

This does not turn exploration into a delegable step. **Enumeration
delegates; orientation does not.** When the shape is already known — list
every call site, find each declared constant — a scout returns it faster
and cheaper. When the question is still what the shape *is*, reading it
yourself is what produces the plan.

## The plan is an artifact, not a conversation

A subagent starts with none of the conversation. Anything the plan leaves
implicit becomes a guess, and the guess arrives as working code that solves
a different problem.

Each item carries four things:

1. **The file and what changes about it.** Not "the parser" — the path.
2. **The check that decides it is done.** A command with an expected
   result. Decided now, by the planner, not later by whoever implements it.
3. **What it must not touch.** The blast radius, stated, so an implementer
   who sees an adjacent problem leaves it alone.
4. **What it depends on.** Items with no dependency between them run at
   once; items with one do not.

A plan that reads "fix the three issues from the audit" names nothing an
implementer can act on. The severity codes, the option letters and the
positional references all die at the subagent boundary.

## A subagent's report is a claim

Agents report success. They report it after skipping a step, after a test
that was already failing, and after deciding an item was unnecessary.

**Ask for evidence, and make the evidence the return value.** Command
output, a test count, the diff that was written. Then check it against the
item's own criterion — not against whether the answer sounds right. A
schema on the Agent call makes that mechanical: the agent cannot return
prose when the field wants a number.

Two things a verifier looks for that a reviewer of the diff does not:

- **What is missing.** An item the plan listed and the result does not
  contain. This is the common failure and it leaves no trace in the diff.
- **What was widened.** An implementer that fixed something adjacent has
  told you the plan was wrong, or has done something nobody checked.

## When the plan is a test plan

The rule that the implementer has no say over what done means gets tighter,
not looser, because now the artefact **is** the criterion.

- **The planner owns the assertions. The subagent owns the mechanics.**
  What must be true — the inputs, the expected values, the wire strings,
  the counts — is written into the plan. The subagent writes the harness,
  the fixtures and the plumbing around it. An agent that supplies both the
  test and its expected value is deciding its own pass mark, and it will
  decide generously.
- **Say where each expected value came from.** From the specification, or
  from running the code as it is today. The second is a characterisation
  test and is legitimate when pinning existing behaviour is the intent —
  and useless when correctness was the intent, because it records the bug.
  The plan marks which of the two each case is; nothing downstream can
  recover it.
- **Verify that each test can fail.** Passing tests are not evidence: a
  test that asserts nothing passes too. See it red before the fix, or break
  the subject and confirm the test notices. This is the only check that
  distinguishes a test from a decoration, and it is the one a subagent
  reporting "12 passed" has not done.
- **Count the cases against the plan.** A case list makes the missing-item
  check mechanical: nine declared, six written, reported as done is the
  ordinary outcome without it.

## Run the checks yourself

The verifier runs the plan's commands in its own session. A subagent
reporting that the tests pass is not the tests passing; it is a sentence
about the tests.

Where the work was split across worktrees, the verification happens after
the merge, on the combined result. Items that pass alone and fail together
are the reason the phase exists.

## When not to do this

- **The work is one edit.** Planning it, spawning an agent and verifying
  the result costs more than making the change.
- **The task is exploratory.** A plan written before the shape is known
  will be wrong, and the implementer will follow it anyway. Orient first —
  yourself, not through a scout — then plan.
- **The items are not separable.** Two agents editing the same file in
  parallel produce a merge, not progress. Either sequence them or give
  them worktrees.

## The user has to have asked

Spawning subagents spends tokens at a rate the user did not choose by
asking for the feature. In Claude Code, only the user explicitly invoking
this skill by name counts as asking; automatic activation from the
description, or inference from the size of a task, does not. In Codex,
follow the host's delegation policy as well: skill invocation cannot
override a requirement for explicit user or repository authorization.
