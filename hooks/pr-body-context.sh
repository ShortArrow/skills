#!/usr/bin/env bash
# PreToolUse hook for `gh pr create` / `gh pr edit`: the body about to be
# posted is a durable artifact, and the moment it is written is inside a
# Bash call, where no skill description can see it. Inject the rule.
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"A pull request body is about to be posted. It is a durable artifact read by someone who never saw this conversation. Before running this command, apply clean-docs, document-structure and plain-language (read their SKILL.md if not loaded this session): write the body from the commits and the diff, not from the conversation; say what changed, why, and what is left; no conversation-local labels (option B, the H1 finding, the thing we discussed); headings that read as an outline; one claim per sentence. If the body in this command does not meet that, rewrite it before running the command."}}
JSON
