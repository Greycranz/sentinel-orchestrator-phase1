from typing import Dict, Any

def analyze_budget(context: Dict[str, Any]) -> Dict[str, Any]:
    """Free-mode finance stub: never spends, only reports readiness and recommendations."""
    plan = {
        "mode": "free_only",
        "spend_allowed": False,
        "recommendations": [
            "Use only free tiers and open-source tools.",
            "Accumulate telemetry to estimate ROI before enabling paid features.",
            "Prepare vendor evaluation checklist for when Finance flips to paid mode."
        ],
    }
    return plan
