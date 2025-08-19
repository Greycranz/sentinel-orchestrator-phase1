from typing import List
from .models import Plan, GateDecision, PromotionResult
from . import planner
from .executor import run_task
from .gates import safety, legal, business, perf

def plan_from_intent(title:str, description:str, priority:str="medium") -> Plan:
    return planner.make_plan(title, description, priority)

def run_tasks(plan: Plan) -> Plan:
    for t in plan.tasks:
        if t.status in ("done","running"): continue
        run_task(plan, t)
    plan.stage = "gates"
    return plan

def run_gates(plan: Plan) -> List[GateDecision]:
    decisions = [safety.run(plan), legal.run(plan), business.run(plan), perf.run(plan)]
    return decisions

def evaluate_and_promote(plan: Plan, decisions: List[GateDecision]) -> PromotionResult:
    if any(d.status == "fail" for d in decisions):
        plan.stage = "failed"
        return PromotionResult(plan_id=plan.id, promoted=False, reason="one or more gates failed")

    if any(d.status == "hold" for d in decisions):
        plan.stage = "evaluate"
        return PromotionResult(plan_id=plan.id, promoted=False, reason="one or more gates hold")

    plan.stage = "promote"
    # TODO: real staging→approval→deploy; create rollback token
    return PromotionResult(plan_id=plan.id, promoted=True, reason="all gates passed", rollback_token=plan.id + "-rb")
