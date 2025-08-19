import os, time, json, uuid, logging, threading
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import requests

# -------- config --------
BASE_URL = os.getenv("SENTINEL_BASE_URL", "http://127.0.0.1:8001")
API_KEY  = os.getenv("SENTINEL_API_KEY")
if not API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("SENTINEL_API_KEY="):
                API_KEY = line.split("=",1)[1].strip()
                break
TENANT  = os.getenv("SENTINEL_TENANT", "default")
NAME    = os.getenv("SENTINEL_AGENT_NAME", "dev-agent-1")
VERSION = os.getenv("SENTINEL_AGENT_VERSION", "0.1.0")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# -------- logging --------
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)
fh = RotatingFileHandler(os.path.join(LOG_DIR, "agent_worker.log"), maxBytes=2_000_000, backupCount=5)
fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(fh)

def now_utc():
    return datetime.now(timezone.utc).isoformat()

# -------- job handlers --------
def handle_echo(job):
    payload = json.loads(job.get("payload_json") or "{}")
    msg = payload.get("msg", "")
    logger.info(f"[echo] {msg}")
    return {"ok": True, "echo": msg, "handled_at": now_utc()}

def handle_http(job):
    payload = json.loads(job.get("payload_json") or "{}")
    method  = str(payload.get("method", "GET")).upper()
    url     = payload.get("url")
    headers = payload.get("headers", {})
    data    = payload.get("data")
    if not url:
        return {"ok": False, "error": "missing url"}

    r = requests.request(method, url, headers=headers, json=data, timeout=30)
    body_sample = r.text[:1000] if isinstance(r.text, str) else None
    return {"ok": True, "status_code": r.status_code, "body_sample": body_sample, "handled_at": now_utc()}
HANDLERS = {
    "echo": handle_echo,
    "http": handle_http,
}

# -------- api helpers (v0) --------
def post(path, body):
    url = f"{BASE_URL}/v0{path}"
    r = requests.post(url, headers=HEADERS, data=json.dumps(body), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"POST {url} -> {r.status_code} {r.text}")
    return r.json() if r.text else {}

def get(path):
    url = f"{BASE_URL}/v0{path}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"GET {url} -> {r.status_code} {r.text}")
    return r.json() if r.text else {}

# -------- heartbeat thread --------
def heartbeat_loop(agent_id, interval):
    interval = max(int(interval or 30), 10)
    while True:
        try:
            post("/agents/heartbeat", {"agent_id": str(agent_id)})
        except Exception as e:
            logger.warning(f"heartbeat failed: {e}")
        time.sleep(interval)

def main():
    reg = post("/agents/register", {"name": NAME, "tenant": TENANT, "version": VERSION})
    agent_id = reg.get("agent_id") or reg.get("id") or str(uuid.uuid4())
    hb_int   = reg.get("heartbeat_interval", 30)
    logger.info(f"registered agent_id={agent_id} heartbeat_interval={hb_int}")

    t = threading.Thread(target=heartbeat_loop, args=(agent_id, hb_int), daemon=True)
    t.start()

    backoff = 1
    while True:
        try:
            job = get(f"/jobs/claim?agent_id={agent_id}")
            if not job or not job.get("id"):
                time.sleep(min(backoff, 10))
                backoff = min(backoff * 2, 10)
                continue

            backoff = 1
            jid  = job["id"]
            kind = job.get("kind", "echo")
            handler = HANDLERS.get(kind)
            logger.info(f"claimed job id={jid} kind={kind}")

            if not handler:
                out = {"ok": False, "error": f"no handler for kind {kind}"}
                post(f"/jobs/{jid}/complete", {"status": "failed", "output_json": json.dumps(out)})
                continue

            try:
                result = handler(job)
                post(f"/jobs/{jid}/complete", {"status": "completed", "output_json": json.dumps(result)})
                logger.info(f"completed job id={jid}")
            except Exception as ex:
                out = {"ok": False, "error": str(ex)}
                post(f"/jobs/{jid}/complete", {"status": "failed", "output_json": json.dumps(out)})

        except Exception as e:
            logger.warning(f"claim loop error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    logger.info("worker starting…")
    main()

