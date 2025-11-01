"""
Analytics and logging system for College Buddy chatbot
Tracks user queries, response times, and popular topics
"""

import json
import os
from datetime import datetime
from collections import defaultdict
from pathlib import Path

ANALYTICS_FILE = "data/analytics/analytics_data.json"

class ChatAnalytics:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        """Load existing analytics data"""
        if os.path.exists(ANALYTICS_FILE):
            try:
                with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_queries": 0,
            "queries_by_category": defaultdict(int),
            "avg_response_time": 0,
            "popular_questions": [],
            "failed_queries": [],
            "daily_stats": {}
        }
    
    def log_query(self, question, category, response_time, success=True):
        """Log a user query with metadata"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update totals
        self.data["total_queries"] += 1
        
        # Category tracking
        if category not in self.data["queries_by_category"]:
            self.data["queries_by_category"][category] = 0
        self.data["queries_by_category"][category] += 1
        
        # Daily stats
        if today not in self.data["daily_stats"]:
            self.data["daily_stats"][today] = {"count": 0, "categories": {}}
        self.data["daily_stats"][today]["count"] += 1
        
        if category not in self.data["daily_stats"][today]["categories"]:
            self.data["daily_stats"][today]["categories"][category] = 0
        self.data["daily_stats"][today]["categories"][category] += 1
        
        # Response time tracking
        total_time = self.data.get("total_response_time", 0) + response_time
        self.data["total_response_time"] = total_time
        self.data["avg_response_time"] = total_time / self.data["total_queries"]
        
        # Track failed queries
        if not success:
            self.data["failed_queries"].append({
                "question": question,
                "timestamp": datetime.now().isoformat(),
                "category": category
            })
            # Keep only last 100 failed queries
            self.data["failed_queries"] = self.data["failed_queries"][-100:]
        
        self.save_data()
    
    def save_data(self):
        """Persist analytics data to file"""
        try:
            with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Failed to save analytics: {e}")
    
    def get_summary(self):
        """Get analytics summary"""
        top_categories = sorted(
            self.data["queries_by_category"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "total_queries": self.data["total_queries"],
            "avg_response_time": f"{self.data['avg_response_time']:.2f}s",
            "top_categories": top_categories,
            "failed_count": len(self.data["failed_queries"])
        }

# Global instance
analytics = ChatAnalytics()
