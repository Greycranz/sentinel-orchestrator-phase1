import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from sentinel_engine.db import SessionLocal
from sentinel_engine.models_agent_mvp import Job

router = APIRouter(prefix="/v0/jobs", tags=["jobs-admin"])

# ---- Pydantic models ----
class EnqueueRequest(BaseModel):
    kind: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class EnqueueResponse(BaseModel):
    id: int
    status: str

class JobOut(BaseModel):
    id: int
    kind: str
    status: str
    payload_json: Optional[str] = None
    updated_at: Optional[str] = None

class TotalsOut(BaseModel):
    queued: int
    in_progress: int
    completed: int
    failed: int

# ---- Endpoints ----
@router.post("/enqueue", response_model=EnqueueResponse)
def enqueue_job(req: EnqueueRequest):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        j = Job(
            kind=req.kind,
            payload_json=json.dumps(req.payload),
            status="queued",
            created_at=now,
            updated_at=now,
        )
        db.add(j)
        db.flush()
        jid = j.id
        db.commit()
    return {"id": jid, "status": "queued"}

@router.get("/recent", response_model=List[JobOut])
def recent_jobs(limit: int = Query(20, ge=1, le=200)):
    with SessionLocal() as db:
        rows = db.query(Job).order_by(Job.id.desc()).limit(limit).all()
        def iso(dt): return dt.isoformat() if dt else None
        return [
            JobOut(
                id=r.id, kind=r.kind, status=r.status,
                payload_json=r.payload_json, updated_at=iso(r.updated_at)
            ) for r in rows
        ]

@router.get("/get/{job_id}", response_model=JobOut)
def get_job(job_id: int):
    with SessionLocal() as db:
        j = db.get(Job, job_id)
        if not j:
            raise HTTPException(status_code=404, detail="Job not found")
        def iso(dt): return dt.isoformat() if dt else None
        return JobOut(
            id=j.id, kind=j.kind, status=j.status,
            payload_json=j.payload_json, updated_at=iso(j.updated_at)
        )

@router.get("/totals", response_model=TotalsOut)
def totals():
    with SessionLocal() as db:
        def c(s): return db.query(Job).filter(Job.status == s).count()
        return TotalsOut(
            queued=c("queued"),
            in_progress=c("in_progress"),
            completed=c("completed"),
            failed=c("failed"),
        )

@router.post("/retry/{job_id}")
def retry(job_id: int):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        j = db.get(Job, job_id)
        if not j:
            raise HTTPException(status_code=404, detail="Job not found")
        j.status = "queued"
        j.updated_at = now
        db.commit()
    return {"ok": True, "id": job_id, "status": "queued"}

@router.post("/unblock_stuck")
def unblock_stuck(age_seconds: int = 300):
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    with SessionLocal() as db:
        q = db.query(Job).filter(Job.status == "in_progress", Job.updated_at < cutoff)
        n = q.count()
        for j in q.all():
            j.status = "queued"
            j.updated_at = datetime.now(timezone.utc)
        db.commit()
    return {"ok": True, "requeued": n, "older_than_seconds": age_seconds}
