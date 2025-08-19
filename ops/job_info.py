import os, sys, json
repo = r'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1'
os.chdir(repo)
if repo not in sys.path: sys.path.insert(0, repo)
from sentinel_engine.db import SessionLocal
from sentinel_engine.models_agent_mvp import Job

jid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
with SessionLocal() as db:
    j = db.get(Job, jid)
    if not j:
        print(json.dumps({"id": jid, "found": False}))
    else:
        print(json.dumps({
            "id": j.id,
            "kind": j.kind,
            "status": j.status,
            "payload_json": j.payload_json
        }, indent=2))
