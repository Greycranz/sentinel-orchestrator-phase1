from sqlalchemy import text
from .db import engine, now_iso

def init_extra_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS tenant_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """))

def seed_default_teams():
    defaults = [
        ("Safety", "Content safety policy & governance"),
        ("SecOps", "Security scanning & hardening"),
        ("RedTeam", "Adversarial testing & fuzzing"),
        ("Planner", "Technical planning / RFCs"),
        ("Builder", "Code and asset generation"),
        ("Reviewer", "Quality control"),
        ("Integrator", "Packaging, deploy, rollback"),
        ("Upgrader", "Keeps tools up-to-date"),
        ("Marketing", "Positioning, copy, launch plan"),
        ("Legal", "Copyright & compliance review"),
        ("Business", "Business model & pricing"),
        ("Finance", "Budgets, taxes, filings (future paid)"),
        ("SpeedOps", "Performance & latency SLOs"),
        ("Support", "Docs, help, customer success")
    ]
    with engine.begin() as conn:
        existing = set([r[0] for r in conn.execute(text("SELECT name FROM teams")).all()])
        for name, desc in defaults:
            if name not in existing:
                conn.execute(text(
                    "INSERT INTO teams (name, description, created_at) VALUES (:n, :d, :ts)"
                ), {"n": name, "d": desc, "ts": now_iso()})
