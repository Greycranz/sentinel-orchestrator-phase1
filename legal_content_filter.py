"""
⚖️ Legal Content Filtering & Copyright Detection
"""
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalContentFilter:
    def __init__(self):
        self.protected_terms = [
            "pokemon", "nintendo", "mario", "zelda", "marvel", "disney", 
            "star wars", "apple", "google", "microsoft", "unreal engine"
        ]
    
    def analyze_business_idea(self, business_idea):
        analysis = {
            "idea": business_idea,
            "copyright_risks": self._detect_copyright_risks(business_idea),
            "risk_level": "low",
            "recommendations": [],
            "legal_review_required": False
        }
        
        if analysis["copyright_risks"]:
            analysis["risk_level"] = "high"
            analysis["legal_review_required"] = True
            analysis["recommendations"].append("Legal review required")
        
        return analysis
    
    def _detect_copyright_risks(self, text):
        risks = []
        text_lower = text.lower()
        
        for term in self.protected_terms:
            if term in text_lower:
                risks.append({
                    "term": term,
                    "risk_type": "copyright/trademark",
                    "severity": "high",
                    "recommendation": f"Avoid direct reference to '{term}'"
                })
        
        return risks

legal_filter = LegalContentFilter()
