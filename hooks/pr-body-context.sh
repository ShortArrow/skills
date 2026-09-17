#!/usr/bin/env bash
# PreToolUse hook for `gh pr create` / `gh pr edit`: the body about to be
# posted is a durable artifact, and the moment it is written is inside a
# Bash call, where no skill description can see it. Inject the rule.
#
# The hook input arrives as JSON on stdin. The marketplace entry filters
# with `if: Bash(gh pr *)`, but the filter is applied here as well, so the
# context is injected only for the command it is about (observed on
# 2026-09-11: the hook ran on an unrelated grep when only `if` filtered).
input="$(cat)"
command="$(printf '%s' "$input" | python -c 'import json,sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception:
    print("")' 2>/dev/null)"
case "$command" in
  *"gh pr create"*|*"gh pr edit"*) ;;
  *) exit 0 ;;
esac
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"A pull request body is about to be posted. It is a durable artifact read by someone who never saw this conversation. Before running this command, apply pull-request, clean-docs, document-structure and plain-language (read their SKILL.md if not loaded this session): the body says only what the diff cannot show (why this choice, the convention it follows, when the change shows and when it does not); no file lists, no list of what is not included, no pasted logs or stack traces, no author-side circumstances; repository code is linked at a commit-pinned line, not quoted; a failure names the function and the line; the body is written from the commits and the diff, not from the conversation, with no conversation-local labels (option B, the H1 finding, the thing we discussed); headings that read as an outline; one claim per sentence. A newline in a pull request body renders as a visible line break, so a blank line only where the claim changes, Japanese one sentence per line (a sentence over 120 characters broken at its 読点), an English paragraph on one line, lists tight, no trailing-space or backslash breaks. Show the whole body to the user before running the command, and if it does not meet the rule, rewrite it first."}}
JSON
