"""
Human Approval System - Phase 4
Multi-stage approval workflow with modification and termination options
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class ApprovalRequest:
    def __init__(self, approval_type, business_idea_id, content):
        self.id = str(uuid.uuid4())[:8]
        self.approval_type = approval_type
        self.business_idea_id = business_idea_id
        self.content = content
        self.status = "pending"
        self.created_at = datetime.utcnow().isoformat()
        self.decided_at = None
        self.feedback = None

class ApprovalSystem:
    def __init__(self):
        self.pending_approvals = {}
        self.approval_history = []
    
    def request_approval(self, approval_type, business_idea_id, content):
        approval = ApprovalRequest(approval_type, business_idea_id, content)
        self.pending_approvals[approval.id] = approval
        return approval.id
    
    def process_approval(self, approval_id, decision, feedback=None):
        approval = self.pending_approvals.get(approval_id)
        if not approval:
            return {"error": "Approval not found"}
        
        if decision.lower() in ["yes", "approved"]:
            approval.status = "approved"
            next_action = "proceed_to_building"
        elif decision.lower() in ["no_fix", "needs_changes"]:
            approval.status = "needs_changes"
            next_action = "revise_and_resubmit"
        elif decision.lower() in ["no_terminate", "rejected"]:
            approval.status = "rejected"
            next_action = "terminate_idea"
        else:
            return {"error": "Invalid decision"}
        
        approval.decided_at = datetime.utcnow().isoformat()
        approval.feedback = feedback
        
        self.approval_history.append(approval)
        del self.pending_approvals[approval_id]
        
        return {
            "approval_id": approval_id,
            "status": approval.status,
            "feedback": feedback,
            "next_action": next_action
        }
    
    def get_pending_approvals(self):
        return list(self.pending_approvals.values())

# Global instance
approval_system = ApprovalSystem()
