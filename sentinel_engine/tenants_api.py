from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from .db import get_engine

router_tenants = APIRouter(prefix="/tenants", tags=["tenants"])

# Ensure schema
engine = get_engine()
with engine.begin() as conn:
    conn.exec_driver_sql("""
    CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.exec_driver_sql("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL REFERENCES tenants(id),
        name TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 0,
        UNIQUE(tenant_id, name)
    )
    """)

class TenantIn(BaseModel):
    name: str

@router_tenants.post("", summary="Create a new tenant")
def create_tenant(tenant: TenantIn):
    with engine.begin() as conn:
        res = conn.execute(
            text("INSERT INTO tenants (name, created_at) VALUES (:name, :ts)"),
            {"name": tenant.name, "ts": datetime.utcnow().isoformat()}
        )
        tid = res.lastrowid
    return {"id": tid, "name": tenant.name}

@router_tenants.get("", summary="List all tenants")
def list_tenants():
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, name, created_at FROM tenants ORDER BY id")).mappings().all()
    return list(rows)

@router_tenants.get("/{tenant_id}", summary="Get tenant by ID")
def get_tenant(tenant_id: int):
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT id, name, created_at FROM tenants WHERE id = :id"),
            {"id": tenant_id}
        ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return dict(row)
