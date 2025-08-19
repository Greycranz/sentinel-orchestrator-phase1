from typing import Dict, Any
from importlib import import_module
from .models import Plan, Task

def _resolve_tool(entry: str):
    # entry like "real_app_builder:real_app_builder"
    mod, attr = entry.split(":")
    m = import_module(mod)
    return getattr(m, attr, None)

def run_task(plan: Plan, task: Task) -> Dict[str, Any]:
    from .registry import registry
    tool = registry.get_tool(task.tool)
    if not tool:
        task.status = "error"; task.error = f"unknown tool {task.tool}"; return {}
    fn = _resolve_tool(tool["entry"])
    if not fn:
        task.status = "error"; task.error = f"cannot resolve {tool['entry']}"; return {}
    # Call the tool (sync wrapper over async if needed)
    try:
        task.status = "running"
        # Expect the builder to expose a lightweight `.plan_only()` when available
        result = {"ok": True, "note": "stub call; wire real tool here", "inputs": task.inputs}
        task.status = "done"; task.result = result
        return result
    except Exception as e:
        task.status = "error"; task.error = str(e); return {}
