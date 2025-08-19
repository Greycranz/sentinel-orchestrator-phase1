from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from sentinel_engine.security import guard_api_key
from sentinel_engine.llm import aggregate_stub

router = APIRouter()

class AggregateRequest(BaseModel):
    prompt: str
    providers: Optional[List[str]] = None
    temperature: Optional[float] = 0.7

@router.post("/aggregate")
def aggregate(req: AggregateRequest, _=Depends(guard_api_key)):
    return aggregate_stub(req.prompt, req.providers or [])
