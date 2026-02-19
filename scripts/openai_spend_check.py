#!/usr/bin/env python3
"""
openai_spend_check.py

Small utility to fetch OpenAI organization usage (completions) grouped by api_key_id
and summarise tokens for last 1 day, last 7 days, and month-to-date.

Usage:
  - Set OPENAI_ADMIN_KEY in environment.
  - Optionally set OPENAI_KEY_ID to filter to a single api_key_id.
  - Run: python3 scripts/openai_spend_check.py

Output: writes /tmp/spend_check_raw.json (raw pages) and prints a JSON summary.
"""
import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse

API_URL = "https://api.openai.com/v1/organization/usage/completions"


def utc_ts(dt):
    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())


def fetch_pages(start_ts, end_ts, group_by=None, api_key_id=None):
    headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_ADMIN_KEY','')}",
               "User-Agent": "openai-spend-check/1.0"}
    if not headers["Authorization"] or headers["Authorization"] == "Bearer ":
        raise RuntimeError("OPENAI_ADMIN_KEY not set in environment")

    q = {"start_time": str(start_ts), "end_time": str(end_ts)}
    # build base url with group_by[]=api_key_id
    params = [("start_time", str(start_ts)), ("end_time", str(end_ts))]
    if group_by:
        for g in group_by:
            params.append(("group_by[]", g))
    if api_key_id:
        # filter parameter (some org APIs accept filter or api_key_id param) — we include as query param api_key_id for compatibility
        params.append(("api_key_id", api_key_id))
    url = API_URL + "?" + urllib.parse.urlencode(params)

    pages = []
    while url:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode()
        except urllib.error.HTTPError as e:
            print("HTTP error", e.code, e.read().decode(), file=sys.stderr)
            raise
        j = json.loads(body)
        pages.append(j)
        # next_page can be an absolute URL, a page token (e.g. 'page_...'), or null
        nxt = j.get("next_page")
        if not nxt:
            url = None
        elif isinstance(nxt, str) and nxt.startswith("http"):
            url = nxt
        else:
            # build URL using page token
            url = API_URL + "?" + urllib.parse.urlencode(params) + "&page=" + urllib.parse.quote(str(nxt))
    return pages


def sum_tokens(pages):
    # pages is a list of page objects; each page contains 'data' -> buckets -> results
    per_key = {}
    total_in = 0
    total_out = 0
    for page in pages:
        for bucket in page.get("data", []):
            for res in bucket.get("results", []):
                key_id = res.get("api_key_id") or res.get("key_id") or "unknown"
                in_t = int(res.get("input_tokens", 0) or 0)
                out_t = int(res.get("output_tokens", 0) or 0)
                total_in += in_t
                total_out += out_t
                if key_id not in per_key:
                    per_key[key_id] = {"input": 0, "output": 0}
                per_key[key_id]["input"] += in_t
                per_key[key_id]["output"] += out_t
    return {"total_input": total_in, "total_output": total_out, "per_key": per_key}


def range_timestamps():
    now = datetime.datetime.utcnow()
    today_start = datetime.datetime(now.year, now.month, now.day, tzinfo=datetime.timezone.utc)
    month_start = datetime.datetime(now.year, now.month, 1, tzinfo=datetime.timezone.utc)
    one_day_ago = now - datetime.timedelta(days=1)
    seven_days_ago = now - datetime.timedelta(days=7)
    return {
        "1d": (utc_ts(one_day_ago), utc_ts(now)),
        "7d": (utc_ts(seven_days_ago), utc_ts(now)),
        "mtd": (utc_ts(month_start), utc_ts(now)),
    }


def main():
    key_filter = os.environ.get("OPENAI_KEY_ID")
    group_by = ["api_key_id"]
    ranges = range_timestamps()
    all_pages = {}
    summary = {}
    for label, (s,e) in ranges.items():
        try:
            pages = fetch_pages(s, e, group_by=group_by, api_key_id=key_filter)
        except Exception as exc:
            print(json.dumps({"error": str(exc)}))
            return 1
        all_pages[label] = pages
        sums = sum_tokens(pages)
        summary[label] = sums
    # save raw
    with open('/tmp/spend_check_raw.json', 'w') as f:
        json.dump(all_pages, f, indent=2)
    out = {"generated_at": datetime.datetime.utcnow().isoformat() + "Z", "summary": summary}
    print(json.dumps(out, indent=2))
    # also write summary file
    summary_path = f"memory/spend_check_summary_{datetime.datetime.utcnow().date().isoformat()}.json"
    with open('/tmp/spend_check_summary.json','w') as f:
        json.dump(out, f, indent=2)
    with open(summary_path,'w') as f:
        json.dump(out, f, indent=2)

    # Update Notion: overwrite the Api usage paragraph and append a timestamped child paragraph
    notion_token = os.environ.get('NOTION_TOKEN')
    parent_page_id = os.environ.get('NOTION_MISSION_PARENT','30b5d455-1f56-803b-98fe-d169dd795d64')
    paragraph_block_id = os.environ.get('NOTION_SPEND_BLOCK','30c5d455-1f56-80fa-9965-df4afd947402')
    if notion_token:
        # compute mtd totals and cost
        mtd = summary['mtd']
        input_t = mtd['total_input']
        output_t = mtd['total_output']
        cost = (input_t * 0.25 / 1_000_000) + (output_t * 2.0 / 1_000_000)
        cost_s = f"${cost:.2f}"
        # update paragraph block
        patch_url = f"https://api.notion.com/v1/blocks/{paragraph_block_id}"
        patch_body = json.dumps({
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Api usage this month: {cost_s}"}}]}
        }).encode()
        req = urllib.request.Request(patch_url, data=patch_body, headers={
            'Authorization': f'Bearer {notion_token}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }, method='PATCH')
        try:
            with urllib.request.urlopen(req) as resp:
                _ = resp.read()
        except Exception as e:
            print('Notion update failed:', e, file=sys.stderr)
    else:
        print('NOTION_TOKEN not set; skipping Notion update')

    return 0


if __name__ == '__main__':
    sys.exit(main())
