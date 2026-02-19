# Mission Control — Overview

**Goal**: centralize operations for MedForm3D (projects, contacts, ideas, tasks, planning) with clear automation boundaries.

## Sources of truth
- **Notion**: canonical store for Projects, Contacts, SOPs, Ideas, long‑form context
- **Todoist**: execution inbox for day‑to‑day tasks and reminders
- **Gmail + Calendar**: inputs for planning and scheduling

## Autonomy rules (confirmed)
- Gmail read: **OK**
- Calendar read: **OK**
- Notion write: **OK**
- Todoist write: **OK**
- Email sending: **never** unless explicitly requested
- Daily summaries: **only when user asks**, sent on Telegram

## Operating cadence
- On request: daily summary from Gmail + Calendar + Todoist status
- On request: create/update Notion pages for Projects, Contacts, Ideas
- On request: create Todoist tasks and reminders

## Audit
- System actions are logged to `memory/agent-audit.log` and `memory/agent-todoist-audit.log` (local only; not committed)

