from .shared import ok, hold
from ..models import Plan, GateDecision

def run(plan: Plan) -> GateDecision:
    # TODO: plug real static checks, content filters, budgets, kill-switch signals
    reasons = ["stub safety ok"]
    return ok("safety", reasons)
