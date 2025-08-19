from .shared import ok, hold
from ..models import Plan, GateDecision
def run(plan: Plan) -> GateDecision:
    # Gate can HOLD if no user/ROI stub present in intent description
    if len(plan.intent.description or "") < 10:
        return hold("business", ["insufficient business rationale"])
    return ok("business", ["stub business ok"])
