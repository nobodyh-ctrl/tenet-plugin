#!/usr/bin/env bash
# Shared helpers for the Bash entry points. Sourced, not executed.

find_python() {
  local candidate
  for candidate in python3 python "py -3"; do
    # shellcheck disable=SC2086 # "py -3" must split into command and flag
    if $candidate -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

run_agentcfg() {
  local python cli
  if ! python="$(find_python)"; then
    echo "error: Python 3.9+ not found. Install it with your package manager (e.g. 'sudo apt install python3') and re-run." >&2
    exit 1
  fi
  cli="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/agentcfg.py"
  if command -v cygpath >/dev/null 2>&1; then
    cli="$(cygpath -w "$cli")"
  fi
  # shellcheck disable=SC2086
  exec $python "$cli" "$@"
}
