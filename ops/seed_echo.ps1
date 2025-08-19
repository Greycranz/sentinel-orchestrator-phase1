param([string]$Msg = "hi")

$RepoRoot = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1"
$PyExe    = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Tmp      = Join-Path $RepoRoot "ops\tmp_seed_echo.py"

# Write a tiny Python file. Read the message from an env var to avoid quoting issues.
$py = @"
import os, sys, json
from datetime import datetime, timezone
repo = r'$RepoRoot'
os.chdir(repo)
if repo not in sys.path: sys.path.insert(0, repo)
from sentinel_engine.db import SessionLocal
from sentinel_engine.models_agent_mvp import Job

msg = os.environ.get("SEED_MSG", "")
with SessionLocal() as db:
    j = Job(kind='echo',
            payload_json=json.dumps({"msg": msg}),
            status='queued',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc))
    db.add(j)
    db.flush()        # get id before commit
    jid = j.id
    db.commit()
print(jid)
"@

Set-Content -Encoding UTF8 -Path $Tmp -Value $py
$env:SEED_MSG = $Msg
& "$PyExe" $Tmp
Remove-Item $Tmp -Force
Remove-Item Env:\SEED_MSG
