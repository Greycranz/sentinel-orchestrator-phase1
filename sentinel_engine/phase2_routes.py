"""Phase 2 API endpoints for Sentinel Engine"""
import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from .llm_orchestrator import orchestrator, TaskType
from .enhanced_handlers import execute_job

# Request/Response models
class LLMRequest(BaseModel):
    prompt: str
    task_type: Optional[str] = "general"

class JobRequest(BaseModel):
    job_type: str
    data: Dict[str, Any]

# Router for Phase 2
phase2_router = APIRouter(prefix="/v1", tags=["Phase 2"])

@phase2_router.post("/llm/orchestrate")
async def orchestrate_llm(request: LLMRequest):
    """Orchestrate LLM request"""
    try:
        task_type = TaskType.GENERAL
        if request.task_type:
            try:
                task_type = TaskType(request.task_type.lower())
            except ValueError:
                task_type = TaskType.GENERAL
        
        result = await orchestrator.orchestrate_consensus(
            prompt=request.prompt,
            task_type=task_type
        )
        
        return {
            "success": True,
            "result": result["result"],
            "consensus": result["consensus"],
            "providers_used": result["providers_used"],
            "cost": result["total_cost"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@phase2_router.get("/llm/cost-summary")
async def get_cost_summary():
    """Get LLM cost summary"""
    return orchestrator.get_cost_summary()

@phase2_router.post("/jobs/enhanced")
async def execute_enhanced_job(request: JobRequest):
    """Execute enhanced job"""
    try:
        result = await execute_job(request.job_type, request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@phase2_router.get("/jobs/handlers")
async def list_job_handlers():
    """List available job handlers"""
    from .enhanced_handlers import JOB_HANDLERS
    return {
        "available_handlers": list(JOB_HANDLERS.keys()),
        "phase2_status": "active"
    }
