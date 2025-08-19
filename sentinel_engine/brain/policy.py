from typing import Dict, Any, List
from .models import Plan, GateDecision

class PolicyEngine:
    def __init__(self):
        # Simple rule placeholders; upgrade to external policy files later
        self.rules = {
            "safety": ["no PII exfiltration","rate limits in place","no illegal content"],
            "legal":  ["license OK","export OK","privacy OK"],
            "business":["has target user","ROI plausible"],
            "perf":   ["no hot path regressions >10%"]
        }

    def evaluate(self, plan: Plan) -> List[GateDecision]:
        # Stub gate aggregator (each gate will validate deeper)
        return []

policy = PolicyEngine()
