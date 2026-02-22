---
name: content-agent
description: Periodic content-production agent for MedForm3D. Use when you need an automated worker that pulls Todoist tasks labeled @agent_content, generates content deliverables (hooks, scripts, captions, image prompts/assets), and writes a completion worklog back into the Todoist task (as comments) with links/files. Also use when setting up scheduling/cron and guardrails for content creation automation.
---

# Content Agent (Todoist-driven)

## Operating loop

1) Query Todoist for open tasks with label `agent_content` (Mission Control project by default).
2) For each task:
   - Add a "claimed" comment (timestamp).
   - Generate the requested deliverable(s) using GPT-5.2 for creative text.
   - If images are requested: generate via the configured image model ("nano banana pro" if available) and save outputs under `/data/.openclaw/workspace/assets/content-agent/<task-id>/`.
   - Post a structured worklog back to the task as one or more Todoist comments.
   - Optionally add label `ready` when deliverable is ready for Diego review.

## Guardrails (non-negotiable)
- Draft-only: never publish/post anywhere automatically.
- No outreach/DMs.
- Treat government work as out-of-scope.
- No secrets in comments.

## Files
- `scripts/run_content_agent.sh` — runner (cron-safe)
- `scripts/content_agent.py` — core loop (Todoist I/O)
- `references/medform3d.md` — business/offer/voice facts (keep updated; source of truth is Notion/website)
- `references/output_templates.md` — comment/worklog templates

## Configuration (env)
- `TODOIST_API_TOKEN` (required)
- `CONTENT_AGENT_PROJECT_NAME` (default: Mission Control)
- `CONTENT_AGENT_LABEL` (default: agent_content)
- `CONTENT_AGENT_DRY_RUN` (default: 0)
- `CONTENT_AGENT_MAX_TASKS` (default: 3)
- `CONTENT_AGENT_REVIEW_SECTION` (default: Ready for Review)
- `CONTENT_AGENT_REVIEW_LABEL` (default: ready_for_review)
- `CONTENT_AGENT_EXCLUDE_LABEL` (default: ready_for_review) — agent must NOT pick these up
- `CONTENT_AGENT_NOTION_DB_ID` (default: Content Creation DB id in this workspace)
- `IMAGE_MODEL` (default: nano-banana-pro) — used only if image generation is enabled

## Scheduling
- Use a cron entry (or OpenClaw scheduler if installed) to run `scripts/run_content_agent.sh` every X hours.
- Always write an audit trail to `memory/agent-todoist-audit.log`.
