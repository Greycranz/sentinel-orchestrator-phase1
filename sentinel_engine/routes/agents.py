from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Any, Dict
from ..db import get_engine
from ..security import guard_api_key

router_v0 = APIRouter(prefix="/v0/agents", tags=["agents"])
router    = APIRouter(prefix="/agents",    tags=["agents"])

DDL = """
CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  host TEXT,
  tenant INTEGER DEFAULT 1,
  last_heartbeat TEXT,
  created_at TEXT NOT NULL
);
"""

def ensure_schema():
    eng = get_engine()
    with eng.begin() as cx:
        cx.exec_driver_sql(DDL)

ensure_schema()

def _uuid_sql(cx):
    return cx.exec_driver_sql(
        "SELECT lower(hex(randomblob(4)))||'-'||lower(hex(randomblob(2)))||'-'||lower(hex(randomblob(2)))||'-'||lower(hex(randomblob(2)))||'-'||lower(hex(randomblob(6)))"
    ).first()[0]

def _register_flex(payload: Dict[str, Any]):
    # accept many shapes: {name, host, tenant}, or alternative keys
    name   = str(payload.get("name") or payload.get("agent_name") or payload.get("id") or "agent").strip() or "agent"
    host   = payload.get("host") or payload.get("hostname") or payload.get("machine") or None
    tenant = payload.get("tenant") or payload.get("tenant_id") or 1
    try:
        tenant = int(tenant)
    except Exception:
        tenant = 1

    eng = get_engine()
    now = datetime.now(timezone.utc).isoformat()
    with eng.begin() as cx:
        agent_id = _uuid_sql(cx)
        cx.exec_driver_sql(
            "INSERT INTO agents(id,name,host,tenant,last_heartbeat,created_at) VALUES(?,?,?,?,?,?)",
            (agent_id, name, host, tenant, now, now)
        )
    return {"id": agent_id, "name": name, "tenant": tenant}

def _heartbeat_flex(payload: Dict[str, Any]):
    # accept id or agent_id, optional RFC3339 timestamp
    agent_id = payload.get("id") or payload.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=422, detail="missing agent id")
    at = payload.get("at")
    if not at:
        at = datetime.now(timezone.utc).isoformat()

    eng = get_engine()
    with eng.begin() as cx:
        upd = cx.exec_driver_sql(
            "UPDATE agents SET last_heartbeat=? WHERE id=?",
            (at, agent_id)
        )
        if upd.rowcount == 0:
            raise HTTPException(status_code=404, detail="agent_not_found")
    return {"ok": True, "id": agent_id, "at": at}

@router_v0.post("/register", dependencies=[Depends(guard_api_key)])
async def register_v0(req: Request):
    body = await req.json()
    return _register_flex(body if isinstance(body, dict) else {})

@router.post("/register", dependencies=[Depends(guard_api_key)])
async def register(req: Request):
    body = await req.json()
    return _register_flex(body if isinstance(body, dict) else {})

@router_v0.post("/heartbeat", dependencies=[Depends(guard_api_key)])
async def heartbeat_v0(req: Request):
    body = await req.json()
    return _heartbeat_flex(body if isinstance(body, dict) else {})

@router.post("/heartbeat", dependencies=[Depends(guard_api_key)])
async def heartbeat(req: Request):
    body = await req.json()
    return _heartbeat_flex(body if isinstance(body, dict) else {})
