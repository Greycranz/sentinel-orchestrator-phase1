from typing import Dict, Any
from datetime import datetime

def deploy(task_id: int, artifact_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate deployment and return a deploy log."""
    return {
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "deployed",
        "log": "Deployed artifact to staging → production (simulated). Rollback hook ready."
    }

def rollback(task_id: int, reason: str) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "rolled_back",
        "reason": reason
    }
