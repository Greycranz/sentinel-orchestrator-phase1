import os, sys, json
from datetime import datetime, timezone
repo = r'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1'
os.chdir(repo)
if repo not in sys.path: sys.path.insert(0, repo)
from sentinel_engine.db import SessionLocal
from sentinel_engine.models_agent_mvp import Job

with SessionLocal() as db:
    j = Job(kind='echo', payload_json=json.dumps({"msg":"hi"}),
            status='queued',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc))
    db.add(j)
    db.flush()            # get PK before commit
    jid = j.id
    db.commit()
print(json.dumps({"seeded_id": jid}))
