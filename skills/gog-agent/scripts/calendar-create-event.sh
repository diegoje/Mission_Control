#!/usr/bin/env bash
# Create a calendar event (quick create) in the primary calendar.
# Usage: calendar-create-event.sh <account> "Summary" "YYYY-MM-DDTHH:MM:SS" "YYYY-MM-DDTHH:MM:SS" "Description"
set -euo pipefail
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}
ACCOUNT=${1:-${GOG_ACCOUNT:-}}
SUMMARY=${2:-}
FROM=${3:-}
TO=${4:-}
DESCRIPTION=${5:-}
if [ -z "$ACCOUNT" ] || [ -z "$SUMMARY" ] || [ -z "$FROM" ] || [ -z "$TO" ]; then
  echo "Usage: $0 <account> \"Summary\" \"from-iso\" \"to-iso\" \"Description\"" >&2
  exit 2
fi
"$GOG_BIN" calendar create primary --summary "$SUMMARY" --from "$FROM" --to "$TO" --description "$DESCRIPTION" --account "$ACCOUNT" --json
