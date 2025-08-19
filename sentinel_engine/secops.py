from typing import Dict, Any, Tuple, List

def scan_security(artifact_bundle: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Stub security scan. Returns (ok, notes)."""
    notes = []
    # Example: disallow secrets-in-text patterns
    text = str(artifact_bundle)
    if "API_KEY=" in text or "BEGIN PRIVATE KEY" in text:
        notes.append("Potential secret detected in artifact.")
        return False, notes
    notes.append("Security scan clean (stub).")
    return True, notes
