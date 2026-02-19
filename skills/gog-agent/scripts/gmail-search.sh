#!/usr/bin/env bash
# Search Gmail messages. Usage: gmail-search.sh <account> "query" [max]
set -euo pipefail
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}
ACCOUNT=${1:-${GOG_ACCOUNT:-}}
QUERY=${2:-}
MAX=${3:-10}
if [ -z "$ACCOUNT" ] || [ -z "$QUERY" ]; then
  echo "Usage: $0 <account> \"query\" [max]" >&2
  exit 2
fi
"$GOG_BIN" gmail search "$QUERY" --max "$MAX" --account "$ACCOUNT" --json
