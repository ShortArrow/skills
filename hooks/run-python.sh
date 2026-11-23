#!/usr/bin/env bash
# Starts a hook's Python script with the first interpreter that runs: python3, then python.
#
#   run-python.sh [--deny-without-python] <script.py> [args...]
#   run-python.sh --which        prints the interpreter's name, or nothing
#
# A name on PATH is not enough: Windows puts a python3 there that only prints a
# Store message, and a Linux machine may have python3 and no python. Each name is
# tried with a one-line program and kept only if it is Python 3 and exits 0.
#
# With no interpreter, a hook gives no verdict and exits 0, as it does when its
# script is missing; with --deny-without-python it refuses the PreToolUse call and
# says why, for a guard whose silence would let everything through.
set -u

pick() {
  local p
  for p in python3 python; do
    if "$p" -c 'import sys; sys.exit(sys.version_info[0] != 3)' </dev/null >/dev/null 2>&1; then
      printf '%s' "$p"
      return 0
    fi
  done
  return 1
}

if [ "${1-}" = --which ]; then
  pick
  exit 0
fi

deny=0
if [ "${1-}" = --deny-without-python ]; then
  deny=1
  shift
fi

if python=$(pick); then
  exec "$python" "$@"
fi

if [ "$deny" = 1 ]; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"attack-guard を起動できない：python3 も python も Python 3 として動かないので、このコマンドを確かめられない。確かめずに通すことはしない。ユーザーに Python 3 を入れるか PATH に置いてもらってから、もう一度実行する。"}}'
fi
exit 0
