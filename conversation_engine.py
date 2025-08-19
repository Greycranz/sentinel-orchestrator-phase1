"""
Conversation Intelligence Engine - Phase 4
Transforms simple business ideas into comprehensive business plans
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class BusinessIdea:
    def __init__(self, idea_text):
        self.id = str(uuid.uuid4())[:8]
        self.original_input = idea_text
        self.current_stage = "conversation"
        self.conversation_history = [
            {"speaker": "user", "message": idea_text, "timestamp": datetime.utcnow().isoformat()}
        ]
        self.business_plan = None
        self.approval_status = "pending"
        self.created_at = datetime.utcnow().isoformat()

class ConversationEngine:
    def __init__(self):
        self.active_ideas = {}
    
    def start_conversation(self, user_input):
        idea = BusinessIdea(user_input)
        self.active_ideas[idea.id] = idea
        return idea
    
    def get_next_question(self, idea_id):
        idea = self.active_ideas.get(idea_id)
        if not idea:
            return {"error": "Idea not found"}
        
        conversation_count = len([msg for msg in idea.conversation_history if msg["speaker"] == "user"])
        
        questions = [
            "What specific problem does this solve, and who would be your target customers?",
            "How do you envision making money from this? What would be your primary revenue streams?", 
            "What existing solutions or competitors are in this space? How would your approach be different?",
            "What technical capabilities would be needed to build this?",
            "What key resources, team members, or partnerships would be essential for success?"
        ]
        
        if conversation_count <= len(questions):
            return {"question": questions[conversation_count - 1], "complete": False}
        else:
            return {"question": "Perfect! Creating your business plan...", "complete": True}

# Global instance
conversation_engine = ConversationEngine()
