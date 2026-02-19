#!/usr/bin/env bash
# Top-level calendar check: lists calendars and today's events, writes raw and summary JSON, appends audit.
set -euo pipefail
GOG_BIN=${GOG_BIN:-/home/linuxbrew/.linuxbrew/bin/gog}
ACCOUNT=${1:-${GOG_ACCOUNT:-diego@jenzerinnovations.com}}
OUT_DIR=/data/.openclaw/workspace/memory
mkdir -p "$OUT_DIR"
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
RAW_PATH="$OUT_DIR/gog_calendar_raw_$TIMESTAMP.json"
SUMMARY_PATH="$OUT_DIR/calendar_summary_$(date -u +%Y-%m-%d).json"
AUDIT_LOG="/data/.openclaw/workspace/memory/agent-audit.log"

# Use the existing wrapper to ensure envs/load
WRAPPER=/data/.openclaw/workspace/skills/gog-agent/scripts/run_gog.sh

# 1) list calendars
$WRAPPER calendar calendars --account "$ACCOUNT" --json > "$RAW_PATH.tmp"
# 2) for each calendar, fetch events for today (local date range)
TODAY=$(date -I)
TOMORROW=$(date -I -d '+1 day')
python3 - <<PY > "$RAW_PATH"
import json,sys,subprocess,shlex
raw=json.load(open('$RAW_PATH.tmp'))
calendars=raw.get('calendars',[])
results={}
TODAY='$TODAY'
TOMORROW='$TOMORROW'
for c in calendars:
    cid=c['id']
    name=c.get('summary')
    cmd=f"$WRAPPER calendar events '{cid}' --from {TODAY} --to {TOMORROW} --account {ACCOUNT} --json"
    # substitute ACCOUNT into command string
    cmd=cmd.replace('{ACCOUNT}', '%s') % ('$ACCOUNT')
    proc=subprocess.run(shlex.split(cmd),capture_output=True,text=True)
    try:
        ev=json.loads(proc.stdout)
    except Exception:
        ev={'error':proc.stdout+proc.stderr}
    results[name]=ev
out={'generated_at':None,'account':'%s','raw':raw,'events':results}
out['generated_at']=__import__('datetime').datetime.utcnow().isoformat()+'Z'
json.dump(out,open('$RAW_PATH','w'),indent=2)
PY
rm -f "$RAW_PATH.tmp"

# 3) produce compact summary
python3 - <<PY > "$SUMMARY_PATH"
import json,sys
doc=json.load(open('$RAW_PATH'))
summary={'generated_at':doc['generated_at'],'account':doc['account'],'calendars':{}}
for cal,ev in doc['events'].items():
    items=ev.get('events') if isinstance(ev,dict) else None
    count = len(items) if isinstance(items,list) else (len(ev.get('events',[])) if isinstance(ev,dict) else 0)
    # Extract simple titles & times
    entries=[]
    for e in (items or ev.get('events',[])):
        if not isinstance(e,dict): continue
        s=e.get('start',{})
        st=s.get('dateTime') or s.get('date')
        en=e.get('end',{})
        et=en.get('dateTime') or en.get('date')
        entries.append({'summary':e.get('summary'),'start':st,'end':et,'source':e.get('source',{}).get('url')})
    summary['calendars'][cal]={'count':len(entries),'entries':entries}
json.dump(summary,open('$SUMMARY_PATH','w'),indent=2)
PY

# 4) append audit
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | agent: Fred | calendar_check | account=$ACCOUNT | summary=$SUMMARY_PATH | raw=$RAW_PATH" >> "$AUDIT_LOG"

# 5) print compact human summary to stdout
python3 - <<PY
import json
s=json.load(open('$SUMMARY_PATH'))
print('Calendar check summary for',s['account'])
for cal,info in s['calendars'].items():
    print(f"- {cal}: {info['count']} events")
    for e in info['entries']:
        print(f"  • {e['summary']} — {e['start']} to {e['end']}")
PY
