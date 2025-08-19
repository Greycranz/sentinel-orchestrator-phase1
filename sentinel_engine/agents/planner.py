from typing import Dict, Any
from ..models import Plan, PlanStep

def make_plan(task: Dict[str, Any]) -> Plan:
    title = task.get("title", "Untitled Task")
    desc = task.get("description") or ""
    steps = [
        PlanStep(name="Analyze request", details=f"Understand goals for: {title}"),
        PlanStep(name="Design solution", details="Draft a minimal deliverable"),
        PlanStep(name="Produce artifact", details="Builder generates initial output"),
        PlanStep(name="Review & verify", details="Reviewer checks quality & safety"),
    ]
    return Plan(steps=steps)
