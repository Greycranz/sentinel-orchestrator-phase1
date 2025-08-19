import base64
import bcrypt
import time
from typing import Optional, Tuple
from fastapi import Request, HTTPException

# --- Basic Auth (for /ui/approvals) ---
# Hash a password once (use tool/CLI); store salt+hash. For the demo we accept env vars or fallback.
_UI_USER = "admin"
_UI_PASS_BCRYPT = None  # set at startup via set_ui_password()

def set_ui_password(plain: str):
    global _UI_PASS_BCRYPT
    _UI_PASS_BCRYPT = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())

def verify_basic_auth(request: Request) -> None:
    if _UI_PASS_BCRYPT is None:
        # No password set => disable auth (dev only)
        return
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    try:
        decoded = base64.b64decode(header.split(" ",1)[1]).decode("utf-8")
        user, pw = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    if user != _UI_USER or not bcrypt.checkpw(pw.encode("utf-8"), _UI_PASS_BCRYPT):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

# --- API key auth + rate limiting (very simple, in-memory) ---
_rate_buckets = {}  # api_key -> (tokens, last_refill_ts)
RATE_LIMIT_TOKENS = 60  # tokens per minute
REFILL_SECONDS = 60

def _consume_token(api_key: str) -> bool:
    now = time.time()
    tokens, last_ts = _rate_buckets.get(api_key, (RATE_LIMIT_TOKENS, now))
    # refill
    if now - last_ts >= REFILL_SECONDS:
        tokens = RATE_LIMIT_TOKENS
        last_ts = now
    # consume
    if tokens <= 0:
        _rate_buckets[api_key] = (tokens, last_ts)
        return False
    tokens -= 1
    _rate_buckets[api_key] = (tokens, last_ts)
    return True
