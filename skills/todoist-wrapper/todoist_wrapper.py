#!/usr/bin/env python3
"""
Simple non-interactive Todoist wrapper for OpenClaw agents.
Usage: Set TODOIST_API_TOKEN in environment. Call functions from other scripts or run via CLI.
"""
import os
import sys
import json
import time
from typing import List, Optional
import requests

API_BASE = os.environ.get("TODOIST_API_BASE", "https://api.todoist.com/api/v1")
TOKEN = os.environ.get("TODOIST_API_TOKEN")
AUDIT_PATH = os.path.join("memory","agent-todoist-audit.log")

if not TOKEN:
    raise SystemExit("TODOIST_API_TOKEN not set in environment")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def audit(agent_name: str, action: str, details: dict):
    entry = {"ts": int(time.time()), "agent": agent_name, "action": action, "details": details}
    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
    with open(AUDIT_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# Core operations

def create_task(agent_name: str, project_id: str, content: str, section_id: Optional[str] = None,
                due_string: Optional[str] = None, labels: Optional[List[str]] = None,
                priority: int = 1, description: Optional[str] = None) -> dict:
    payload = {"content": content, "project_id": project_id, "priority": priority}
    if section_id:
        payload["section_id"] = section_id
    if due_string:
        payload["due_string"] = due_string
    if labels:
        payload["labels"] = labels
    if description:
        payload["description"] = description

    r = requests.post(f"{API_BASE}/tasks", headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    resp = r.json()
    audit(agent_name, "create_task", {"project_id": project_id, "task_id": resp.get("id"), "content": content})
    return resp


def list_tasks(agent_name: str, project_id: Optional[str] = None):
    url = f"{API_BASE}/tasks"
    if project_id:
        url += f"?project_id={project_id}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    resp = r.json()
    audit(agent_name, "list_tasks", {"project_id": project_id, "count": len(resp)})
    return resp


def move_task(agent_name: str, task_id: str, section_id: str):
    url = f"{API_BASE}/tasks/{task_id}/move"
    payload = {"section_id": section_id}
    r = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    resp = r.json()
    audit(agent_name, "move_task", {"task_id": task_id, "section_id": section_id})
    return resp


def complete_task(agent_name: str, task_id: str):
    url = f"{API_BASE}/tasks/{task_id}/close"
    r = requests.post(url, headers=HEADERS)
    r.raise_for_status()
    audit(agent_name, "complete_task", {"task_id": task_id})
    return {"task_id": task_id, "status": "completed"}


def add_comment(agent_name: str, task_id: str, content: str):
    url = f"{API_BASE}/comments"
    payload = {"task_id": task_id, "content": content}
    r = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    resp = r.json()
    audit(agent_name, "add_comment", {"task_id": task_id, "comment_id": resp.get("id")})
    return resp


# Template instantiation: copy tasks from template project into target project
# Simple approach: read tasks from template project and recreate them in target project as new tasks.

def create_template_instance(agent_name: str, template_project_id: str, target_project_id: str, target_section_id: Optional[str] = None):
    # list template project tasks
    tasks = list_tasks(agent_name, project_id=template_project_id)
    created = []
    parent_map = {}
    for t in tasks:
        # only top-level tasks first (parent_id == None)
        if not t.get("parent_id"):
            resp = create_task(agent_name, target_project_id, t.get("content"), section_id=target_section_id,
                               due_string=None, labels=None, priority=t.get("priority",1), description=t.get("description",""))
            parent_map[t.get("id")] = resp.get("id")
            created.append(resp)
    # now recreate subtasks
    for t in tasks:
        if t.get("parent_id"):
            parent_new = parent_map.get(t.get("parent_id"))
            if parent_new:
                payload = {"content": t.get("content"), "project_id": target_project_id, "parent_id": parent_new}
                r = requests.post(f"{API_BASE}/tasks", headers=HEADERS, data=json.dumps(payload))
                r.raise_for_status()
                created.append(r.json())
    audit(agent_name, "create_template_instance", {"template_project": template_project_id, "target_project": target_project_id, "created_count": len(created)})
    return created


# Minimal CLI wrapper for simple calls
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    agent = sys.argv[2] if len(sys.argv) > 2 else "Fred"
    try:
        if cmd == 'create_task':
            project_id = sys.argv[3]
            content = sys.argv[4]
            res = create_task(agent, project_id, content)
            print(json.dumps(res, indent=2))
        elif cmd == 'list_tasks':
            project_id = sys.argv[3] if len(sys.argv) > 3 else None
            res = list_tasks(agent, project_id)
            print(json.dumps(res, indent=2))
        elif cmd == 'move_task':
            task_id = sys.argv[3]
            section_id = sys.argv[4]
            res = move_task(agent, task_id, section_id)
            print(json.dumps(res, indent=2))
        elif cmd == 'complete_task':
            task_id = sys.argv[3]
            res = complete_task(agent, task_id)
            print(json.dumps(res, indent=2))
        elif cmd == 'add_comment':
            task_id = sys.argv[3]
            comment = sys.argv[4]
            res = add_comment(agent, task_id, comment)
            print(json.dumps(res, indent=2))
        elif cmd == 'create_template':
            template_project = sys.argv[3]
            target_project = sys.argv[4]
            target_section = sys.argv[5] if len(sys.argv) > 5 else None
            res = create_template_instance(agent, template_project, target_project, target_section)
            print(json.dumps(res, indent=2))
        else:
            print("Usage: todoist_wrapper.py <command> <agent> [args...]")
    except requests.HTTPError as e:
        print("HTTP error:", e.response.status_code, e.response.text)
        raise
