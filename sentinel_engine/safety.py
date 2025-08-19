from typing import Dict, Any, Tuple, List

# Very simple Tier-1 rules: block obviously illegal/forbidden terms.
FORBIDDEN = [
    "csam", "child sexual", "make a bomb", "credit card dump", "ransomware",
    "exploit zero-day", "assassinate", "build a gun", "fentanyl synthesis",
]

WARNINGS = [
    "extreme gore", "sexual content", "nudity", "graphic violence"
]

def check_policy(artifact_bundle: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Return (allowed, notes). If not allowed -> False with reasons."""
    text = json_safe_flatten(artifact_bundle)
    reasons = []
    lowered = text.lower()
    for bad in FORBIDDEN:
        if bad in lowered:
            reasons.append(f"Forbidden content detected: '{bad}'")
    allowed = len(reasons) == 0
    # Add warnings (informational only)
    warnings = [f"Warning: '{w}' present" for w in WARNINGS if w in lowered]
    reasons.extend(warnings)
    return allowed, reasons

def json_safe_flatten(obj: Any) -> str:
    try:
        import json
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)
