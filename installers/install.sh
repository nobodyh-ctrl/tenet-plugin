#!/usr/bin/env bash
# Installs the facundo-agent-config complementary configuration on Linux (and Git Bash).
# Detects the environment, locates Python 3.9+ and delegates to scripts/agentcfg.py.
# Never installs third-party tools. Run with --dry-run first to preview every change.
#
# Usage: installers/install.sh [--dry-run] [--with-permissions] [--with-plugin] [--with-engram]
#                              [--config-dir DIR] [--restore BACKUP_ID]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=installers/common.sh
. "$HERE/common.sh"

args=(install)
restore=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run|--with-permissions|--with-plugin|--with-engram) args+=("$1") ;;
    --config-dir) shift; args+=(--config-dir "${1:?--config-dir needs a value}") ;;
    --restore) shift; restore="${1:?--restore needs a backup id}" ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "error: unknown option $1" >&2; exit 2 ;;
  esac
  shift
done

if [ -n "$restore" ]; then
  filtered=(restore "$restore")
  for a in "${args[@]:1}"; do
    case "$a" in --with-*) ;; *) filtered+=("$a") ;; esac
  done
  args=("${filtered[@]}")
fi

echo "facundo-agent-config installer - $(uname -s) $(uname -r) / bash ${BASH_VERSION}"
run_agentcfg "${args[@]}"
