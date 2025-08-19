from ..models import GateDecision
def ok(name, reasons=None):  return GateDecision(gate=name, status="pass", reasons=reasons or [])
def hold(name, reasons=None):return GateDecision(gate=name, status="hold", reasons=reasons or [])
def fail(name, reasons=None):return GateDecision(gate=name, status="fail", reasons=reasons or [])
