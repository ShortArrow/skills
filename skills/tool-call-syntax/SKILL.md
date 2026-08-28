---
name: tool-call-syntax
description: Recover from a malformed, missing, or silently ignored tool call by using the current host's native tool-call protocol. In Claude Code's XML harness that means exactly antml:function_calls, antml:invoke, and antml:parameter; in Codex, antml is invalid and the exposed structured tool interface owns the syntax. Consult before retrying a call that did not parse or never returned.
---

# Tool Call Syntax

Identify the host from the tools it exposes before choosing a row:
`AskUserQuestion`, `Agent` and `Skill` mean Claude Code; a structured tool
interface with approval requests on blocked calls means Codex;
`askQuestions`, `runSubagent` and `#browser` mean Copilot in VS Code;
`/agent`, a permission prompt with a "rest of the session" option and
`--allow-all` mean Copilot CLI; an "Ask questions" tool, a Task tool and a
Browser tool mean Cursor; `ask_user`, `read_file` and subagents exposed as
tools of their own name mean Gemini CLI. A host that matches none of these
takes the last row.

**Do not translate one host's wire format into another.** Tool syntax is
runtime protocol, not portable skill content.

## Codex, Copilot, Cursor, Gemini CLI, and any other host

Use the structured tool interface exposed by the current runtime.
Choose the tool by its advertised name and pass an object matching its
schema. Never print `antml` tags, XML wrappers, or a guessed JSON envelope
into assistant prose; that text is not a Codex tool call.

After a parse or schema failure:

1. Re-read the exposed tool name and input schema.
2. Send one minimal call with only required fields.
3. If it returns, rebuild the real call from the schema instead of retrying
   the failed text unchanged.

Any other host follows the same three steps.

## Claude Code

### Write this

Every call has this shape. Angle brackets are full-width ＜＞ here to keep
the block inert; a real call uses `<>`.

```
＜antml:function_calls＞
  ＜antml:invoke name="Bash"＞
    ＜antml:parameter name="command"＞ls＜/antml:parameter＞
    ＜antml:parameter name="description"＞list files＜/antml:parameter＞
  ＜/antml:invoke＞
＜/antml:function_calls＞
```

Three tag names, each carrying the `antml:` prefix, opening and closing:

- `antml:function_calls` — the block
- `antml:invoke` — one call, `name` is the exact tool name
- `antml:parameter` — one argument, `name` is the argument name

The prefix is not optional and not decorative. Without it the tags mean
nothing to the parser, and neither does any other wrapper around them.
There is no second spelling to choose between: copy the shape above.

### When a call does not parse

The harness answers `Your tool call was malformed and could not be parsed`
and **nothing runs**. No command executed, no file changed. The reply looks
like every other reply, which is why the mistake survives: the natural next
move is to send the same text again, and the same text fails the same way.

So the next message after a parse failure is not a retry of what just
failed. It is one call, one tool, minimal arguments, written out from the
shape above rather than edited down from the broken attempt:

```
＜antml:function_calls＞
  ＜antml:invoke name="Bash"＞
    ＜antml:parameter name="command"＞echo ok＜/antml:parameter＞
  ＜/antml:invoke＞
＜/antml:function_calls＞
```

If that returns, the syntax is sound and the fault was in the previous
message's tags. Rebuild the real call from the shape — do not paste the
failed one back in.

### What actually goes wrong

Nearly always the block is opened with a name that is not
`antml:function_calls`: a word invented on the spot, or the right word with
the prefix dropped. The three tag names are the first thing to check and
usually the last.

The rest, in order of how often they bite:

1. A closing tag missing the `antml:` prefix while the opening tag has it.
2. A tool name that does not match the one in the tool list, character for
   character.
3. An argument name invented rather than taken from the tool's schema.

### Failing quietly is the real cost

A parse failure produces no error the user can see — only silence where
output should be, then the same broken message again. Repeated across
turns it reads as the agent ignoring instructions, and the user ends up
saying the same thing several times to no effect. Each retry of unchanged
text spends a turn and teaches nothing.

Two rules follow:

- **Never send the same text twice.** If it failed to parse once, it will
  fail identically. Change the tags or change nothing.
- **Suspect your own syntax before the tool.** A tool that returns nothing
  is far more likely to have never been called than to be broken.

### Writing about Claude Code syntax

Naming a tag in ordinary prose risks both a stray invocation and a typo
that propagates. Keep every tag name inside a code block — including in
documents like this one, and including the wrong spellings, which are best
not written down at all.
