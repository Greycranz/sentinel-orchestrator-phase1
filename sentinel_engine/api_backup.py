"""
Sentinel Engine Phase 2 - Complete FastAPI Application
Revenue-ready multi-LLM orchestration platform
"""
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import local modules
from .models import create_tables, get_db, Agent, Job, LLMUsage
from .multi_llm_orchestrator import multi_llm
from .enhanced_job_handlers import enhanced_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Sentinel Engine Phase 2...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down Sentinel Engine Phase 2...")

# Create FastAPI app
app = FastAPI(
    title="Sentinel Engine Phase 2",
    description="Multi-LLM Revenue Engine for $1M ARR",
    version="2.0.0",
    lifespan=lifespan
)

# Global metrics
metrics = {
    'requests_total': 0,
    'requests_success': 0,
    'requests_failed': 0,
    'jobs_processed': 0,
    'agents_registered': 0,
    'uptime_start': datetime.utcnow()
}

def get_api_key() -> str:
    """Get API key from environment"""
    return os.getenv('SENTINEL_API_KEY', 'ytOTqqiZ9jvpW3yPruv4ryM297uszGC1V6+/mpt7Odo=')

def verify_api_key(x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    """Verify API key from header"""
    global metrics
    
    # Extract key from headers
    api_key = None
    if x_api_key:
        api_key = x_api_key
    elif authorization and authorization.startswith('Bearer '):
        api_key = authorization[7:]
    
    if not api_key:
        metrics['requests_failed'] += 1
        raise HTTPException(status_code=401, detail="API key required (X-API-Key header or Authorization: Bearer)")
    
    stored_key = get_api_key()
    if api_key != stored_key:
        metrics['requests_failed'] += 1
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    metrics['requests_success'] += 1
    return api_key

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Update request metrics"""
    global metrics
    metrics['requests_total'] += 1
    
    response = await call_next(request)
    return response

# HEALTH AND STATUS ENDPOINTS (NO AUTH)
@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Sentinel Engine Phase 2",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/healthz/ready")
async def ready():
    """Readiness check with database"""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        
        return {
            "ready": True,
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.get("/version", dependencies=[Depends(verify_api_key)])
async def version():
    """Service version information"""
    return {
        "name": "sentinel-engine-phase2",
        "version": "2.0.0",
        "phase": "Phase 2 - Multi-LLM Revenue Engine",
        "environment": os.getenv("SENTINEL_ENV", "dev"),
        "started_at": metrics['uptime_start'].isoformat(),
        "capabilities": [
            "multi-llm-orchestration",
            "enhanced-job-processing", 
            "git-operations",
            "file-operations",
            "web-requests",
            "shell-execution",
            "cost-optimization"
        ]
    }

@app.get("/metrics", dependencies=[Depends(verify_api_key)])
async def get_metrics():
    """Service metrics"""
    uptime_seconds = (datetime.utcnow() - metrics['uptime_start']).total_seconds()
    
    return {
        "uptime_seconds": round(uptime_seconds, 2),
        "requests_total": metrics['requests_total'],
        "requests_success": metrics['requests_success'],
        "requests_failed": metrics['requests_failed'],
        "success_rate": round((metrics['requests_success'] / max(metrics['requests_total'], 1)) * 100, 2),
        "jobs_processed": metrics['jobs_processed'],
        "agents_registered": metrics['agents_registered'],
        "llm_usage": multi_llm.get_usage_summary()
    }

# AGENT MANAGEMENT ENDPOINTS
@app.post("/v0/agents/register", dependencies=[Depends(verify_api_key)])
async def register_agent(agent_data: Dict[str, Any]):
    """Register new agent"""
    try:
        db = next(get_db())
        
        agent = Agent(
            name=agent_data.get('name', f'agent-{datetime.utcnow().timestamp()}'),
            capabilities=str(agent_data.get('capabilities', [])),
            status='active'
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        db.close()
        
        metrics['agents_registered'] += 1
        
        return {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status,
            "registered_at": agent.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v0/agents/heartbeat", dependencies=[Depends(verify_api_key)])
async def agent_heartbeat(heartbeat_data: Dict[str, Any]):
    """Agent heartbeat"""
    try:
        agent_id = heartbeat_data.get('id')
        if not agent_id:
            raise HTTPException(status_code=400, detail="Agent ID required")
        
        db = next(get_db())
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        
        if not agent:
            db.close()
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent.last_heartbeat = datetime.utcnow()
        agent.status = 'active'
        db.commit()
        db.close()
        
        return {
            "agent_id": agent_id,
            "status": "acknowledged",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Heartbeat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# JOB PROCESSING ENDPOINTS
@app.post("/v0/jobs/enqueue", dependencies=[Depends(verify_api_key)])
async def enqueue_job(job_data: Dict[str, Any]):
    """Enqueue new job"""
    try:
        db = next(get_db())
        
        job = Job(
            type=job_data.get('type'),
            payload=str(job_data.get('payload', {})),
            status='queued'
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        db.close()
        
        return {
            "job_id": job.id,
            "type": job.type,
            "status": job.status,
            "created_at": job.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Job enqueue error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v0/jobs/enhanced", dependencies=[Depends(verify_api_key)])
async def process_enhanced_job(job_data: Dict[str, Any]):
    """Process enhanced job immediately"""
    try:
        job_type = job_data.get('type')
        payload = job_data.get('payload', {})
        
        if not job_type:
            raise HTTPException(status_code=400, detail="Job type required")
        
        # Process job with enhanced handlers
        result = await enhanced_handlers.handle_job(job_type, payload)
        
        # Update metrics
        metrics['jobs_processed'] += 1
        
        return {
            "status": "completed" if result['success'] else "failed",
            "job_type": job_type,
            "result": result,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Enhanced job processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v0/jobs/types", dependencies=[Depends(verify_api_key)])
async def get_job_types():
    """Get available job types"""
    return {
        "enhanced_types": list(enhanced_handlers.handlers.keys()),
        "total_types": len(enhanced_handlers.handlers),
        "categories": {
            "llm": ["llm_request"],
            "git": ["git_clone", "git_status"],
            "file": ["file_read", "file_write", "file_list"],
            "system": ["shell_exec", "test_endpoint"],
            "web": ["web_request"],
            "build": ["build_project"],
            "utility": ["echo"]
        }
    }

# MULTI-LLM ENDPOINTS
@app.post("/v1/llm/orchestrate", dependencies=[Depends(verify_api_key)])
async def orchestrate_llm(request_data: Dict[str, Any]):
    """Orchestrate LLM request across providers"""
    try:
        prompt = request_data.get('prompt')
        task_type = request_data.get('task_type', 'general')
        use_consensus = request_data.get('use_consensus', False)
        budget_limit = request_data.get('budget_limit', 1.0)
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        result = await multi_llm.route_task(prompt, task_type, use_consensus, budget_limit)
        
        return {
            "result": result,
            "usage_summary": multi_llm.get_usage_summary(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"LLM orchestration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/llm/cost-summary", dependencies=[Depends(verify_api_key)])
async def get_cost_summary():
    """Get LLM usage and cost summary"""
    return multi_llm.get_usage_summary()

@app.get("/v1/llm/providers", dependencies=[Depends(verify_api_key)])
async def get_providers():
    """Get available LLM providers and their status"""
    provider_status = {}
    
    for provider in multi_llm.providers.keys():
        provider_status[provider] = {
            'available': multi_llm._has_api_key(provider),
            'config': multi_llm.providers[provider]
        }
    
    return {
        "providers": provider_status,
        "total_providers": len(multi_llm.providers),
        "configured_providers": sum(1 for p in provider_status.values() if p['available'])
    }

# ENTERPRISE DEMO ENDPOINTS
@app.post("/v1/demo/customer-demo", dependencies=[Depends(verify_api_key)])
async def customer_demo(demo_data: Dict[str, Any]):
    """Enterprise customer demonstration"""
    try:
        # Demo scenario: Multi-LLM cost optimization
        demo_prompt = demo_data.get('prompt', 'Analyze the competitive advantages of multi-LLM orchestration for enterprise AI deployments')
        
        # Run with multiple providers for comparison
        results = {}
        
        # Try free providers first
        for provider in ['groq', 'google']:
            if multi_llm._has_api_key(provider):
                result = await multi_llm._call_provider(provider, demo_prompt, 0.3, 1.0)
                if result['success']:
                    results[provider] = result
        
        # Calculate cost savings
        usage_summary = multi_llm.get_usage_summary()
        
        return {
            "demo_results": results,
            "cost_analysis": usage_summary['cost_savings'],
            "value_proposition": {
                "cost_savings": f"{usage_summary['cost_savings'].get('savings_percentage', 0):.1f}%",
                "provider_redundancy": len(results),
                "response_quality": "Multi-provider consensus available",
                "vendor_independence": "No single-provider lock-in"
            },
            "enterprise_benefits": [
                "30%+ cost reduction vs single provider",
                "Automatic provider optimization",
                "Built-in redundancy and failover",
                "Real-time cost tracking",
                "Custom task routing"
            ]
        }
        
    except Exception as e:
        logger.error(f"Customer demo error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # For development
    uvicorn.run(
        "sentinel_engine.api:app",
        host="127.0.0.1",
        port=8001,
        log_level="info",
        reload=True
    )
