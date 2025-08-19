import os, threading
from pathlib import Path
from secrets import token_urlsafe

_ENV_PATH = Path(os.getenv("SENTINEL_ENV_PATH", ".env"))
_lock = threading.Lock()
_cache = {"key": None, "mtime": 0.0}

def _read_key_from_file() -> str:
    if not _ENV_PATH.exists():
        return ""
    try:
        lines = _ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return ""
    for line in lines:
        if line.startswith("SENTINEL_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    return ""

def get_key() -> str:
    try:
        mtime = _ENV_PATH.stat().st_mtime
    except FileNotFoundError:
        mtime = 0.0
    with _lock:
        if mtime != _cache["mtime"]:
            _cache["key"] = _read_key_from_file()
            _cache["mtime"] = mtime
        return _cache["key"] or ""

def rotate_key() -> str:
    new = token_urlsafe(32)
    lines = []
    if _ENV_PATH.exists():
        try:
            lines = _ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            lines = []
    found = False
    for i, l in enumerate(lines):
        if l.startswith("SENTINEL_API_KEY="):
            lines[i] = f"SENTINEL_API_KEY={new}"
            found = True
            break
    if not found:
        lines.append(f"SENTINEL_API_KEY={new}")
    _ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with _lock:
        _cache["key"] = new
        try:
            _cache["mtime"] = _ENV_PATH.stat().st_mtime
        except Exception:
            pass
    return new
