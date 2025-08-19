"""
Autonomous Financial Manager - CFO Agent
Automates all financial decisions and budget optimization
"""
import json
from datetime import datetime
from typing import Dict, List

class FinancialManager:
    def __init__(self):
        self.budget = {"total": 0, "allocated": {}, "spent": {}}
        self.revenue = {"monthly": 0, "total": 0, "customers": {}}
        self.decisions = []
        
    def track_revenue(self, customer_id, amount, description="Monthly subscription"):
        """Track incoming revenue"""
        self.revenue["monthly"] += amount
        self.revenue["total"] += amount
        self.revenue["customers"][customer_id] = amount
        
        # Auto-allocate budget based on revenue
        self._auto_allocate_budget()
        
        return {
            "revenue_tracked": amount,
            "total_monthly": self.revenue["monthly"],
            "budget_allocated": self._get_budget_allocation()
        }
    
    def _auto_allocate_budget(self):
        """Automatically allocate budget based on revenue"""
        monthly_revenue = self.revenue["monthly"]
        
        # Conservative allocation: 30% for growth, 70% profit
        growth_budget = monthly_revenue * 0.3
        
        self.budget["allocated"] = {
            "api_upgrades": growth_budget * 0.4,  # 40% for better APIs
            "marketing": growth_budget * 0.3,     # 30% for customer acquisition  
            "infrastructure": growth_budget * 0.2, # 20% for scaling
            "development": growth_budget * 0.1     # 10% for new features
        }
    
    def should_upgrade_api(self, current_usage, cost_per_request):
        """Autonomous decision: Should we upgrade to paid APIs?"""
        monthly_api_cost = current_usage * cost_per_request * 30
        available_budget = self.budget["allocated"].get("api_upgrades", 0)
        
        # Only upgrade if we have 3x the monthly cost available
        if available_budget >= monthly_api_cost * 3:
            decision = {
                "decision": "APPROVE_UPGRADE",
                "reasoning": f"Budget allows 3x safety margin (${available_budget:.2f} vs ${monthly_api_cost:.2f})",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            decision = {
                "decision": "DENY_UPGRADE", 
                "reasoning": f"Insufficient budget safety margin (${available_budget:.2f} vs ${monthly_api_cost:.2f})",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        self.decisions.append(decision)
        return decision
    
    def get_financial_health(self):
        """Get complete financial health report"""
        return {
            "revenue": self.revenue,
            "budget": self.budget,
            "recent_decisions": self.decisions[-5:],
            "financial_health": "Excellent" if self.revenue["monthly"] > 1000 else "Good",
            "growth_rate": "Tracking for autonomous expansion"
        }
    
    def _get_budget_allocation(self):
        """Get current budget allocation"""
        return self.budget["allocated"]

# Global financial manager
financial_manager = FinancialManager()
