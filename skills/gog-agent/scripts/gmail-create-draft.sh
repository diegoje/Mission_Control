#!/usr/bin/env bash
# Create a Gmail draft
# Usage: gmail-create-draft.sh <account> recipient@example.com "Subject" "Body text"
set -euo pipefail
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}
ACCOUNT=${1:-${GOG_ACCOUNT:-}}
TO=${2:-}
SUBJECT=${3:-}
BODY=${4:-}
if [ -z "$ACCOUNT" ] || [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
  echo "Usage: $0 <account> recipient@example.com \"Subject\" \"Body\"" >&2
  exit 2
fi
# Create draft using gog; body passed via stdin
printf '%s' "$BODY" | "$GOG_BIN" gmail drafts create --to "$TO" --subject "$SUBJECT" --body-file - --account "$ACCOUNT" --json
