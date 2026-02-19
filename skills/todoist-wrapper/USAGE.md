Todoist wrapper (shell) — Usage

Purpose
- Lightweight, non-interactive shell wrapper around the Todoist REST API for OpenClaw agents.
- Agents call this script to add comments, create tasks, move tasks, and perform common operations without handling the raw API.
- All actions are audited to memory/agent-todoist-audit.log with agent name and timestamp.

Location
- skills/todoist-wrapper/todoist_wrapper.sh

Requirements
- TODOIST_API_TOKEN environment variable must be set (your Todoist API token).
- jq installed on the host (used for JSON handling in audit messages).

Audit log
- Path: memory/agent-todoist-audit.log
- Each line is a JSON object: { ts, agent, action, details }

Basic command
- Add a comment to a task (used for timestamped progress notes):
  export TODOIST_API_TOKEN=<your_token>
  bash skills/todoist-wrapper/todoist_wrapper.sh add_comment <AgentName> <task_id> "Comment text..."

Notes for agents
- Pass an agent name as the first argument (e.g., Fred, ContentAgent). This value is recorded in the audit log.
- The script is intentionally minimal; it can be extended with more actions as needed.

Example workflow for an agent (instantiate a template then comment):
- Use the existing template project (Mission Control Templates) and the create_template_instance functionality in the Python wrapper (if available), or manually recreate template tasks in the target project.
- After creating tasks, call add_comment to record progress and notes.

Development
- There is also a Python implementation at skills/todoist-wrapper/todoist_wrapper.py (requires Python 'requests' package). Use it in environments where installing Python packages is allowed.

Security
- Keep TODOIST_API_TOKEN secret. Revoke it at Todoist integrations page if needed.
- The wrapper uses the single token model; if you need per-agent credentials or OAuth, we can extend the wrapper.
