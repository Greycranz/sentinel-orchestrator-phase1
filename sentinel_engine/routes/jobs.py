from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from ..db import get_engine
from ..security import guard_api_key

router_v0 = APIRouter(prefix="/v0/jobs", tags=["jobs"])
router    = APIRouter(prefix="/jobs",    tags=["jobs"])

DDL = """
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  payload_json TEXT,
  status TEXT NOT NULL DEFAULT 'queued',
  created_at TEXT NOT NULL,
  claimed_by TEXT,
  claimed_at TEXT,
  completed_at TEXT,
  output_json TEXT
);
"""

def ensure_schema():
  eng = get_engine()
  with eng.begin() as cx:
    cx.exec_driver_sql(DDL)

ensure_schema()

class EnqueueJob(BaseModel):
  kind: str
  payload_json: str | None = None

def _uuid_sql(cx):
  return cx.exec_driver_sql("SELECT lower(hex(randomblob(4)))||'-'||lower(hex(randomblob(2)))||'-'||lower(hex(randomblob(2)))||'-'||lower(hex(randomblob(2)))||'-'||lower(hex(randomblob(6)))").first()[0]

def _enqueue(body: EnqueueJob):
  eng = get_engine()
  now = datetime.now(timezone.utc).isoformat()
  with eng.begin() as cx:
    job_id = _uuid_sql(cx)
    cx.exec_driver_sql(
      "INSERT INTO jobs(id,kind,payload_json,status,created_at) VALUES(?,?,?,?,?)",
      (job_id, body.kind, body.payload_json or "{}", "queued", now)
    )
  return {"id": job_id, "kind": body.kind, "status": "queued"}

def _claim(agent_id: str):
  eng = get_engine()
  now = datetime.now(timezone.utc).isoformat()
  with eng.begin() as cx:
    # claim the oldest queued job atomically
    row = cx.exec_driver_sql(
      "SELECT id, kind, payload_json FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1"
    ).first()
    if not row:
      return {}  # no job
    job_id, kind, payload_json = row
    cx.exec_driver_sql(
      "UPDATE jobs SET status='claimed', claimed_by=?, claimed_at=? WHERE id=? AND status='queued'",
      (agent_id, now, job_id)
    )
    # confirm claimed
    chk = cx.exec_driver_sql("SELECT status FROM jobs WHERE id=?", (job_id,)).first()
    if not chk or chk[0] != "claimed":
      return {}  # race lost
  return {"id": job_id, "kind": kind, "payload_json": payload_json}

class CompleteJob(BaseModel):
  status: str
  output_json: str | None = None

def _complete(job_id: str, body: CompleteJob):
  if body.status not in ("completed","failed"):
    raise HTTPException(status_code=400, detail="bad_status")
  eng = get_engine()
  now = datetime.now(timezone.utc).isoformat()
  with eng.begin() as cx:
    upd = cx.exec_driver_sql(
      "UPDATE jobs SET status=?, completed_at=?, output_json=? WHERE id=?",
      (body.status, now, body.output_json or "{}", job_id)
    )
    if upd.rowcount == 0:
      raise HTTPException(status_code=404, detail="job_not_found")
  return {"ok": True, "id": job_id, "status": body.status}

@router_v0.post("/enqueue", dependencies=[Depends(guard_api_key)])
def enqueue_v0(body: EnqueueJob): return _enqueue(body)

@router.post("/enqueue", dependencies=[Depends(guard_api_key)])
def enqueue(body: EnqueueJob):     return _enqueue(body)

@router_v0.get("/claim", dependencies=[Depends(guard_api_key)])
def claim_v0(agent_id: str = Query(...)): return _claim(agent_id)

@router.get("/claim", dependencies=[Depends(guard_api_key)])
def claim(agent_id: str = Query(...)):     return _claim(agent_id)

@router_v0.post("/{job_id}/complete", dependencies=[Depends(guard_api_key)])
def complete_v0(job_id: str, body: CompleteJob): return _complete(job_id, body)

@router.post("/{job_id}/complete", dependencies=[Depends(guard_api_key)])
def complete(job_id: str, body: CompleteJob):     return _complete(job_id, body)
