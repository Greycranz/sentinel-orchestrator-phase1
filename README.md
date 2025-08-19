# Sentinel Engine – Orchestrator (Phase 1)

Minimal, runnable orchestrator skeleton for your self-building AI company. 
It includes a Task Manager, simple department router, and three initial agents (Planner, Builder, Reviewer) with an approval gate.

## What’s here
- FastAPI service with endpoints to create tasks, list tasks, and approve tasks.
- Async worker loop that routes tasks through Planner → Builder → Reviewer → "awaiting_approval".
- SQLite persistence (no external DB required).
- Extensible agent pattern for future departments (Legal, Marketing, SecOps, Red Team, etc.).

## Quick Start (Windows PowerShell 7+)
```powershell
# 1) Create and activate a virtualenv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# 2) Install deps
pip install -r requirements.txt

# 3) Run API
uvicorn main:app --reload

# 4) Try creating a task (in another terminal or via browser)
# POST http://127.0.0.1:8000/tasks
# Body:
# {
#   "title": "Build Blender animation tool",
#   "description": "Create a basic tool stub",
#   "priority": 5,
#   "requester": "human"
# }
```

## Quick Start (Ubuntu / macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to use the Swagger UI.

## Project layout
```
sentinel-orchestrator-phase1/
├─ requirements.txt
├─ main.py
├─ README.md
└─ sentinel_engine/
   ├─ __init__.py
   ├─ config.py
   ├─ models.py
   ├─ db.py
   ├─ task_queue.py
   ├─ orchestrator.py
   └─ agents/
      ├─ __init__.py
      ├─ planner.py
      ├─ builder.py
      └─ reviewer.py
```

## Phase-1 Workflow
1. Create a task via API → Task saved as `queued`
2. Background worker picks it up → Planner drafts a plan
3. Builder produces an artifact (stub, for now)
4. Reviewer checks it (stub, for now)
5. Task becomes `awaiting_approval`
6. Approve via API → status becomes `approved` (Phase-2 will deploy)

## Next phases
- Add Safety Layer (filtering pipeline) before approval.
- Add SecOps + Red Team agents (pre-deploy checks).
- Add Legal/Marketing/Finance departments as separate agents.
- Add Integrator Agent for deployment & rollback.
- Add Upgrader/Adapter Generator/Capability Scanner hooks.
```