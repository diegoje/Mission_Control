#!/usr/bin/env python3
"""
Sync Notion Tasks (Status=Ready for Ops) -> create Todoist tasks and write back the Todoist ID.
Uses NOTION_TOKEN and TODOIST_API_TOKEN from env.
"""
import os, json, urllib.request, urllib.parse, time

NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
TODOIST_TOKEN = os.environ.get('TODOIST_TOKEN')
TASKS_DB_ID = os.environ.get('NOTION_TASKS_DB_ID')
TODOIST_PROJECT_ID = os.environ.get('TODOIST_PROJECT_ID', '6g3JFX554fxr47w7')

if not NOTION_TOKEN or not TODOIST_TOKEN or not TASKS_DB_ID:
    raise SystemExit('Set NOTION_TOKEN, TODOIST_API_TOKEN, and NOTION_TASKS_DB_ID in env')

NOTION_HEADERS = {'Authorization': f'Bearer {NOTION_TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
TODOIST_HEADERS = {'Authorization': f'Bearer {TODOIST_TOKEN}', 'Content-Type': 'application/json'}

AUDIT_PATH = os.path.join('memory','agent-todoist-audit.log')

def audit(agent, action, details):
    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
    entry = {'ts': int(time.time()), 'agent': agent, 'action': action, 'details': details}
    with open(AUDIT_PATH,'a') as f:
        f.write(json.dumps(entry)+"\n")


def notion_query_ready_tasks():
    url = 'https://api.notion.com/v1/databases/' + TASKS_DB_ID + '/query'
    # filter: Status select equals "Ready for Ops" and Todoist Task ID is empty
    body = {
        "filter": {
            "and": [
                {"property": "Status", "select": {"equals": "Ready for Ops"}},
                {"property": "Todoist Task ID", "rich_text": {"is_empty": True}}
            ]
        },
        "page_size": 50
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=NOTION_HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.load(r).get('results', [])


def create_todoist_task(content, due_string=None, priority=1, description=None):
    url = 'https://api.todoist.com/api/v1/tasks'
    payload = {'content': content, 'project_id': TODOIST_PROJECT_ID, 'priority': priority}
    if due_string:
        payload['due_string'] = due_string
    if description:
        payload['description'] = description
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=TODOIST_HEADERS, method='POST')
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def notion_write_todoist_id(page_id, todo_id):
    url = 'https://api.notion.com/v1/pages/' + page_id
    props = {'Todoist Task ID': {'rich_text': [{'text': {'content': todo_id}}]}}
    body = {'properties': props}
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=NOTION_HEADERS, method='PATCH')
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def page_title(page):
    title_prop = page.get('properties',{}).get('Name',{})
    if title_prop and 'title' in title_prop and title_prop['title']:
        return title_prop['title'][0]['text']['content']
    return 'Untitled'


def page_due_string(page):
    d = page.get('properties',{}).get('Due',{})
    if d and d.get('date') and d['date'].get('start'):
        return d['date']['start']
    return None


def page_description(page):
    # try to extract a short description from children? For now, include a link to the Notion page
    return page.get('url')


def main():
    agent='Fred'
    ready = notion_query_ready_tasks()
    if not ready:
        print('No ready tasks found')
        return
    for p in ready:
        pid = p['id']
        title = page_title(p)
        due = page_due_string(p)
        desc = page_description(p)
        todo = create_todoist_task(title, due_string=due, priority=1, description=f"Notion: {desc}")
        todo_id = todo.get('id')
        notion_write_todoist_id(pid, todo_id)
        audit(agent, 'notion->todoist', {'notion_page': pid, 'todoist_id': todo_id})
        print(f'Created Todoist task {todo_id} for Notion page {pid}')

if __name__ == '__main__':
    main()
