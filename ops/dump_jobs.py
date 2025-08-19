import os, sys, json
repo = r'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1'
os.chdir(repo)
if repo not in sys.path: sys.path.insert(0, repo)
from sentinel_engine.db import SessionLocal
from sentinel_engine.models_agent_mvp import Job

def iso(dt): return dt.isoformat() if dt else None
with SessionLocal() as db:
    rows = db.query(Job).order_by(Job.id.desc()).limit(10).all()
out = [{"id": r.id, "kind": r.kind, "status": r.status, "updated_at": iso(r.updated_at)} for r in rows]
print(json.dumps(out, indent=2))
