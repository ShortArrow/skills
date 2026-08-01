---
name: tool-call-syntax
description: Checklist for not breaking the XML syntax of a tool call. Wrapping a call in a tag that does not exist makes the harness fail to parse it, and nothing runs at all — no output, no file written, so the failure is invisible from the outside and looks like the agent silently stalling. Consult after seeing "malformed tool call" or "could not be parsed", when a tool result never arrives, or when the same failure repeats across turns.
---

# Tool Call Syntax

When the agent itself mistypes the XML around a tool call, the harness
answers `Your tool call was malformed and could not be parsed` and **runs
nothing**. There is no output and no side effect, so from the user's side
it looks like the agent went quiet or started repeating itself. The agent
believes it ran the tool, which is what makes the loop hard to leave.

The characteristic form of the mistake is an invented wrapper:

```
court
<invoke name="Bash">
...
</invoke>
court
```

Neither `court` nor a bare `<invoke>` is part of the grammar. Nothing
about the response distinguishes this from a working call, so it repeats
until the wrapper itself is suspected.

## The syntax

A call goes inside an `antml:function_calls` block as an `antml:invoke`,
with arguments as `antml:parameter`.

- Block: `antml:function_calls`
- Each call: `antml:invoke`, with the exact tool name in `name`
- Each argument: `antml:parameter`, with the argument name in `name`

Shape (angle brackets below are full-width ＜＞ to keep this inert; real
calls use `<>`):

```
＜antml:function_calls＞
  ＜antml:invoke name="Bash"＞
    ＜antml:parameter name="command"＞ls＜/antml:parameter＞
    ＜antml:parameter name="description"＞list files＜/antml:parameter＞
  ＜/antml:invoke＞
＜/antml:function_calls＞
```

**Bare `<invoke>`, `<function_calls>` and `<parameter>` are invalid.** The
`antml:` prefix is always required, and inventing a wrapper such as
`court` is not a variation on the grammar.

## Before calling

1. Is the opening tag `antml:function_calls` — not `court`, not
   `function_calls` without the prefix?
2. Does each call start with `antml:invoke name="<exact tool name>"`?
3. Is every argument an `antml:parameter name="<argument name>"`?
4. Do the closing tags carry the `antml:` prefix too?
5. **Are you about to spell a tag in prose?** Describing the syntax to a
   user in ordinary text risks both a stray invocation and a typo. Keep it
   in a code block.

## Recovering without repeating it

On `malformed` or `could not be parsed`, **identify one cause before
retrying**. Re-sending the same text reproduces the same failure exactly,
so a retry without a hypothesis costs a turn and learns nothing.

1. Suspect the opening tag name first. A foreign wrapper is the most
   likely culprit.
2. Check the `antml:` prefix on every tag.
3. If still unclear, call a single tool with minimal arguments to isolate
   it.
4. Do not keep asking the user the same question. They can only see that
   something is broken.

## Notes

- This file writes broken tags **inside code blocks** for illustration.
  Never outside one, in prose or in an actual call.
- If a tool seems to have run without returning anything, suspect your own
  syntax first. Your typo is far more likely than a fault in the tool.
