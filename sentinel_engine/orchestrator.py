import asyncio
import json
from typing import Dict, Any
from .db import init_db, next_queued_task, update_task_status, get_task, get_tenant
from .task_queue import wait_for_task_id
from .config import settings
from .agents.planner import make_plan
from .agents.builder import build_artifact
from .agents.reviewer import review_artifact
from .safety import check_policy
from .safety_policy import check_policy_for_tenant
from .secops import scan_security
from .redteam import simulate_attacks
from .upgrader import upgrader_tick
from .metrics import tasks_inflight, tasks_failed

_worker_task: asyncio.Task | None = None
_upgrader_task: asyncio.Task | None = None
_shutdown = asyncio.Event()

async def startup_event():
    init_db()
    global _worker_task, _upgrader_task
    _worker_task = asyncio.create_task(worker_loop())
    _upgrader_task = asyncio.create_task(upgrader_loop())

async def shutdown_event():
    _shutdown.set()
    tasks = []
    if _worker_task: tasks.append(_worker_task)
    if _upgrader_task: tasks.append(_upgrader_task)
    if tasks:
        await asyncio.wait(tasks)

async def upgrader_loop():
    while not _shutdown.is_set():
        try:
            _ = await upgrader_tick()
        except Exception as e:
            # log later
            pass
        await asyncio.sleep(60)  # check every minute in Phase 3 (fast for demo)

async def worker_loop():
    poll = settings.worker_poll_interval_seconds
    while not _shutdown.is_set():
        task = next_queued_task()
        if not task:
            await asyncio.sleep(poll)
            continue

        task_id = task["id"]
        tasks_inflight.inc()
        try:
            update_task_status(task_id, "in_progress")

            # Planner
            plan = make_plan(task)
            update_task_status(task_id, "planned", data_update={"plan": plan.model_dump()})

            # Builder
            artifact = build_artifact(task, plan.model_dump())
            update_task_status(task_id, "built", data_update={"artifact": artifact})

            # Tenant-specific safety policy if tenant set, otherwise global
            safety_mode = None
            if task.get("tenant_id"):
                tenant = get_tenant(task["tenant_id"])
                if tenant:
                    safety_mode = tenant.get("safety_mode")
            if safety_mode:
                allowed, notes = check_policy_for_tenant(artifact, safety_mode)
            else:
                allowed, notes = check_policy(artifact)

            if not allowed:
                update_task_status(task_id, "needs_revision", data_update={"safety": notes})
                tasks_failed.inc()
                await asyncio.sleep(poll)
                tasks_inflight.dec()
                continue
            else:
                update_task_status(task_id, "safety_ok", data_update={"safety": notes})

            # SecOps
            ok, sec_notes = scan_security(artifact)
            if not ok:
                update_task_status(task_id, "needs_revision", data_update={"secops": sec_notes})
                tasks_failed.inc()
                tasks_inflight.dec()
                await asyncio.sleep(poll)
                continue
            else:
                update_task_status(task_id, "secops_ok", data_update={"secops": sec_notes})

            # Red Team
            resilient, rt_notes = simulate_attacks(artifact)
            if not resilient:
                update_task_status(task_id, "needs_revision", data_update={"redteam": rt_notes})
                tasks_failed.inc()
                tasks_inflight.dec()
                await asyncio.sleep(poll)
                continue
            else:
                update_task_status(task_id, "redteam_ok", data_update={"redteam": rt_notes})

            # Reviewer
            review = review_artifact(artifact)
            update_task_status(task_id, "awaiting_approval", data_update={"review": review})

        except Exception as e:
            update_task_status(task_id, "error", data_update={"error": str(e)})
            tasks_failed.inc()
        finally:
            tasks_inflight.dec()

        await asyncio.sleep(poll)
