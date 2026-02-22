#!/usr/bin/env python3
"""Todoist-driven content agent.

Scope:
- Pull open tasks with label agent_content from a target project
- Post comments for claiming + a placeholder worklog

NOTE: This is the deterministic I/O skeleton. The creative generation step is intentionally
left as a callable hook so it can be implemented using OpenClaw's agent runtime (GPT-5.2)
without embedding secrets or provider SDKs here.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

TODOIST_API = "https://api.todoist.com/api/v1"
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def auth_headers() -> Dict[str, str]:
    tok = os.environ.get("TODOIST_API_TOKEN")
    if not tok:
        raise SystemExit("TODOIST_API_TOKEN is not set")
    return {"Authorization": f"Bearer {tok}"}


def get_json(path: str, params: Optional[dict] = None) -> dict:
    r = requests.get(f"{TODOIST_API}{path}", headers=auth_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def post_json(path: str, payload: dict) -> dict:
    r = requests.post(
        f"{TODOIST_API}{path}",
        headers={**auth_headers(), "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def find_project_id_by_name(name: str) -> str:
    data = get_json("/projects")
    for p in data.get("results", []):
        if p.get("name") == name:
            return p["id"]
    raise SystemExit(f"Project not found: {name}")


def find_label_id_by_name(name: str) -> str:
    data = get_json("/labels")
    for l in data.get("results", []):
        if l.get("name") == name:
            return str(l["id"])
    raise SystemExit(f"Label not found: {name}")


def list_open_tasks(project_id: str) -> List[dict]:
    """List open tasks in a project."""
    data = get_json("/tasks", params={"project_id": project_id})
    return data.get("results", [])


def list_sections(project_id: str) -> List[dict]:
    data = get_json("/sections", params={"project_id": project_id})
    return data.get("results", [])


def find_section_id_by_name(project_id: str, name: str) -> str:
    for s in list_sections(project_id):
        if s.get("name") == name:
            return s["id"]
    raise SystemExit(f"Section not found in project {project_id}: {name}")


def task_has_label(task: dict, label_name: str) -> bool:
    # v1 returns labels as list of label names (strings)
    labels = task.get("labels") or []
    return label_name in labels


def add_comment(task_id: str, content: str) -> None:
    post_json("/comments", {"task_id": task_id, "content": content})


def update_task(task_id: str, payload: dict) -> dict:
    return post_json(f"/tasks/{task_id}", payload)


def notion_headers() -> Dict[str, str]:
    tok = os.environ.get("NOTION_TOKEN")
    if not tok:
        raise SystemExit("NOTION_TOKEN is not set")
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def notion_create_page(database_id: str, props: dict) -> dict:
    r = requests.post(
        f"{NOTION_API}/pages",
        headers=notion_headers(),
        data=json.dumps({"parent": {"database_id": database_id}, "properties": props}),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def main() -> int:
    project_name = os.environ.get("CONTENT_AGENT_PROJECT_NAME", "Mission Control")
    label = os.environ.get("CONTENT_AGENT_LABEL", "agent_content")
    exclude_label = os.environ.get("CONTENT_AGENT_EXCLUDE_LABEL", "ready_for_review")
    review_section_name = os.environ.get("CONTENT_AGENT_REVIEW_SECTION", "Ready for Review")
    review_label = os.environ.get("CONTENT_AGENT_REVIEW_LABEL", "ready_for_review")
    notion_db_id = os.environ.get("CONTENT_AGENT_NOTION_DB_ID", "30f5d4551f5681df854cec8394a19414")
    dry_run = os.environ.get("CONTENT_AGENT_DRY_RUN", "0") == "1"
    max_tasks = int(os.environ.get("CONTENT_AGENT_MAX_TASKS", "3"))

    project_id = find_project_id_by_name(project_name)
    review_section_id = find_section_id_by_name(project_id, review_section_name)

    tasks = [
        t
        for t in list_open_tasks(project_id)
        if task_has_label(t, label) and not task_has_label(t, exclude_label)
    ]
    tasks = tasks[:max_tasks]

    audit_path = "/data/.openclaw/workspace/memory/agent-todoist-audit.log"

    for t in tasks:
        tid = t["id"]
        title = t.get("content", "")
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] picked task {tid} :: {title}\n")

        claim = f"Content Agent: claimed at {now_iso()}. I will generate deliverables and post a worklog here."
        worklog = (
            "Content Agent Worklog (placeholder)\n"
            f"- Task: {title}\n"
            f"- Started: {now_iso()}\n\n"
            "Next: creative generation step must be executed by OpenClaw runtime (GPT-5.2 / image model).\n"
        )

        if dry_run:
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(f"[{now_iso()}] DRY_RUN would claim + worklog + move-to-review for task {tid}\n")
            continue

        add_comment(tid, claim)
        time.sleep(0.4)
        add_comment(tid, worklog)
        time.sleep(0.4)

        # Persist a record in Notion (Content Creation DB).
        # Keep it minimal; richer fields can be filled by the creative worker.
        todoist_url = f"https://todoist.com/app/task/{tid}"
        try:
            notion_create_page(
                notion_db_id,
                {
                    "Name": {"title": [{"type": "text", "text": {"content": title}}]},
                    "Status": {"select": {"name": "Ready"}},
                    "Todoist Task ID": {"rich_text": [{"type": "text", "text": {"content": str(tid)}}]},
                    "Todoist Task URL": {"url": todoist_url},
                },
            )
        except Exception as e:
            add_comment(tid, f"Content Agent: WARNING — failed to write Notion record: {e}")

        # Mark ready for Diego review: move to section + add review label.
        existing = t.get("labels") or []
        if review_label not in existing:
            existing = list(existing) + [review_label]
        update_task(tid, {"section_id": review_section_id, "labels": existing})
        time.sleep(0.4)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
