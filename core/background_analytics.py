"""
Background LLM Analytics - No impact on response time
Runs after user gets their answer
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.client import configure

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    configure(api_key=GEMINI_API_KEY)
    model = GenerativeModel('gemini-2.0-flash-exp')
else:
    model = None
    logger.warning("No Gemini API key - background analytics disabled")


class BackgroundAnalytics:
    """Analyzes queries and responses in background (no user delay)"""
    
    def __init__(self, analytics_file: str = "data/analytics/background_analytics.json"):
        self.analytics_file = analytics_file
        self.load_analytics()
    
    def load_analytics(self):
        """Load existing analytics data"""
        try:
            if os.path.exists(self.analytics_file):
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "query_categories": {},
                    "topic_trends": [],
                    "confusion_indicators": [],
                    "voice_usage": {
                        "voice_queries": 0,
                        "text_queries": 0,
                        "voice_languages": {}
                    },
                    "last_updated": None
                }
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
            self.data = {}
    
    def save_analytics(self):
        """Save analytics data"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
    
    def categorize_query_async(self, query: str, response: str):
        """
        Categorize query in background (runs AFTER user gets response)
        NO DELAY to user experience
        """
        if not model:
            return
        
        try:
            prompt = f"""Categorize this college chatbot query into ONE category:
            
Query: {query}
Response given: {response[:200]}...

Categories: admission, placement, faculty, fees, facilities, courses, timing, events, contact, other

Just respond with the category name (one word)."""

            result = model.generate_content(prompt)
            category = result.text.strip().lower()
            
            # Update statistics
            if category in self.data.get("query_categories", {}):
                self.data["query_categories"][category] += 1
            else:
                if "query_categories" not in self.data:
                    self.data["query_categories"] = {}
                self.data["query_categories"][category] = 1
            
            self.save_analytics()
            logger.info(f"📊 Query categorized as: {category}")
            
        except Exception as e:
            logger.error(f"Background categorization error: {e}")
    
    def detect_confusion_async(self, query: str, response: str, user_feedback: Optional[str] = None):
        """
        Detect if user seems confused (runs in background)
        """
        if not model or not user_feedback:
            return
        
        try:
            # Check if user gave negative feedback or asked follow-up
            confusion_indicators = [
                "what?", "unclear", "confused", "don't understand", 
                "explain", "still", "but", "however"
            ]
            
            if any(indicator in user_feedback.lower() for indicator in confusion_indicators):
                confusion_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "response_preview": response[:100],
                    "user_feedback": user_feedback
                }
                
                if "confusion_indicators" not in self.data:
                    self.data["confusion_indicators"] = []
                
                self.data["confusion_indicators"].append(confusion_entry)
                self.save_analytics()
                logger.warning(f"⚠️ Possible confusion detected: {query}")
        
        except Exception as e:
            logger.error(f"Confusion detection error: {e}")
    
    def generate_weekly_report(self) -> Dict:
        """
        Generate insights report (run as scheduled task, not during queries)
        """
        if not model:
            return {"error": "No LLM available"}
        
        try:
            # Top categories
            categories = self.data.get("query_categories", {})
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Generate insights with LLM
            prompt = f"""Analyze these college chatbot statistics and provide insights:

Top query categories: {dict(top_categories)}
Confusion indicators: {len(self.data.get('confusion_indicators', []))} cases

Provide 3-5 actionable insights for improving the chatbot."""

            result = model.generate_content(prompt)
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "top_categories": dict(top_categories),
                "total_queries": sum(categories.values()),
                "confusion_cases": len(self.data.get("confusion_indicators", [])),
                "insights": result.text,
            }
            
            logger.info("📈 Weekly report generated")
            return report
        
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {"error": str(e)}
    
    def get_statistics(self) -> Dict:
        """Get current statistics (fast, no LLM)"""
        return {
            "total_categories": len(self.data.get("query_categories", {})),
            "most_common": max(
                self.data.get("query_categories", {}).items(), 
                key=lambda x: x[1], 
                default=("none", 0)
            ),
            "confusion_cases": len(self.data.get("confusion_indicators", [])),
            "last_updated": self.data.get("last_updated", "Never")
        }


# Global instance
analytics = BackgroundAnalytics()


# Easy-to-use functions
def analyze_query_background(query: str, response: str):
    """
    Call this AFTER sending response to user (no delay!)
    """
    try:
        analytics.categorize_query_async(query, response)
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")


def detect_user_confusion(query: str, response: str, feedback: Optional[str] = None):
    """
    Call when user provides feedback
    """
    try:
        analytics.detect_confusion_async(query, response, feedback)
    except Exception as e:
        logger.error(f"Confusion detection failed: {e}")


def get_quick_stats() -> Dict:
    """
    Get statistics instantly (no LLM call)
    """
    return analytics.get_statistics()


def generate_insights_report() -> Dict:
    """
    Generate detailed report (run as scheduled task)
    """
    return analytics.generate_weekly_report()


def track_voice_usage(is_voice: bool = False, language: str = "en-US"):
    """
    Track voice vs text input usage (instant, no LLM)
    """
    try:
        if "voice_usage" not in analytics.data:
            analytics.data["voice_usage"] = {
                "voice_queries": 0,
                "text_queries": 0,
                "voice_languages": {}
            }
        
        if is_voice:
            analytics.data["voice_usage"]["voice_queries"] += 1
            lang_key = language.split('-')[0]  # 'en', 'te', 'hi'
            analytics.data["voice_usage"]["voice_languages"][lang_key] = \
                analytics.data["voice_usage"]["voice_languages"].get(lang_key, 0) + 1
        else:
            analytics.data["voice_usage"]["text_queries"] += 1
        
        analytics.save_analytics()
        logger.info(f"📊 Voice usage tracked: {'voice' if is_voice else 'text'} ({language})")
        
    except Exception as e:
        logger.error(f"Voice tracking failed: {e}")


if __name__ == "__main__":
    # Test
    print("📊 Current Statistics:")
    print(json.dumps(get_quick_stats(), indent=2))
