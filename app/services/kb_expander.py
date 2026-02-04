"""
Knowledge Base Expander
Automatically expands static KB by learning from user queries and web scraping
"""

import json
import requests
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path


class KnowledgeBaseExpander:
    """Smart KB expansion using analytics and LLM reasoning"""
    
    def __init__(self):
        """Initialize KB expander"""
        self.kb_path = Path("app/services/ultra_rag.py")
        self.suggestions_path = Path("app/database/kb_suggestions.json")
        
        # Load analytics
        try:
            from app.services.analytics import AnalyticsSystem
            self.analytics = AnalyticsSystem()
        except:
            self.analytics = None
        
        # Load existing suggestions
        self.suggestions = self._load_suggestions()
    
    def _load_suggestions(self) -> dict:
        """Load pending KB suggestions"""
        if self.suggestions_path.exists():
            with open(self.suggestions_path, 'r') as f:
                return json.load(f)
        return {"pending": [], "approved": [], "rejected": []}
    
    def _save_suggestions(self):
        """Save KB suggestions"""
        self.suggestions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.suggestions_path, 'w') as f:
            json.dump(self.suggestions, f, indent=2)
    
    def identify_knowledge_gaps(self, days: int = 7) -> List[str]:
        """Find frequently asked questions that went to web search"""
        if not self.analytics:
            return []
        
        # Get queries that used web search (not in static KB)
        recent_queries = self.analytics.get_recent_queries(limit=100)
        
        # Filter for web search queries
        web_queries = [
            q['query'] for q in recent_queries 
            if q['tool_used'] == 'search_website' and q['success']
        ]
        
        # Count frequency
        from collections import Counter
        query_counts = Counter(web_queries)
        
        # Return top 10 most frequent gaps
        gaps = [q for q, count in query_counts.most_common(10) if count >= 2]
        
        return gaps
    
    def extract_facts_from_text(self, text: str, topic: str) -> Dict[str, Any]:
        """Use LLM to extract structured facts from text"""
        try:
            # Prepare prompt for fact extraction
            prompt = f"""Extract factual information from this college website content about "{topic}".

Content: {text[:1000]}

Return ONLY a JSON object with this structure:
{{
  "category": "one of: personnel, facilities, events, courses, fees, scholarships, clubs, sports",
  "facts": [
    {{"key": "specific_item", "value": "factual_value"}},
    ...
  ],
  "confidence": 0.0-1.0
}}

Be precise and factual. Only include information explicitly stated in the content."""

            # Call Ollama Gemma 2:2b
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'gemma2:2b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,  # Low temperature for factual extraction
                        'num_predict': 300
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                llm_response = response.json().get('response', '').strip()
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from response (might have extra text)
                    start = llm_response.find('{')
                    end = llm_response.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = llm_response[start:end]
                        facts = json.loads(json_str)
                        return facts
                except:
                    pass
        
        except Exception as e:
            print(f"Fact extraction error: {e}")
        
        return None
    
    def suggest_kb_update(self, query: str, web_content: str):
        """Analyze web content and suggest KB update"""
        # Extract facts using LLM
        facts = self.extract_facts_from_text(web_content, query)
        
        if not facts or facts.get('confidence', 0) < 0.7:
            return None
        
        # Create suggestion
        suggestion = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "category": facts.get('category'),
            "facts": facts.get('facts', []),
            "confidence": facts.get('confidence', 0),
            "status": "pending"
        }
        
        # Add to suggestions
        self.suggestions['pending'].append(suggestion)
        self._save_suggestions()
        
        return suggestion
    
    def get_pending_suggestions(self) -> List[Dict]:
        """Get all pending KB suggestions"""
        return self.suggestions.get('pending', [])
    
    def approve_suggestion(self, index: int):
        """Approve a KB suggestion and add to KB"""
        if index < 0 or index >= len(self.suggestions['pending']):
            return False
        
        suggestion = self.suggestions['pending'].pop(index)
        suggestion['status'] = 'approved'
        suggestion['approved_at'] = datetime.now().isoformat()
        
        self.suggestions['approved'].append(suggestion)
        self._save_suggestions()
        
        # TODO: Actually update ultra_rag.py KNOWLEDGE_BASE
        # For now, just flag as approved
        
        return True
    
    def reject_suggestion(self, index: int):
        """Reject a KB suggestion"""
        if index < 0 or index >= len(self.suggestions['pending']):
            return False
        
        suggestion = self.suggestions['pending'].pop(index)
        suggestion['status'] = 'rejected'
        suggestion['rejected_at'] = datetime.now().isoformat()
        
        self.suggestions['rejected'].append(suggestion)
        self._save_suggestions()
        
        return True
    
    def auto_expand(self, min_confidence: float = 0.85):
        """Automatically expand KB with high-confidence facts"""
        approved_count = 0
        
        for i, suggestion in enumerate(self.suggestions['pending'][:]):
            if suggestion['confidence'] >= min_confidence:
                self.approve_suggestion(i - approved_count)
                approved_count += 1
                print(f"✓ Auto-approved: {suggestion['query']} (confidence: {suggestion['confidence']})")
        
        return approved_count
    
    def generate_report(self) -> str:
        """Generate KB expansion report"""
        gaps = self.identify_knowledge_gaps()
        pending = len(self.suggestions['pending'])
        approved = len(self.suggestions['approved'])
        rejected = len(self.suggestions['rejected'])
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║           KNOWLEDGE BASE EXPANSION REPORT                        ║
╚══════════════════════════════════════════════════════════════════╝

📊 Knowledge Gaps Identified: {len(gaps)}
   {', '.join(gaps[:5]) if gaps else 'None'}

📝 Pending Suggestions: {pending}
✅ Approved Updates: {approved}
❌ Rejected Suggestions: {rejected}

💡 Recommendation:
   - Review pending suggestions
   - Auto-approve high-confidence (>0.85) facts
   - Manually review medium-confidence (0.7-0.85) facts
"""
        return report


if __name__ == "__main__":
    # Test KB expander
    expander = KnowledgeBaseExpander()
    
    # Identify gaps
    print("Identifying knowledge gaps...")
    gaps = expander.identify_knowledge_gaps()
    print(f"Found {len(gaps)} gaps: {gaps}")
    
    # Generate report
    print(expander.generate_report())
    
    # Test fact extraction
    sample_text = """
    TKRCET has several active student clubs including the IEEE Student Branch,
    CSI Chapter, Coding Club, Robotics Club, and Literary Club. The college
    also has a Photography Club and Music Club for cultural activities.
    """
    
    facts = expander.extract_facts_from_text(sample_text, "student clubs")
    print(f"\nExtracted facts: {json.dumps(facts, indent=2)}")
