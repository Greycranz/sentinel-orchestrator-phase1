from typing import Dict, Any, Tuple, List

DEFAULT_POLICIES = {
    "strict": {"forbidden_terms": ["csam", "child sexual", "assassinate", "build a bomb", "fentanyl synthesis"], "warnings": ["extreme gore", "sexual content", "nudity"]},
    "standard": {"forbidden_terms": ["csam", "child sexual"], "warnings": ["graphic violence", "sexual content"]},
    "relaxed": {"forbidden_terms": ["csam", "child sexual"], "warnings": []},
}

def check_policy_for_tenant(artifact_bundle: Dict[str, Any], safety_mode: str) -> Tuple[bool, List[str]]:
    policy = DEFAULT_POLICIES.get(safety_mode, DEFAULT_POLICIES["strict"])
    text = _flatten(artifact_bundle).lower()
    reasons: List[str] = []
    for term in policy["forbidden_terms"]:
        if term in text:
            reasons.append(f"Forbidden content detected: '{term}'")
    allowed = len(reasons) == 0
    reasons.extend([f"Warning: '{w}' present" for w in policy["warnings"] if w in text])
    return allowed, reasons

def _flatten(obj: Any) -> str:
    try:
        import json
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)
