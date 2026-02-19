Todoist wrapper skill for OpenClaw

Purpose
- Provide a non-interactive wrapper around the Todoist REST API so OpenClaw agents can create and manage tasks without managing the raw API calls.

Setup
1. Put your Todoist API token into the environment where OpenClaw runs:
   export TODOIST_API_TOKEN=<your_token>
2. Ensure Python 3 and `requests` are available. Install requests if needed:
   pip install requests

Usage (examples)
- Create a task:
  python3 todoist_wrapper.py create_task Fred <project_id> "Task content here"

- List tasks in a project:
  python3 todoist_wrapper.py list_tasks Fred <project_id>

- Move a task to a section:
  python3 todoist_wrapper.py move_task Fred <task_id> <section_id>

- Complete a task:
  python3 todoist_wrapper.py complete_task Fred <task_id>

- Add a comment to a task (used as timestamped progress note):
  python3 todoist_wrapper.py add_comment Fred <task_id> "Completed step X"

- Instantiate a template project into a real project:
  python3 todoist_wrapper.py create_template Fred <template_project_id> <target_project_id> [target_section_id]

Audit log
- The script writes a JSON-delimited audit log to memory/agent-todoist-audit.log recording agent actions.

Notes
- Agents should call the wrapper and pass their agent name (e.g., "Fred", "ContentAgent") as the second positional argument. This is recorded in the audit log for traceability.
- The wrapper uses the v1 Todoist REST API endpoints currently used in this environment. If Todoist deprecates or changes endpoints, update API_BASE in the script.
