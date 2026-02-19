# Todoist Rules (Mission Control)

Todoist is the execution inbox for day‑to‑day tasks and reminders.

## Rules
- Use Todoist for operational tasks (calls, follow‑ups, reminders, execution items).
- Do **not** store long‑form project context in Todoist; that belongs in Notion.
- Tasks created from Notion should carry a reference back to the Notion page when possible.

## Automation
- Notion → Todoist (primary)
  - Script: `skills/todoist-wrapper/notion_to_todoist.py`
  - Trigger: Notion Task Status == “Ready for Ops” and Todoist Task ID is empty
  - Action: create Todoist task; write back the Todoist ID to Notion
  - Audit: `memory/agent-todoist-audit.log`

- Todoist → Notion completion sync (planned)
  - Mark completed tasks in Notion and append completion timestamp

