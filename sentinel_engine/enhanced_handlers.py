"""Enhanced Job Handlers for Sentinel Engine Phase 2"""
import os
import json
import asyncio
import logging
import time
from typing import Dict, Any, Optional

from .llm_orchestrator import orchestrator, TaskType

logger = logging.getLogger(__name__)

class JobHandler:
    async def execute(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return await self._execute_impl(job_data)
        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            return {"success": False, "error": str(e), "output": ""}
    
    async def _execute_impl(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class EchoHandler(JobHandler):
    async def _execute_impl(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        message = job_data.get("message", "Hello from Sentinel!")
        return {
            "success": True,
            "output": f"Echo: {message}",
            "timestamp": time.time()
        }

class LLMHandler(JobHandler):
    async def _execute_impl(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = job_data.get("prompt", "")
        task_type_str = job_data.get("task_type", "general")
        
        if not prompt:
            return {"success": False, "error": "No prompt provided"}
        
        try:
            task_type = TaskType(task_type_str.lower())
        except ValueError:
            task_type = TaskType.GENERAL
        
        result = await orchestrator.orchestrate_consensus(prompt=prompt, task_type=task_type)
        
        return {
            "success": True,
            "output": result["result"],
            "consensus": result["consensus"],
            "providers_used": result["providers_used"],
            "cost": result["total_cost"]
        }

# Job handler registry
JOB_HANDLERS = {
    "echo": EchoHandler(),
    "llm": LLMHandler(),
}

async def execute_job(job_type: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    handler = JOB_HANDLERS.get(job_type)
    if not handler:
        return {
            "success": False,
            "error": f"Unknown job type: {job_type}",
            "available_types": list(JOB_HANDLERS.keys())
        }
    return await handler.execute(job_data)
