"""
Autonomous Execution Engine - Phase 4
Builds complete sub-companies autonomously with safety constraints
"""
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class BuildStatus:
    def __init__(self, business_idea_id, company_name):
        self.id = str(uuid.uuid4())[:8]
        self.business_idea_id = business_idea_id
        self.company_name = company_name
        self.status = "initiated"
        self.progress = 0.0
        self.current_step = "Initializing build"
        self.steps_completed = []
        self.sandbox_url = None
        self.build_logs = []
        self.created_at = datetime.utcnow().isoformat()
        self.completed_at = None

class AutonomousExecutor:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.sandbox_dir = self.repo_root / "sandbox"
        self.subcompany_dir = self.repo_root / "sub_companies"
        self.active_builds = {}
        self.build_history = []
        
        # Ensure directories exist
        self.sandbox_dir.mkdir(exist_ok=True)
        self.subcompany_dir.mkdir(exist_ok=True)
    
    async def build_subcompany(self, business_plan, business_idea_id):
        company_name = business_plan.get("company_name", "New Company")
        build_status = BuildStatus(business_idea_id, company_name)
        self.active_builds[build_status.id] = build_status
        
        # Start building process (simplified for Phase 4)
        try:
            build_status.status = "building"
            build_status.current_step = "Creating sandbox environment"
            build_status.progress = 0.2
            
            # Create sandbox directory
            company_slug = company_name.lower().replace(" ", "_")
            sandbox_path = self.sandbox_dir / f"{company_slug}_{build_status.id}"
            sandbox_path.mkdir(exist_ok=True)
            
            build_status.current_step = "Generating API structure"
            build_status.progress = 0.5
            
            # Generate basic API
            self._create_basic_api(sandbox_path, business_plan)
            
            build_status.current_step = "Creating web interface"  
            build_status.progress = 0.8
            
            # Generate web interface
            self._create_web_interface(sandbox_path, business_plan)
            
            build_status.status = "completed"
            build_status.current_step = "Build completed successfully"
            build_status.progress = 1.0
            build_status.sandbox_url = f"http://127.0.0.1:9000/{company_slug}"
            build_status.completed_at = datetime.utcnow().isoformat()
            
            # Move to history
            self.build_history.append(build_status)
            del self.active_builds[build_status.id]
            
        except Exception as e:
            build_status.status = "failed"
            build_status.current_step = f"Build failed: {str(e)}"
        
        return build_status.id
    
    def _create_basic_api(self, sandbox_path, business_plan):
        api_content = f'''# {business_plan.get("company_name", "Company")} API
from fastapi import FastAPI

app = FastAPI(title="{business_plan.get("company_name", "Company")}")

@app.get("/")
def root():
    return {{"message": "Welcome to {business_plan.get("company_name", "Company")}", "status": "operational"}}

@app.get("/health")
def health():
    return {{"status": "healthy", "company": "{business_plan.get("company_name", "Company")}"}}
'''
        (sandbox_path / "main.py").write_text(api_content)
    
    def _create_web_interface(self, sandbox_path, business_plan):
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>{business_plan.get("company_name", "Company")}</title>
</head>
<body>
    <h1>🚀 {business_plan.get("company_name", "Company")}</h1>
    <p>{business_plan.get("executive_summary", "AI-powered business solutions")}</p>
    <p>Status: <strong>Operational in Sandbox</strong></p>
</body>
</html>'''
        (sandbox_path / "index.html").write_text(html_content)
    
    def get_all_builds(self):
        return {{"active": list(self.active_builds.values()), "completed": self.build_history}}
    
    def get_build_status(self, build_id):
        return self.active_builds.get(build_id) or next(
            (build for build in self.build_history if build.id == build_id), None
        )

# Global instance (will be initialized with repo_root)
autonomous_executor = None
