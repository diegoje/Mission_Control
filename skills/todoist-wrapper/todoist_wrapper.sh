#!/usr/bin/env bash
# Simple shell wrapper for Todoist actions using curl. Non-interactive.
# Requires TODOIST_API_TOKEN env var and workspace root.
API_BASE="https://api.todoist.com/api/v1"
TOKEN="${TODOIST_API_TOKEN}"
AUDIT_FILE="memory/agent-todoist-audit.log"

if [ -z "$TOKEN" ]; then
  echo "TODOIST_API_TOKEN not set" >&2
  exit 1
fi

audit(){
  AGENT="$1"
  ACTION="$2"
  DETAILS="$3"
  TS=$(date +%s)
  mkdir -p "$(dirname "$AUDIT_FILE")"
  printf '%s\n' "{\"ts\": $TS, \"agent\": \"$AGENT\", \"action\": \"$ACTION\", \"details\": $DETAILS}" >> "$AUDIT_FILE"
}

add_comment(){
  AGENT="$1"
  TASK_ID="$2"
  shift 2
  COMMENT="$*"
  BODY=$(jq -nc --arg task_id "$TASK_ID" --arg content "$COMMENT" '{task_id:$task_id, content:$content}')
  resp=$(curl -s -X POST "$API_BASE/comments" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$BODY")
  code=$(jq -r '.id // ""' <<<"$resp")
  if [ -n "$code" ]; then
    audit "$AGENT" "add_comment" "{\"task_id\":\"$TASK_ID\",\"comment_id\":\"$code\"}"
    echo "$resp"
    return 0
  else
    echo "Failed to add comment: $resp" >&2
    return 2
  fi
}

# CLI dispatch
cmd="$1"
case "$cmd" in
  add_comment)
    add_comment "$2" "$3" "${@:4}"
    ;;
  *)
    echo "Usage: $0 add_comment <AgentName> <task_id> <comment text...>"
    exit 1
    ;;
esac
