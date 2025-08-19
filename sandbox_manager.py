"""
🧪 Sandbox Manager with Emergency Controls
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SandboxEnvironment:
    def __init__(self, sandbox_id, company_name, port):
        self.sandbox_id = sandbox_id
        self.company_name = company_name
        self.port = port
        self.process_id = None
        self.status = "created"
        self.created_at = datetime.utcnow()
        self.url = f"http://localhost:{port}"

class SandboxManager:
    def __init__(self):
        self.active_sandboxes = {}
        self.emergency_mode = False
        
    def create_sandbox(self, company_name):
        sandbox_id = f"sandbox_{len(self.active_sandboxes)+1:03d}"
        port = 9000 + len(self.active_sandboxes)
        
        sandbox = SandboxEnvironment(sandbox_id, company_name, port)
        self.active_sandboxes[sandbox_id] = sandbox
        
        logger.info(f"Sandbox created: {sandbox_id}")
        return sandbox
    
    def emergency_stop_all(self):
        """EMERGENCY: Stop all operations"""
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.emergency_mode = True
        
        for sandbox_id, sandbox in self.active_sandboxes.items():
            sandbox.status = "emergency_stopped"
        
        return {"status": "emergency_stop_complete", "emergency_mode": True}
    
    def enable_manual_mode(self):
        self.emergency_mode = True
        return {"status": "manual_mode_enabled", "automation": "disabled"}
    
    def disable_emergency_mode(self):
        self.emergency_mode = False
        return {"status": "normal_operations_restored"}
    
    def get_safety_status(self):
        return {
            "emergency_mode": self.emergency_mode,
            "active_sandboxes": len(self.active_sandboxes),
            "safety_systems": "operational"
        }

sandbox_manager = SandboxManager()
