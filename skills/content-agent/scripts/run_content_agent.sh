#!/usr/bin/env bash
set -euo pipefail

cd /data/.openclaw/workspace

# Default config
: "${CONTENT_AGENT_PROJECT_NAME:=Mission Control}"
: "${CONTENT_AGENT_LABEL:=agent_content}"
: "${CONTENT_AGENT_DRY_RUN:=0}"
: "${CONTENT_AGENT_MAX_TASKS:=3}"

# Ensure token is present
: "${TODOIST_API_TOKEN:?TODOIST_API_TOKEN must be set}"

# Create audit log dir
mkdir -p memory assets/content-agent

echo "[$(date -Is)] content-agent run (dry_run=$CONTENT_AGENT_DRY_RUN max=$CONTENT_AGENT_MAX_TASKS)" >> memory/agent-todoist-audit.log

python3 /data/.openclaw/workspace/skills/content-agent/scripts/content_agent.py "$@"
