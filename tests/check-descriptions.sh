#!/usr/bin/env bash
#
# Refuse SKILL.md descriptions long enough for the harness to truncate.
#
# The model-facing skill listing shortens descriptions to fit a context
# budget (hard truncation near 1536 chars); the tail is what gets cut,
# and the tail is where the "Use when" triggers live, so an over-long
# description loses exactly the part recall depends on. 1200 leaves
# headroom: a thesis plus a use-when list fits well under it, and an
# enumeration of the body's sections does not — that belongs in the body.
#
# Wire into a clone once:  see readme (git hook shim in .git/hooks).
set -o errexit -o pipefail -o nounset

limit=1200
root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${1:-$root/skills}"
fail=0

for f in "$target"/*/SKILL.md; do
  len=$(awk '/^---\r?$/{n++; next} n==1' "$f" \
    | awk '/^description:/{d=1} d && /^[a-zA-Z_-]+:/ && !/^description:/{d=0} d{print}' \
    | sed -e 's/^description: *|* *//' -e 's/^  //' | tr -d '\r\n' | wc -c)
  if [ "$len" -gt "$limit" ]; then
    name=$(basename "$(dirname "$f")")
    {
      echo "check-descriptions: $name: description is $len chars (limit $limit)."
      echo "  Fix: keep the thesis and the 'Use when' triggers; move the"
      echo "  enumeration of the body's content into the body. The listing"
      echo "  truncates long descriptions from the tail, which is where the"
      echo "  triggers sit."
    } >&2
    fail=1
  fi
done
exit $fail
