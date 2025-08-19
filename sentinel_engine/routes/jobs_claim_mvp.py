from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime, timezone

try:
    # local imports relative to your repo layout
    from sentinel_engine.db import SessionLocal
    from sentinel_engine.models_agent_mvp import Job
except Exception as e:
    # If imports fail, raise a clear error in logs
    raise

router = APIRouter(prefix="/v0", tags=["jobs"])

def _now_utc():
    return datetime.now(timezone.utc)

def _job_to_dict(j) -> Dict[str, Any]:
    # Be defensive in case your Job model shape differs
    return {
        "id": getattr(j, "id", None),
        "kind": getattr(j, "kind", None),
        "payload_json": getattr(j, "payload_json", None),
        "status": getattr(j, "status", None),
        "claimed_by_agent_id": getattr(j, "claimed_by_agent_id", None),
        "created_at": getattr(j, "created_at", None),
        "updated_at": getattr(j, "updated_at", None),
        "output_json": getattr(j, "output_json", None),
    }

@router.get("/jobs/claim")
def claim_job(agent_id: str = Query(..., description="UUID from /v0/agents/register")):
    # Oldest queued first
    with SessionLocal() as db:
        j = (
            db.query(Job)
            .filter(Job.status == "queued")
            .order_by(Job.id.asc())
            .first()
        )
        if not j:
            return None
        # Mark as claimed (set field only if it exists on your model)
        if hasattr(j, "claimed_by_agent_id"):
            setattr(j, "claimed_by_agent_id", agent_id)
        j.status = "in_progress"
        j.updated_at = _now_utc()
        db.add(j)
        db.commit()
        db.refresh(j)
        return _job_to_dict(j)

@router.post("/jobs/{job_id}/complete")
def complete_job(job_id: int, body: Dict[str, Any]):
    # Expected body: {"status":"completed","output_json":"{...}"}
    status = body.get("status", "completed")
    output_json = body.get("output_json")
    with SessionLocal() as db:
        j = db.query(Job).filter(Job.id == job_id).first()
        if not j:
            raise HTTPException(status_code=404, detail="job not found")
        j.status = status
        if output_json is not None:
            # Some schemas store a string; others a JSON column.
            # We just assign what we're given.
            setattr(j, "output_json", output_json)
        j.updated_at = _now_utc()
        db.add(j)
        db.commit()
        db.refresh(j)
        return {"ok": True, "job": _job_to_dict(j)}
