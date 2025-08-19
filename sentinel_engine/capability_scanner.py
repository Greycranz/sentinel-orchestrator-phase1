from typing import Dict, Any, List

REQUIRED_CAPABILITIES = ["linting", "unit_tests", "perf_checks", "sec_scans", "legal_checks", "marketing_plan"]

def scan_capabilities(current: List[str]) -> Dict[str, Any]:
    missing = [c for c in REQUIRED_CAPABILITIES if c not in current]
    return {"missing": missing, "have": current}
