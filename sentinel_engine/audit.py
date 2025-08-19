import json, os, datetime

def _audit_path():
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ops", "logs")
    os.makedirs(base, exist_ok=True)
    day = datetime.datetime.utcnow().strftime("%Y%m%d")
    return os.path.join(base, f"audit-{day}.jsonl")

def write_audit(event: str, status: int, path: str, method: str, client: str = "", detail: dict | None = None):
    rec = {
        "ts": datetime.datetime.utcnow().isoformat()+"Z",
        "event": event,
        "status": status,
        "path": path,
        "method": method,
        "client": client,
    }
    if detail: rec["detail"] = detail
    p = _audit_path()
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
