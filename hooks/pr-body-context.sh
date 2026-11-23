#!/usr/bin/env bash
# PreToolUse hook for a command that posts to a pull request: the body of
# `gh pr create` / `gh pr edit`, or a reply through `gh pr comment`,
# `gh pr review` with a body, or `gh api` on a comment or review endpoint.
# The text is written inside a Bash call, where no skill description can
# see it. Inject the rule for that kind of text.
#
# The hook input arrives as JSON on stdin. The marketplace entries filter
# with `if: Bash(gh pr *)` and `if: Bash(gh api *)`, but the filter is
# applied here as well, so the context is injected only for the command it
# is about (observed on 2026-09-11: the hook ran on an unrelated grep when
# only `if` filtered). `issues/<n>/comments` is included because a comment
# in a pull request's conversation is posted there; a plain issue comment
# gets the same rule, which is written to hold for both.
input="$(cat)"
python=$(bash "$(dirname "$0")/run-python.sh" --which)
[ -n "$python" ] || exit 0
command="$(printf '%s' "$input" | "$python" -c 'import json,sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception:
    print("")' 2>/dev/null)"
kind=$(printf '%s' "$command" | "$python" -c '
import re, sys
c = sys.stdin.read()
if re.search(r"gh pr (create|edit)\b", c):
    print("body")
elif re.search(r"gh pr comment\b", c):
    print("reply")
elif re.search(r"gh pr review\b", c) and re.search(r"(^|\s)(--body|--body-file|-b|-F)(\s|=|$)", c):
    print("reply")
elif re.search(r"gh api\b", c):
    posts = re.search(r"\bbody=|--input\b", c)
    rest = re.search(r"/(pulls/\d+/(comments|reviews)|pulls/comments/\d+/replies|issues/\d+/comments)\b", c)
    graphql = re.search(r"\bgraphql\b", c) and re.search(r"\b(addPullRequestReview\w*|addComment)\b", c)
    if (rest and posts) or graphql:
        print("reply")
' 2>/dev/null)
case "$kind" in
  body) ;;
  reply)
    cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"A comment on a pull request or an issue is about to be posted, usually a reply to a review. It is read by someone who never saw this conversation. Before running this command, apply pull-request (its section A reply to a review), clean-docs and plain-language (read their SKILL.md if not loaded this session): what the code decides (how many, which, in what order, what is logged) is stated first as what the code predicts, and the reviewer is asked only whether what they saw differs; another comment is pointed at with its cause in one sentence and a link to it, never by its number alone; repository code is linked at a commit-pinned line, not quoted; no conversation-local labels (option B, the H1 finding, the thing we discussed); a reply changes what the comment named and nothing else. A newline in a comment renders as a visible line break, so a blank line only where the claim changes, Japanese one sentence per line, an English paragraph on one line. Write the reply to a file and show the whole text to the user before posting it."}}
JSON
    exit 0 ;;
  *) exit 0 ;;
esac
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"A pull request body is about to be posted. It is a durable artifact read by someone who never saw this conversation. Before running this command, apply pull-request, clean-docs, document-structure and plain-language (read their SKILL.md if not loaded this session): first decide the scale from the receiving repository: on a large open-source project follow its pull request template and fill every section in full (title form, issue link, motivation, what changed at release-note depth, how tested, breaking changes, docs and changelog, checklist, follow-ups under its own heading); on a small project or a team repository the body says only what the diff cannot show (why this choice, the convention it follows, when the change shows and when it does not), with no file lists, no list of what is not included, no pasted logs or stack traces, no author-side circumstances; repository code is linked at a commit-pinned line, not quoted; a failure names the function and the line; the body is written from the commits and the diff, not from the conversation, with no conversation-local labels (option B, the H1 finding, the thing we discussed); headings that read as an outline; one claim per sentence. A newline in a pull request body renders as a visible line break, so a blank line only where the claim changes, Japanese one sentence per line (a sentence over 120 characters broken at its 読点), an English paragraph on one line, lists tight, no trailing-space or backslash breaks. Open the pull request as a draft with a body of at most 120 characters first (the one thing the diff cannot say, or the issue it closes), read the checks, then write the full body to a file, show it to the user, put it in with gh pr edit --body-file, and mark the pull request ready; if this command already carries a full body in --body, stop and follow that order instead."}}
JSON
