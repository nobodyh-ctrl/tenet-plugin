#!/usr/bin/env bash
# Launches guard.py with the first usable Python 3.9+.
# Fails open (exit 0, no decision) when no interpreter is found, so tools keep working;
# scripts/doctor.py reports that state.
SCRIPT="${BASH_SOURCE[0]}"
case "$SCRIPT" in */*) DIR="${SCRIPT%/*}" ;; *) DIR="." ;; esac
GUARD="$DIR/guard.py"
# Native Windows Python cannot open MSYS paths such as /c/Users/...
if command -v cygpath >/dev/null 2>&1; then
  GUARD="$(cygpath -w "$GUARD")"
fi

for candidate in python3 python "py -3"; do
  # shellcheck disable=SC2086 # "py -3" must split into command and flag
  if $candidate -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" </dev/null >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    exec $candidate "$GUARD"
  fi
done

echo "tenet guard: Python 3.9+ not found; guard inactive" >&2
exit 0
