#!/usr/bin/env bash
#
# Refuse SKILL.md descriptions a host would truncate or reject.
#
# Two hosts set the cap. Claude Code truncates a description at 1,536
# characters (skillListingMaxDescChars), from the tail, which is where the
# "Use when" triggers sit. GitHub Copilot CLI rejects the whole skill when
# the description exceeds 1,024 characters ("Skill description must be at
# most 1024 characters", read from its bundle on 2026-09-11): the skill is
# not listed at all. 1,000 leaves headroom under the tighter of the two.
#
# Wire into a clone once:  see docs/CONTRIBUTING.md (git hook shim in .git/hooks).
set -o errexit -o pipefail -o nounset

limit=1000
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
