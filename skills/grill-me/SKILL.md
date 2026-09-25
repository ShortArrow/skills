---
name: grill-me
description: |
  Asking the user, triggered by the moments that produce a questionnaire instead of an answer: about to ask something the repository, the history or the running system could answer, about to send a list of questions before starting, about to ask an open question where three candidates and a default would do, about to ask about a convention the codebase already follows, about to ask about a requirement nobody has raised, or about to keep asking after the implementation is already safe. A question costs the user a context switch and gives back one fact, so it is asked only for what the user alone knows, one at a time, with candidates attached and the rest of the work already done. Use when a request leaves a gap, when an instruction says to confirm with the user, and when about to write a question of any kind.
---

# Grill me

**A question is the most expensive way to get a fact.** It stops the work,
it costs the user a context switch, and it returns one fact,
phrased by someone who does not know what the work needs.
A skill that says "ask the user" produces a questionnaire:
each item is cheap to write and the sum exhausts the person answering,
who ends up filling in a survey so that the model can start.
The model can start on what it knows;
the question is for the one thing it cannot know.

## The moments this replaces

| About to… | Instead |
|---|---|
| ask what the code, the history or the environment would tell you | read it; `Grep`, `git log`, the config file and the running system answer without a context switch |
| send a list of questions before starting | start; do everything the answers do not change, then ask the one that remains |
| ask an open question ("what should the output format be?") | offer the candidates and a default ("CSV as today, or TSV, or Excel; going with CSV unless you say otherwise") |
| ask about a convention the codebase already follows | follow it; the convention is a fact in the code, not a preference to confirm |
| ask about a requirement nobody has raised | leave it; a question about a hypothetical is a hypothetical made real at the user's expense |
| ask again once the implementation is safe | stop; a safe change with a stated assumption beats a confirmed change delivered late |

## Three checks before a question

Each is answered before the question is written,
and a "no" to any of them means the question is not asked.

1. **Is the answer already somewhere I can read?** The repository,
   its history, the issue tracker, the documentation, the running system,
   the test suite.
   "Which database does this use" is in the connection string;
   "what does the team call this" is in the last ten commit messages.
2. **Does only the user know it?** A production path, a customer's name,
   a deadline, which of two valid designs they prefer,
   whether a behaviour was intended.
   A guess about these is a guess about a person's mind.
   A guess about a library's behaviour is a fact one command away.
3. **Does the answer change what I do next?** If both answers lead to the same code,
   the question is curiosity.
   If the answer only matters in a case the request does not cover,
   it is a speculative requirement.

What survives all three is asked, and it is usually one thing.

## The form of a question

- **One at a time.** The second question is often answered by the first,
  and two questions read as the beginning of a list.
- **Prefer choices over open-ended questions.** Candidates show the user what the model already knows,
  and picking one costs less than composing an answer.
  Name a default, so that no reply is also an answer.
- **Say what the answer unblocks.** "The export goes to a path only you know; the rest is done and tested against `./out`." The user then knows the question is the last thing,
  not the first.
- **Carry the work forward under a stated assumption where the cost of being wrong is small.** A reversible choice is made,
  named in the result, and left for the user to overturn.
  A question is reserved for the choice that would waste the work if wrong.

## What not to ask

- Established conventions: the formatter, the branch naming,
  the test layout.
- Speculative requirements:
  "should this also handle the case where…" when nobody said it should.
- Confirmation of what the request already said.
- Anything the model would answer the same way regardless of the reply.

Stop when implementation is safe:
the gap that remains is named in the result as an assumption,
and the user changes it in one line if it is wrong.

## Host tools

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

Use the host's native capabilities;
do not emit another host's tool names as calls.
Where the host has a question tool that takes options,
the candidates go in the options and the default is marked in its label.

- Claude Code: `Read`, `Grep`, `Glob`, `LS`, `AskUserQuestion`,
  `TodoWrite`, `Agent`, `EnterPlanMode`, `ExitPlanMode`
- Codex: repository search and read tools,
  a dedicated user-input tool when available,
  and the plan tool when a plan materially helps.
  Use subagents only when the user or governing repository instructions authorize them
- Copilot in VS Code: `askQuestions` for the question,
  plus the repository search and read tools.
  Use `runSubagent` only when the user or governing repository instructions authorize delegation
- Copilot CLI: no question tool is documented (checked 2026-08-28);
  ask in chat.
  The built-in agents reached with `/agent` are subject to the same authorization
- Cursor: the "Ask questions" tool, the repository read and search tools,
  and the Task tool under the same authorization
- Gemini CLI: `ask_user` with type `choice` for the question,
  `read_file` and the search tools for the codebase,
  and subagents exposed as tools of their own name under the same authorization
- Any other host: the repository read and search tools it does expose,
  and the question in chat.
  Do not name another host's tool to stand in for a missing one

## Where this sits

`request-approval` is a different act:
it asks for permission to do something irreversible,
and the answer is yes or no.
This skill is about information the user holds.
A skill in this catalogue that needs something only the user has,
a file to attach or a failing run to paste,
says so at that step and nowhere else;
`docs/design-intent.md` carries the rule for writing one.
The rules here rest on practice.
