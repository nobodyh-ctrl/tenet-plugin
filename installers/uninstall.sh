#!/usr/bin/env bash
# Removes only the components that tenet installed (per its manifest).
# Foreign rules, settings, MCP servers and Engram data are preserved. The private profile is kept
# unless --purge is given. Every removal is backed up; undo with install.sh --restore <id>.
#
# Usage: installers/uninstall.sh [--dry-run] [--purge] [--config-dir DIR]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=installers/common.sh
. "$HERE/common.sh"

args=(uninstall)
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run|--purge) args+=("$1") ;;
    --config-dir) shift; args+=(--config-dir "${1:?--config-dir needs a value}") ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "error: unknown option $1" >&2; exit 2 ;;
  esac
  shift
done

run_agentcfg "${args[@]}"
