from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

Stage = Literal["plan","gates","evaluate","promote","done","failed"]

class Intent(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["low","medium","high","urgent"] = "medium"

class Task(BaseModel):
    id: str
    name: str
    tool: str
    inputs: Dict[str, Any] = {}
    expected: str = ""
    status: Literal["queued","running","done","error"] = "queued"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class Plan(BaseModel):
    id: str
    intent: Intent
    tasks: List[Task] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    stage: Stage = "plan"
    evidence: Dict[str, Any] = {}

class GateDecision(BaseModel):
    gate: str
    status: Literal["pass","hold","fail"]
    reasons: List[str] = []
    evidence: Dict[str, Any] = {}
    owner: str = "auto"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PromotionResult(BaseModel):
    plan_id: str
    promoted: bool
    reason: str = ""
    rollback_token: Optional[str] = None
