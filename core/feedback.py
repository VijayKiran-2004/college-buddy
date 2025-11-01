"""
User feedback collection system
Tracks helpful/unhelpful responses to improve the chatbot
"""

import json
import os
from datetime import datetime
from typing import Optional

FEEDBACK_FILE = "user_feedback.json"

class FeedbackCollector:
    def __init__(self):
        self.feedback = self.load_feedback()
    
    def load_feedback(self):
        """Load existing feedback data"""
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "responses": [],
            "stats": {
                "helpful": 0,
                "unhelpful": 0,
                "total": 0
            }
        }
    
    def save_feedback(self):
        """Save feedback to file"""
        try:
            with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.feedback, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save feedback: {e}")
    
    def add_feedback(self, question: str, response: str, is_helpful: bool, comment: Optional[str] = None):
        """Record user feedback"""
        entry = {
            "question": question,
            "response": response[:200],  # Truncate long responses
            "is_helpful": is_helpful,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback["responses"].append(entry)
        
        # Update stats
        self.feedback["stats"]["total"] += 1
        if is_helpful:
            self.feedback["stats"]["helpful"] += 1
        else:
            self.feedback["stats"]["unhelpful"] += 1
        
        # Keep only last 1000 entries
        if len(self.feedback["responses"]) > 1000:
            self.feedback["responses"] = self.feedback["responses"][-1000:]
        
        self.save_feedback()
    
    def get_unhelpful_responses(self, limit=20):
        """Get recent unhelpful responses for improvement"""
        unhelpful = [
            r for r in self.feedback["responses"] 
            if not r["is_helpful"]
        ]
        return unhelpful[-limit:]
    
    def get_stats(self):
        """Get feedback statistics"""
        stats = self.feedback["stats"]
        if stats["total"] > 0:
            satisfaction_rate = (stats["helpful"] / stats["total"]) * 100
        else:
            satisfaction_rate = 0
        
        return {
            "total_feedback": stats["total"],
            "helpful": stats["helpful"],
            "unhelpful": stats["unhelpful"],
            "satisfaction_rate": f"{satisfaction_rate:.1f}%"
        }

# Global instance
feedback_collector = FeedbackCollector()
