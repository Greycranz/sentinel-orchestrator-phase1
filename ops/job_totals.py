import os, sys, json
repo = r'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1'
os.chdir(repo)
if repo not in sys.path: sys.path.insert(0, repo)
from sentinel_engine.db import SessionLocal
from sentinel_engine.models_agent_mvp import Job

statuses = ["queued","in_progress","completed","failed"]
with SessionLocal() as db:
    totals = {s: db.query(Job).filter(Job.status == s).count() for s in statuses}
print(json.dumps(totals, indent=2))
