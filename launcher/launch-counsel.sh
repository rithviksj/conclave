#!/bin/bash
# conclave counsel launcher: opens ONE new iTerm tab and starts a session in it.
# The command is chosen from a fixed list of constants. Nothing typed by the user
# ever reaches the shell or the AppleScript: an unknown mode is rejected.
#
# Usage: launch-counsel.sh [--print] [lite|full|plain]
#   lite   starts:  claude "/counsel"        (the skill asks for the proposal)
#   full   starts:  claude "/counsel full"   (the skill asks for the proposal)
#   plain  starts:  claude                   (you type /counsel yourself)
#   --print shows the command and opens nothing (for testing)

set -u

PRINT=0
if [ "${1-}" = "--print" ]; then PRINT=1; shift; fi
if [ "$#" -gt 1 ]; then echo "too many arguments" >&2; exit 2; fi

MODE="${1-lite}"   # default only when NO argument is given; an empty string is rejected below
case "$MODE" in
  lite)  CMD='claude "/counsel"' ;;
  full)  CMD='claude "/counsel full"' ;;
  plain) CMD='claude' ;;
  *) echo "usage: launch-counsel.sh [--print] [lite|full|plain]" >&2; exit 2 ;;
esac

if [ "$PRINT" -eq 1 ]; then printf '%s\n' "$CMD"; exit 0; fi

DIR="$(cd "$(dirname "$0")" && pwd)"
osascript "$DIR/counsel-tab.applescript" "$CMD"
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "counsel launcher: osascript failed (exit $rc). Either macOS blocked automation of iTerm (allow it in System Settings > Privacy & Security > Automation) or the command was refused." >&2
  exit "$rc"
fi
