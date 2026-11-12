---
name: pull-request
description: |
  The body of a pull request, triggered by the moments that pad it or starve it: about to describe what the diff already shows, about to explain the change by the author's own circumstances, about to paste a stack trace, a log or a "verified" section, about to quote the repository's own code in a code block, about to write "X breaks" without naming the function and the line, about to send a body nobody has seen in full, about to open a pull request with its whole body in one command, or about to send a large project's template with a section left thin. The scale sets the coverage: a large open-source project's template, issue link, test plan, breaking changes and checklist are filled in full; a small project or a team's own repository gets only what the diff cannot say. In both, repository code is linked at a commit-pinned line and a newline renders as a visible break. Use when writing or revising a pull request body or a reply to a review.
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
| list what the pull request does not include | on a small project delete it, since what is not in the diff is not in the pull request; on a large project write it under the template's follow-up or out-of-scope heading, and nowhere else |
| send a large project's template with a section left thin | fill every section the template asks for, at the depth its maintainers review at; a thin section costs a review round |
| paste a stack trace, a log excerpt or a "verified" section | one line naming the condition and the observed result; the evidence lives in the commit, the test or a linked run |
| quote the repository's own code in a code block | link the line at the commit it was read at; a code block is for output that came from outside the repository |
| write "this breaks the parser" | name the function and the line and say how it breaks there; if that cannot be named yet, the cause has not been found |
| put a blank line after every sentence, or break a line inside an English paragraph | a blank line only where the claim changes; on GitHub a newline in a body is a visible break, so Japanese takes one sentence per line and English keeps its paragraph on one line |
| send the body straight from the command | show the whole text first; a body typed inside a command is never read as a document |
| open a pull request with its whole body in one command | open it as a draft with a body of at most 120 characters, then write the body as a file and put it in with `gh pr edit --body-file` (Procedure) |
| rewrite the body after one review comment | change what the comment named and nothing else |

## Two scales

The body's coverage is set by who reads it and how many.
Decide the scale before writing, from the receiving repository,
not from the size of the diff.

**A large open-source project.** Many maintainers,
none of whom know the author, a pull request template,
release notes generated from merged pull requests,
and a review queue where a body that makes the reviewer ask one question costs a round trip.
Coverage is required, and the template is the specification:

- The title in the form the project uses (a conventional-commit prefix, an issue number, a component tag),
  read from the last twenty merged pull requests.
- The issue it closes, with the closing keyword the project uses (`Fixes #123`),
  or the discussion it came from.
- Motivation: the problem as the user of the software meets it,
  before the change.
- What changed, at the depth the release notes will need: the behaviour,
  not the files.
- How it was tested: the commands, the platforms, the cases added,
  and what was not tested and why.
- Breaking changes and the migration, under that heading,
  even when the answer is "none".
- Documentation, changelog entry and screenshots for a visible change,
  where the project keeps them.
- Every checklist item the template carries, ticked or explained;
  a sign-off or CLA where the project requires one.
- Follow-ups and out of scope, under the template's own heading,
  so the reviewer does not ask.

A section the template asks for is filled even when the answer is short;
a section it does not ask for is not invented.
`github-paths` says where the template lives.

**A small project or a team's own repository.** Reviewers who know the codebase and the author,
no template or a short one, and release notes written by hand.
Here the body says only what the diff cannot,
and everything below this section is the rule for that scale.
Applying the large-project coverage here produces the padded body the moments table refuses.

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
- The list of things not included, on a small project.
  Written down, it reads as a promise or an apology, and it is neither;
  what the diff lacks, the pull request lacks.
  A large project's template asks for it under its own heading,
  and there it is filled.
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

## Line breaks are visible here

A pull request body is not a Markdown file.
GitHub renders a single newline in an issue,
a pull request or a comment as a line break,
where the same newline in a `.md` file renders as a space (docs.github.com, read 2026-09-17).
So the source convention for repository files, one sentence per line,
changes meaning in a body:
every line ending the writer types is a line ending the reviewer sees.

Place them where the reviewer should see them.
In Japanese that is the technical-writing layout `unmachine-prose`'s Japanese layer describes:
one sentence per line, and a sentence over 120 characters broken at its 読点.
In English a paragraph stays on one line,
because a break after each sentence renders as a column of short lines and reads as verse.
In both, a blank line goes only where the claim changes (`document-structure`),
a list stays tight, and no sentence is broken with two trailing spaces or a backslash to make it fit;
a body has no width to fit.

## Name the target

"The parser breaks on empty input" is a sentence that can be written before the cause is known.
"`parse_header` at `src/parser.py#L42` indexes `line[0]` on an empty line and raises `IndexError`" cannot.
A body that can only describe the failure vaguely is a body written before the failure was located;
locate it, then write.

## Procedure

1. Open the pull request as a draft,
   with the title in the form the receiving repository uses and a body of at most 120 characters:
   the one thing the diff cannot say, or the issue it closes.
   A draft cannot be merged and requests no review from code owners (docs.github.com, read 2026-09-22),
   so nobody reads it before the body exists,
   and the checks run meanwhile.
   The title is settled here because it travels in notifications and mail subjects,
   which a later edit does not reach.
   120 is a detector, not a target:
   a summary of the diff does not fit in it,
   so a first body that overflows is describing what the diff shows.
   Some repositories refuse the draft flag;
   when `gh pr create --draft` fails for that reason,
   open it without the flag and with the same short body.
2. Read the checks.
   On a large project the test plan is written from what ran,
   not from what was meant to run.
3. Write the body to a file and read it as the reviewer will.
   A body composed inside `gh pr create --body` is written without the pause in which a document is read,
   and that is where the material above creeps in.
4. Put it in with `gh pr edit --body-file <file>`,
   then mark the pull request ready.
   Marking it ready is what requests review from the code owners.
5. After a review comment, change what the comment named.
   A comment on one paragraph is not a request to rewrite the body,
   and a rewrite hands the reviewer a new document to read from the top.

## Host branches

The moment inside `gh pr create --body` is one no description can see.
The procedure removes it,
since a body that arrives through `--body-file` was a file first,
and each host covers the command for the session that skips the procedure:

| Host | Cover |
|---|---|
| Claude Code | The writing-skills plugin runs a PreToolUse hook on `gh pr create` and `gh pr edit` that injects this rule as context before the command runs (`hooks/pr-body-context.sh`) |
| Codex | `PreToolUse` in `.codex/hooks.json` or `config.toml` intercepts shell commands (learn.chatgpt.com/docs/hooks, checked 2026-09-17); this catalogue does not wire it, so a project adds the same script there or relies on step 1 of the procedure |
| Copilot | `preToolUse` in `.github/hooks/<name>.json` for Copilot agents (docs.github.com, checked 2026-09-17); whether Copilot CLI reads it is not stated there. Not wired by this catalogue; step 1 of the procedure covers the command |
| Cursor | `beforeShellExecution` or `preToolUse` in `.cursor/hooks.json` (cursor.com/docs/agent/hooks, checked 2026-09-17). Not wired by this catalogue; step 1 of the procedure covers the command |
| Gemini CLI | `BeforeTool` under `hooks` in `settings.json` (geminicli.com/docs/hooks, checked 2026-09-17). Not wired by this catalogue; step 1 of the procedure covers the command |
| Any other host | Open the draft with the short body, write the body to a file, read it in full, then pass the file to `gh pr edit --body-file` |

## How this connects

`github-paths` says where a project's pull request template and CONTRIBUTING live,
and both outrank every rule here on that project.
`clean-docs` keeps conversation-local labels out of the body and makes it answer the reader,
not the reviewer; this skill says which of the reader's questions the body may answer at all.
`document-structure` shapes whatever remains.
`unmachine-prose` catches the closer and the "verified" section on their way in.
The rules here rest on practice.

## Sources

- The host table above cites each host's own documentation for its pre-tool hook,
  all read on 2026-09-17: learn.chatgpt.com/docs/hooks (Codex),
  docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks (Copilot),
  cursor.com/docs/agent/hooks (Cursor) and geminicli.com/docs/hooks (Gemini CLI). docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax,
  read 2026-09-17, for the rendering of a single newline in a pull request body against a `.md` file. docs.github.com/en/pull-requests/reference/pull-requests,
  read 2026-09-22, for a draft not being mergeable,
  code owners not being requested on a draft,
  and ready for review being what requests them.
  No standard stands behind the body rules themselves.
