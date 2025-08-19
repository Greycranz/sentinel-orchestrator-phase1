import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
OPS_DIR = ROOT / "ops"
FLAGS_DIR = OPS_DIR / "flags"
LOGS_DIR = OPS_DIR / "logs" / "patches"
FLAGS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def api_key() -> str | None:
    return os.getenv("SENTINEL_API_KEY")

def rollback_flag_path() -> Path:
    return FLAGS_DIR / "rollback.on"

def is_rollback_enabled() -> bool:
    return rollback_flag_path().exists()

def set_rollback(enabled: bool) -> None:
    p = rollback_flag_path()
    if enabled:
        p.write_text("on")
    else:
        if p.exists():
            p.unlink()

def audit_log(msg: str) -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    path = LOGS_DIR / f"patch-audit-{datetime.utcnow().strftime('%Y%m%d')}.log"
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# ---- settings shim (env-first, minimal) ----
try:
    from pydantic import BaseModel
except Exception:  # fallback if pydantic missing
    class BaseModel:  # type: ignore
        pass

class Settings(BaseModel):
    database_url: str | None = os.getenv("DATABASE_URL")
    sentinel_api_key: str | None = os.getenv("SENTINEL_API_KEY")
    env: str = os.getenv("ENV", "dev")
    debug: bool = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes", "on")

settings = Settings()
# --------------------------------------------

from typing import Optional

def build_version() -> str:
    try:
        with (OPS_DIR / "version.txt").open("r", encoding="utf-8") as f:
            return f.read().strip() or "dev"
    except Exception:
        return "dev"

def database_url_fallback() -> Optional[str]:
    url = os.getenv("DATABASE_URL")
    if url and url.strip():
        return url.strip()
    # Fallback to repo-local SQLite (ops/data/dev.db)
    root = ROOT.as_posix()
    return f"sqlite:///{root}/ops/data/dev.db"

