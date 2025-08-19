import uuid
from typing import List
from .models import Intent, Plan, Task
from .registry import registry

def make_plan(title:str, description:str, priority:str="medium") -> Plan:
    intent = Intent(id=str(uuid.uuid4()), title=title, description=description, priority=priority)
    tasks: List[Task] = []

    # Minimal heuristic: when intent smells like "build app", schedule the app_builder
    if any(k in (title+description).lower() for k in ["build","app","unreal","hollywood","web","api"]):
        tasks.append(Task(
            id=str(uuid.uuid4()), name="Generate application scaffold",
            tool="app_builder", inputs={"idea": description}, expected="Working scaffold + endpoints"
        ))

    return Plan(id=str(uuid.uuid4()), intent=intent, tasks=tasks)
