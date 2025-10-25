"""
Response caching system to speed up common queries
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional

CACHE_FILE = "response_cache.json"
CACHE_DURATION_HOURS = 24

class ResponseCache:
    def __init__(self):
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load cache from file"""
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def get_cache_key(self, question: str) -> str:
        """Generate cache key from question"""
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, question: str) -> Optional[dict]:
        """Get cached response if available and fresh"""
        key = self.get_cache_key(question)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        cached_time = datetime.fromisoformat(entry["timestamp"])
        
        # Check if cache is still fresh
        if datetime.now() - cached_time > timedelta(hours=CACHE_DURATION_HOURS):
            del self.cache[key]
            self.save_cache()
            return None
        
        return entry["response"]
    
    def set(self, question: str, response):
        """Cache a response (can be string or dict with answer and sources)"""
        key = self.get_cache_key(question)
        self.cache[key] = {
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # Limit cache size to 500 entries
        if len(self.cache) > 500:
            # Remove oldest entries
            sorted_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )
            for old_key in sorted_keys[:100]:
                del self.cache[old_key]
        
        self.save_cache()
    
    def clear_old(self):
        """Clear expired cache entries"""
        expired_keys = []
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry["timestamp"])
            if datetime.now() - cached_time > timedelta(hours=CACHE_DURATION_HOURS):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.save_cache()

# Global instance
response_cache = ResponseCache()
