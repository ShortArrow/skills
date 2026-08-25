#!/usr/bin/env bash
#
# Run the firing tests of one skill and report which scenarios fired.
#
#   tests/run-firing-tests.sh <skill> [out-dir] [scenario-regex]
#
# Scenarios are read from tests/<skill>/firing-tests.md — every "### Sn"
# heading under "## Should fire" or "## Should not fire", with the prompt
# in the "> " lines that follow — so the document is the only copy. Each
# scenario runs in a fresh headless session inside a fresh git repository
# holding a fixture — tests/fixtures/leap unless the document names
# another in a "Fixture: `tests/fixtures/<name>`" line — and passes when
# it fires on the expected side: a Skill tool_use naming the skill counts as fired. Behavioural
# passes without a Skill call (the procedure followed, the action refused)
# are not detected here; read the transcript for those.
#
# Cost: one run is one full session with every installed skill in the
# system prompt. Measure before scaling — the first probe on this machine
# was 37k input tokens for a one-line prompt.

set -euo pipefail

skill=${1:?skill name}
out=${2:-"${TMPDIR:-/tmp}/firing-tests/${skill}"}
only=${3:-.}
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
doc="$root/tests/$skill/firing-tests.md"
[ -f "$doc" ] || { echo "no $doc" >&2; exit 2; }
fixture="$root/tests/fixtures/$(sed -n 's/^Fixture: `tests\/fixtures\/\([^`]*\)`.*/\1/p' "$doc" | head -1)"
[ "$fixture" != "$root/tests/fixtures/" ] || fixture="$root/tests/fixtures/leap"
mkdir -p "$out"

# Nested launches refuse when CLAUDECODE is set by the parent session.
unset CLAUDECODE

# Signing is on globally and the key is declared per repository, so a
# fresh repository cannot commit until it carries the same identity and
# key as this one. Signing stays on; the fixture commits are signed too.

parse() {
  awk '
    /^## Should fire/     { side="fire"; next }
    /^## Should not fire/ { side="nofire"; next }
    /^## /                { side="" }
    side != "" && /^### S[0-9]+/ { id=$2; expect[id]=side; order[++n]=id; next }
    side != "" && id != "" && /^> / { sub(/^> /, ""); prompt[id]=prompt[id] (prompt[id]==""?"":" ") $0; next }
    END { for (i=1;i<=n;i++) printf "%s\t%s\t%s\n", order[i], expect[order[i]], prompt[order[i]] }
  ' "$doc"
}

pass=0 fail=0
while IFS=$'\t' read -r id expect prompt; do
  [ -n "$prompt" ] || { echo "$id: no prompt parsed" >&2; exit 2; }
  [[ "$id" =~ $only ]] || continue
  work=$(mktemp -d "${out}/${id}.XXXX")
  cp -r "$fixture"/. "$work"/
  git -C "$work" init -q
  for key in user.name user.email user.signingkey; do
    git -C "$work" config "$key" "$(git -C "$root" config "$key")"
  done
  git -C "$work" add -A && git -C "$work" commit -qm "fixture"
  # stdin is the scenario list; without </dev/null the session reads it and the loop ends after one.
  (cd "$work" && claude -p "$prompt" --output-format stream-json --verbose --max-turns 6 </dev/null >"$out/$id.jsonl" 2>"$out/$id.err") || true
  if grep -q "\"name\":\"Skill\"" "$out/$id.jsonl" && grep -q "\"skill\":\"[a-z-]*:\?$skill\"" "$out/$id.jsonl"; then got=fire; else got=nofire; fi
  if [ "$got" = "$expect" ]; then verdict=pass; pass=$((pass+1)); else verdict=FAIL; fail=$((fail+1)); fi
  printf '%-4s expected %-6s got %-6s %s\n' "$id" "$expect" "$got" "$verdict"
done < <(parse)

echo "$pass passed, $fail failed — transcripts in $out"
[ "$fail" -eq 0 ]
