---
name: pull-request
description: |
  The body of a pull request, triggered by the moments that pad it: about to describe what the diff already shows, about to explain the change by the author's own circumstances, about to list what the pull request does not include, about to paste a stack trace, a log excerpt or a "verified" section, about to quote the repository's own code in a code block, about to write "X breaks" without naming the function and the line, or about to send a body nobody has seen in full. The body says only what the diff cannot: why this choice, how it stays consistent with the code around it, and under which conditions the change shows and does not. Its length follows the diff, code from the same repository is linked at a commit-pinned line rather than quoted, and a review comment is answered by changing what it named and nothing else. Use when writing or revising a pull request body or a reply to a review, on your own repository or someone else's.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Pull request

A pull request body is read beside its diff by someone who has the diff open.
Everything the diff shows, they already have;
what they do not have is why the diff looks the way it does,
and that is the whole of what the body is for.

## The moments this replaces

| About to… | Instead |
|---|---|
| describe what the diff already shows | delete it; the reviewer is reading the diff, not a summary of it |
| explain the change by the author's own circumstances (a deadline, a downstream project, a preference) | the body is for the receiving repository; say what the change does for it, or say nothing |
| list what the pull request does not include | delete the list; what is not in the diff is not in the pull request |
| paste a stack trace, a log excerpt or a "verified" section | one line naming the condition and the observed result; the evidence lives in the commit, the test or a linked run |
| quote the repository's own code in a code block | link the line at the commit it was read at; a code block is for output that came from outside the repository |
| write "this breaks the parser" | name the function and the line and say how it breaks there; if that cannot be named yet, the cause has not been found |
| send the body straight from the command | show the whole text first; a body typed inside a command is never read as a document |
| rewrite the body after one review comment | change what the comment named and nothing else |

## Only what the diff cannot say

Three things live outside the diff and inside the body:

- **Why this choice.** The alternative that was there and the reason it lost,
  in one sentence each.
- **How it stays consistent with the code around it.** The convention the change follows is in lines the diff does not touch;
  name it, so the reviewer does not have to check.
- **When it shows.** The condition under which the change is visible,
  and the condition under which it is not.
  "Only when the retry budget is exhausted; a first-attempt success is unchanged" tells the reviewer what to try.

Everything else in a body is either in the diff or about the author.

## What stays out

- What the diff shows: which files, which functions, what was renamed.
- The author's side.
  A pull request to someone else's repository carries none of the sender's circumstances;
  the receiving project owes nothing to them and cannot act on them.
- The list of things not included.
  Written down, it reads as a promise or an apology, and it is neither;
  what the diff lacks, the pull request lacks.
- Long evidence: a full stack trace, a log excerpt,
  a section headed "verified" or "confirmed".
  A reviewer who doubts the fix wants the test, not the transcript.

## Length follows the diff

A one-line diff gets a one-line body.
A body longer than its diff is explaining something the diff should have made clear,
or carrying material from the list above.

## Link, do not quote

Code that is in the repository is referred to by a link pinned to a commit:

```
https://github.com/<owner>/<repo>/blob/<full sha>/<path>#L<from>-L<to>
```

Line numbers move with the next commit;
a link that carries the commit hash does not.
On GitHub, pressing `y` on a file view rewrites the URL to the pinned form.
A code block is reserved for what did not come from the repository:
the output of a command, an error message, a response body.

## Name the target

"The parser breaks on empty input" is a sentence that can be written before the cause is known.
"`parse_header` at `src/parser.py#L42` indexes `line[0]` on an empty line and raises `IndexError`" cannot.
A body that can only describe the failure vaguely is a body written before the failure was located;
locate it, then write.

## Procedure

1. Show the whole body before it is sent.
   A body composed inside `gh pr create --body` is written without the pause in which a document is read,
   and that is where the material above creeps in.
   Write it to a file, read it as the reviewer will, then send it.
2. After a review comment, change what the comment named.
   A comment on one paragraph is not a request to rewrite the body,
   and a rewrite hands the reviewer a new document to read from the top.

## Host branches

The moment inside `gh pr create --body` is one no description can see,
so it is covered per host:

| Host | Cover |
|---|---|
| Claude Code | The writing-skills plugin runs a PreToolUse hook on `gh pr create` and `gh pr edit` that injects this rule as context before the command runs (`hooks/pr-body-context.sh`) |
| Codex | `PreToolUse` in `.codex/hooks.json` or `config.toml` intercepts shell commands (learn.chatgpt.com/docs/hooks, checked 2026-09-17); this catalogue does not wire it, so a project adds the same script there or relies on step 1 of the procedure |
| Copilot | `preToolUse` in `.github/hooks/<name>.json` for Copilot agents (docs.github.com, checked 2026-09-17); whether Copilot CLI reads it is not stated there. Not wired by this catalogue; step 1 of the procedure covers the command |
| Cursor | `beforeShellExecution` or `preToolUse` in `.cursor/hooks.json` (cursor.com/docs/agent/hooks, checked 2026-09-17). Not wired by this catalogue; step 1 of the procedure covers the command |
| Gemini CLI | `BeforeTool` under `hooks` in `settings.json` (geminicli.com/docs/hooks, checked 2026-09-17). Not wired by this catalogue; step 1 of the procedure covers the command |
| Any other host | Write the body to a file, read it in full, then pass the file to the command |

## How this connects

`clean-docs` keeps conversation-local labels out of the body and makes it answer the reader,
not the reviewer; this skill says which of the reader's questions the body may answer at all.
`document-structure` shapes whatever remains.
`unmachine-prose` catches the closer and the "verified" section on their way in.
The rules here rest on practice.

## Sources

- The host table above cites each host's own documentation for its pre-tool hook,
  all read on 2026-09-17: learn.chatgpt.com/docs/hooks (Codex),
  docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks (Copilot),
  cursor.com/docs/agent/hooks (Cursor) and geminicli.com/docs/hooks (Gemini CLI).
  No standard stands behind the body rules themselves.
