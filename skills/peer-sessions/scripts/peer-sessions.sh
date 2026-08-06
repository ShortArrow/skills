#!/usr/bin/env bash
# What other Claude Code sessions are doing, from the files they leave behind.
#
# Prints one row per session whose transcript was touched inside the window:
# last activity, working directory, git branch, and the task it says it is on.
#
# Reads metadata and the task store only. The transcripts themselves reach
# tens of megabytes, so nothing here opens one whole.
#
# Usage: peer-sessions.sh [minutes]   (default 60)
set -u

WINDOW=${1:-60}
ROOT="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

[ -d "$ROOT/projects" ] || { echo "no projects directory under $ROOT" >&2; exit 1; }

printf '%-6s %-30s %-20s %s\n' 'SEEN' 'CWD' 'BRANCH' 'TASK'

find "$ROOT/projects" -maxdepth 2 -name '*.jsonl' -mmin "-$WINDOW" -printf '%T@ %p\n' 2>/dev/null |
  sort -rn |
  while read -r ts path; do
    sid=$(basename "$path" .jsonl)

    # cwd and gitBranch are recorded on entries after the first, so the file is
    # scanned for the first occurrence rather than parsed as a header. The
    # directory name under projects/ is a lossy encoding of the same path and
    # cannot be turned back into one.
    cwd=$(grep -m1 -o '"cwd":"[^"]*"' "$path" 2>/dev/null | head -1 | sed 's/.*:"//; s/"$//; s/\\\\/\\/g')
    branch=$(grep -m1 -o '"gitBranch":"[^"]*"' "$path" 2>/dev/null | head -1 | sed 's/.*:"//; s/"$//')

    task=$(
      for f in "$ROOT/tasks/$sid"/*.json; do
        [ -e "$f" ] || continue
        cat "$f"
      done | tr -d '\n' | grep -o '{[^{]*"status": *"in_progress"[^}]*}' | head -1 |
        grep -o '"subject": *"[^"]*"' | sed 's/.*: *"//; s/"$//'
    )
    [ -n "${task:-}" ] || task='-'

    b=${branch:--}
    printf '%-6s %-30s %-20s %s\n' \
      "$(date -d "@${ts%.*}" +%H:%M 2>/dev/null || echo '?')" \
      "$(basename "${cwd:-?}")" "${b:0:20}" "${task:0:60}"
  done
