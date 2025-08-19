from datetime import datetime
import os
from pathlib import Path
BOOT_TIME = datetime.utcnow().isoformat() + "Z"
NAME = os.getenv("SENTINEL_NAME", "sentinel-orchestrator")
ENV  = os.getenv("SENTINEL_ENV",  "dev")
_commit = os.getenv("SENTINEL_COMMIT")
if not _commit:
    try:
        root = Path(__file__).resolve().parents[1]
        head = (root / ".git" / "HEAD").read_text().strip()
        if head.startswith("ref:"):
            ref_path = root / ".git" / head.split(" ", 1)[1]
            _commit = ref_path.read_text().strip()
        else:
            _commit = head
    except Exception:
        _commit = "unknown"
COMMIT = _commit
