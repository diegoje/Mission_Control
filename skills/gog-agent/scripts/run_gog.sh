#!/usr/bin/env bash
# Wrapper to run gog commands safely from the agent environment.
# Usage: scripts/run_gog.sh <gog subcommand and flags>

set -euo pipefail

# Ensure workspace and config paths
GOG_CONFIG_DIR=${GOG_CONFIG_DIR:-/data/.config/gogcli}
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}

if [ ! -x "$GOG_BIN" ]; then
  echo "gog binary not found at $GOG_BIN" >&2
  exit 1
fi

# Ensure config dir exists
mkdir -p "$GOG_CONFIG_DIR/keyring" || true

# Load .env safely (for GOG_KEYRING_PASSWORD) without sourcing arbitrary content
ENV_FILE=/data/.openclaw/workspace/.env
if [ -f "$ENV_FILE" ]; then
  # Read lines of form KEY=VALUE and export only the expected keys
  while IFS= read -r line || [ -n "$line" ]; do
    # skip empty or comment lines
    case "$line" in
      ''|\#*) continue ;;
    esac
    # split on first =
    key="${line%%=*}"
    val="${line#*=}"
    # trim possible surrounding single or double quotes from val
    if [ "${val#\'}" != "$val" ] && [ "${val%\'}" != "$val" ]; then
      val="${val#\'}"
      val="${val%\'}"
    elif [ "${val#\"}" != "$val" ] && [ "${val%\"}" != "$val" ]; then
      val="${val#\"}"
      val="${val%\"}"
    fi
    case "$key" in
      GOG_KEYRING_PASSWORD)
        export GOG_PASSPHRASE="$val"
        ;;
      GOG_ACCOUNT)
        export GOG_ACCOUNT="$val"
        ;;
      # add other allowed keys here if needed
    esac
  done < "$ENV_FILE"
fi

# Export GOG_ACCOUNT if provided in env
if [ -z "${GOG_ACCOUNT:-}" ]; then
  # no default account; user must pass --account on command line
  :
fi

# Run gog with passed arguments
# Preserve JSON output where supported
"$GOG_BIN" "$@"
