---
name: gog-agent
description: Run and manage Google Workspace (gog) CLI commands for Gmail, Calendar, Drive, Contacts, Docs and Sheets. Use when the agent needs to read calendars, send email, create events, list drives, or run gog workflows.
---

# gog-agent

Purpose
- Provide a small, reliable wrapper around the gog CLI so the agent can run authenticated Google Workspace commands from the host/container environment where gog is installed and configured.

When to use this skill
- Use when a task requires reading or writing from Google services (Calendar, Gmail, Drive, Contacts, Docs, Sheets) using the gog CLI.
- Trigger when the user explicitly asks to list events, send emails, create calendar events, search Drive, or manage Google resources programmatically via the CLI.

What the skill provides
- scripts/run_gog.sh: A safe wrapper script to execute gog commands with proper environment and account handling.
- guidance and examples for common commands (calendar events, gmail search, drive search).

Security & setup
- The skill assumes gog is installed in the runtime and credentials are persisted in the configured keyring (e.g. /data/.config/gogcli).
- The skill will not store secrets itself. Ensure client_secret.json and the gog keyring live in a persistent, secure mount (example: /docker/openclaw-5mvg/data/.config/gogcli).
- Prefer secrets passed via mounted files or Docker secrets; do not put secrets in SKILL.md.

Examples
- List today’s calendar events:
  scripts/run_gog.sh calendar events primary --from $(date -I) --to $(date -I -d '+1 day') --account you@example.com

- Search Gmail for recent messages:
  scripts/run_gog.sh gmail search 'newer_than:7d' --max 10 --account you@example.com

- List Drive files:
  scripts/run_gog.sh drive search "name:Mission Control" --max 10 --account you@example.com

Implementation notes
- The wrapper ensures GOG_ACCOUNT is set, uses the persistent workspace paths, and returns JSON when the gog command supports --json. It gracefully surfaces errors for the agent to act on.

Notion & Todoist integration (process documented)
- Purpose: create Projects and Contacts rows in the Mission Control Notion workspace and mirror operational tasks into Todoist.

- Databases (Mission Control):
  - Projects DB: expected properties include Name (title), Status (select), Priority (select), Due (date), Tags (multi-select), Todoist Project ID (rich_text), Company (rich_text), Owner (relation)
  - Contacts DB: expected properties include Name (title), Organization (rich_text), Role (rich_text), Email (email), Phone (phone), Notes (rich_text)

- Files & scripts used:
  - skills/todoist-wrapper/notion_to_todoist.py — Notion -> Todoist push script (requires NOTION_TOKEN, TODOIST_TOKEN, NOTION_TASKS_DB_ID)
  - scripts/run_gog.sh and skills/gog-agent/scripts/* — for Gmail fetch and local parsing

- Standard create flow (what the agent will do):
  1. Query Notion for the Projects and Contacts databases (search by name or use known db ids).
  2. Read the database property schema to determine exact property names and types.
  3. Create a new row in the Projects DB using matching property keys and types (title, rich_text, select, number, relation).
  4. Create a new row in the Contacts DB for the contact and capture its page id.
  5. Link the contact to the project by writing the relation property on the project row.
  6. Add short Gmail snippets and notes as children blocks under the project row (simple paragraph blocks). If adding children returns an error, write a local note and retry with a minimal payload.
  7. Create Todoist tasks using TODOIST_TOKEN and record the created task IDs. If the Projects DB supports a Todoist Project ID property, write the task ids back to the Notion row's Todoist Project ID property (rich_text).
  8. Append an audit line to memory/agent-audit.log with Notion page ids and Todoist task ids.

- Safety & policies:
  - The agent will only write to Notion under the Mission Control parent page (page_id 30b5d455-1f56-803b-98fe-d169dd795d64).
  - Notion writes that include PHI/confidential data require manual sign-off (see memory/2026-02-18_mission_control_design.md).
  - The agent will not send emails or download attachments without explicit permission.

- Troubleshooting notes:
  - If Notion returns HTTP 400 on creating children blocks, try a minimal paragraph-only payload or save the content locally and retry later.
  - Always fetch the DB schema before writing to ensure property names match; do not assume property names.

