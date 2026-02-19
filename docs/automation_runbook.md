# Automation Runbook

## Boundaries
- No email sending unless explicitly requested.
- Notion writes only under Mission Control.
- No secrets in repo.

## Core scripts
- `skills/gog-agent/scripts/run_gog.sh` — Gmail/Calendar access
- `skills/todoist-wrapper/notion_to_todoist.py` — Notion → Todoist sync

## Planned automations
- Todoist → Notion completion sync (cron)
- Daily summary on request

## Audit
- `memory/agent-audit.log`
- `memory/agent-todoist-audit.log`

