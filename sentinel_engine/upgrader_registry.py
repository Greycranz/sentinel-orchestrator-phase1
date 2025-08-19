import json, os
from .adapter_generator import generate_adapters

def registry_path():
    return os.path.join(os.path.dirname(__file__), "tool_registry.json")

def propose_from_registry():
    try:
        with open(registry_path(), "r", encoding="utf-8") as f:
            reg = json.load(f)
    except Exception:
        return {"ran": False, "reason": "no registry"}
    if not reg.get("tools"):
        return {"ran": False, "reason": "no tools"}
    todo = [t["name"] for t in reg["tools"] if t.get("status") in ("candidate", "beta")]
    gen = generate_adapters(todo)
    return {"ran": True, "generated": gen}
