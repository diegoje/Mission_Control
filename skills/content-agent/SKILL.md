---
name: content-agent
description: Periodic content-production agent for MedForm3D. Use when you need an automated worker that pulls Todoist tasks labeled @agent_content, generates content deliverables (hooks, scripts, captions, image prompts/assets), and writes a completion worklog back into the Todoist task (as comments) with links/files. Also use when setting up scheduling/cron and guardrails for content creation automation.
---

# Content Agent (Todoist-driven)

## Operating loop (authoritative)

1) Query Todoist for **open** tasks in project `Mission Control` with label `agent_content`.
2) **Skip** any task that already has label `ready_for_review`.
3) Build the **effective brief**:
   - Base: Todoist task description.
   - Override: latest **human** comment (any comment not starting with `Content Agent:`). Latest human comment wins.
4) Infer intent/type and produce text-only outputs:
   - **Ideas request ("Generate N ideas")** → produce N distinct ideas. Create **one Notion row per idea** in the `Content Creation` database with **Status = Idea** and put the idea into `Brief / Notes`.
   - **Draft request (blog post / LinkedIn / IG / Reel / etc.)** → create **one Notion row** with **Status = In progress** and fill `Draft Text` / `Script` / `Hashtags` / `CTA` as appropriate.
   - **Image-based IG request** → if the Todoist task/comment has an attachment URL, add it to the Notion row `Assets` as an external file link; tailor the caption to that image.
5) Post a "Content Agent Worklog" comment back to the Todoist task including:
   - what you created
   - Notion page URLs
   - assumptions + questions
6) Mark for review:
   - Move the Todoist task to section **Ready for Review**
   - Add label `ready_for_review`
   - **Do NOT remove** `agent_content` (Diego uses removing `ready_for_review` to request iteration).

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
