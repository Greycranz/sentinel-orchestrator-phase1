import os
import sys
import platform
from datetime import datetime, timezone
from fastapi import APIRouter

router_version = APIRouter()

def _read_git_commit(repo_root: str) -> str:
    try:
        head = os.path.join(repo_root, ".git", "HEAD")
        if not os.path.exists(head):
            return ""
        with open(head, "r", encoding="utf-8") as f:
            line = f.read().strip()
        if line.startswith("ref: "):
            ref_rel = line.split(" ", 1)[1]
            ref_abs = os.path.join(repo_root, ".git", *ref_rel.split("/"))
            if os.path.exists(ref_abs):
                with open(ref_abs, "r", encoding="utf-8") as rf:
                    return rf.read().strip()
        # detached HEAD
        return line[:40]
    except Exception:
        return ""

def _coalesce_commit(repo_root: str) -> str:
    env = os.getenv("SENTINEL_COMMIT", "") or os.getenv("GIT_COMMIT", "")
    git = _read_git_commit(repo_root)
    return (git or env or "unknown")[:40]

@router_version.get("/version", summary="Service version info")
def get_version():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    info = {
        "name": os.getenv("SENTINEL_NAME", "sentinel-orchestrator"),
        "env": os.getenv("SENTINEL_ENV", "dev"),
        "commit": _coalesce_commit(repo_root),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "fastapi": __import__("fastapi").__version__,
        "uvicorn": __import__("uvicorn").__version__,
    }
    return info
