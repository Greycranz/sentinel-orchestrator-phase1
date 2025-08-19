from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..db import SessionLocal, engine, Base
from ..models_agent_mvp import Agent, Job, Result

# Ensure tables exist (idempotent)
Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["agents", "jobs"])

# --- Pydantic I/O models ---
class AgentRegisterIn(BaseModel):
    name: str

class AgentRegisterOut(BaseModel):
    id: int
    name: str
    status: str

class AgentHeartbeatIn(BaseModel):
    id: int

class JobOut(BaseModel):
    id: int
    kind: str
    payload_json: Optional[str] = None

class JobCompleteIn(BaseModel):
    status: str  # "completed" | "failed"
    output_json: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---

@router.post("/agents/register", response_model=AgentRegisterOut)
def register_agent(payload: AgentRegisterIn, request: Request, db: Session = Depends(get_db)):
    # Deterministic: one row per name
    existing = db.execute(select(Agent).where(Agent.name == payload.name)).scalar_one_or_none()
    if existing:
        # Update status to known "idle" on (re)register
        existing.status = "idle"
        db.commit()
        db.refresh(existing)
        return AgentRegisterOut(id=existing.id, name=existing.name, status=existing.status)

    a = Agent(name=payload.name, status="idle", last_seen=datetime.utcnow())
    db.add(a)
    db.commit()
    db.refresh(a)
    return AgentRegisterOut(id=a.id, name=a.name, status=a.status)

@router.post("/agents/heartbeat")
def agent_heartbeat(payload: AgentHeartbeatIn, request: Request, db: Session = Depends(get_db)):
    a = db.get(Agent, payload.id)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")
    a.last_seen = datetime.utcnow()
    if a.status == "unknown":
        a.status = "idle"
    db.commit()
    return {"ok": True}

@router.get("/jobs/claim", response_model=Optional[JobOut])
def claim_job(request: Request, agent_id: int, db: Session = Depends(get_db)):
    # Atomic-ish claim for SQLite:
    # 1) find oldest queued job id
    job_id = db.execute(
        select(Job.id).where(Job.status == "queued").order_by(Job.created_at.asc()).limit(1)
    ).scalar_one_or_none()
    if not job_id:
        return None  # no jobs to claim

    # 2) attempt to transition queued -> in_progress (only if still queued)
    res = db.execute(
        update(Job)
        .where(Job.id == job_id, Job.status == "queued")
        .values(status="in_progress", agent_id=agent_id, updated_at=datetime.utcnow())
    )
    if res.rowcount != 1:
        db.rollback()
        return None

    db.commit()
    job = db.get(Job, job_id)
    if not job:
        return None
    return JobOut(id=job.id, kind=job.kind, payload_json=job.payload_json)

@router.post("/jobs/{job_id}/complete")
def complete_job(job_id: int, payload: JobCompleteIn, request: Request, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")

    if payload.status not in ("completed", "failed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid status")

    job.status = payload.status
    job.updated_at = datetime.utcnow()
    db.add(job)

    # Upsert a result row (deterministic)
    existing = db.execute(select(Result).where(Result.job_id == job_id)).scalar_one_or_none()
    if existing:
        existing.status = payload.status
        existing.output_json = payload.output_json
    else:
        db.add(Result(job_id=job_id, status=payload.status, output_json=payload.output_json))

    db.commit()
    return {"ok": True}


