from .shared import ok
from ..models import Plan, GateDecision
def run(plan: Plan) -> GateDecision:
    return ok("perf", ["perf budget TBD; stub ok"])
