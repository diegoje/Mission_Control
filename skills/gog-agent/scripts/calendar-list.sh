#!/usr/bin/env bash
# List calendars for the configured account (JSON)
set -euo pipefail
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}
ACCOUNT=${1:-${GOG_ACCOUNT:-}}
if [ -z "$ACCOUNT" ]; then
  echo "Usage: $0 <account>" >&2
  exit 2
fi
"$GOG_BIN" calendar calendars --account "$ACCOUNT" --json
