#!/usr/bin/env bash
# List today's calendar events for the primary calendar
set -euo pipefail
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}
ACCOUNT=${1:-${GOG_ACCOUNT:-}}
FROM=${2:-$(date -I)}
TO=${3:-$(date -I -d '+1 day')}
if [ -z "$ACCOUNT" ]; then
  echo "Usage: $0 <account> [from] [to]" >&2
  exit 2
fi
"$GOG_BIN" calendar events primary --from "$FROM" --to "$TO" --account "$ACCOUNT" --json
