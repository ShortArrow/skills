#!/usr/bin/env bash
# Starts a hook's Python script with the first interpreter that runs: python3, then python.
#
#   run-python.sh [--deny-without-python] <script.py> [args...]
#   run-python.sh --which        prints the interpreter's path, or nothing
#
# A Linux machine may have python3 and no python, and on Windows the python3 on
# PATH may be the Store stub that only prints a message. So the first of python3
# and python found outside the Store folder (WindowsApps) is taken as it is; only
# when both are in that folder, or absent, is each tried with a one-line program
# and kept if it runs as Python 3. A trial run costs a process on every hook, which
# on Windows came to most of a second.
#
# With no interpreter, a hook gives no verdict and exits 0, as it does when its
# script is missing; with --deny-without-python it refuses the PreToolUse call and
# says why, for a guard whose silence would let everything through.
set -u

pick() {
  local p path
  for p in python3 python; do
    path=$(command -v "$p" 2>/dev/null) || continue
    case "$path" in
      */[Ww]indows[Aa]pps/*) continue ;;
    esac
    printf '%s' "$path"
    return 0
  done
  for p in python3 python; do
    path=$(command -v "$p" 2>/dev/null) || continue
    if "$path" -c 'import sys; sys.exit(sys.version_info[0] != 3)' </dev/null >/dev/null 2>&1; then
      printf '%s' "$path"
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
