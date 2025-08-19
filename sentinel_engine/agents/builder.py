from typing import Dict, Any

def build_artifact(task: Dict[str, Any], plan_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Stubbed builder: creates a trivial 'artifact' string based on task title
    title = task.get("title", "Untitled")
    artifact = f"Artifact for '{title}' created. (Stub builder)"
    return {
        "artifact": artifact,
        "plan_used": plan_dict,
    }
