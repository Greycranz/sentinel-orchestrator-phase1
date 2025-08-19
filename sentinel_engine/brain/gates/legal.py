from .shared import ok
from ..models import Plan, GateDecision
def run(plan: Plan) -> GateDecision:
    reasons = ["stub legal ok (licenses TBD)"]
    return ok("legal", reasons)
