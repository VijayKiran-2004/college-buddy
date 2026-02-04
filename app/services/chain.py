"""
Simple Knowledge Base Helper
Used as fallback responder when LLM is not available
"""

from typing import List, Dict, Optional


# Knowledge Base (same as in rag_system.py)
KNOWLEDGE_BASE = {
    "personnel": {
        "principal": "Dr. D. V. Ravi Shankar",
        "vice_principal": "Dr. A. Suresh Rao",
        "secretary": "Dr. T. Harinath Reddy",
        "chairman": "Sri. Teegala Krishna Reddy",
        "founder": "Sri. Teegala Krishna Reddy",
        "hod": {
            "cse": "Dr. A. Suresh Rao",
            "cse-aiml": "Dr. B. Sunil Srinivas",
            "csm": "Dr. B. Sunil Srinivas",
            "cse-ds": "Dr. V. Krishna",
            "csd": "Dr. V. Krishna",
            "ece": "Dr. D. Nageshwar Rao",
            "eee": "Dr. K. Raju",
            "it": "Dr. R. Muruanantham",
            "mech": "Mr. D. Rushi Kumar",
            "civil": "Mr. K.V.R Satya Sai",
            "mba": "Dr. K. Gyaneswari"
        }
    },
    "timings": {
        "working_hours": "9:40 AM to 4:20 PM (Monday-Saturday)",
        "lunch_break": "12:40 PM to 1:20 PM"
    },
    "history": {
        "established": "2002",
        "affiliation": "JNTUH",
        "location": "Medbowli, Hyderabad"
    }
}


class SimpleRAGResponder:
    """Simple responder using knowledge base"""
    
    def __init__(self):
        self.kb = KNOWLEDGE_BASE
    
    def respond(self, query: str, documents: List[Dict] = None) -> Optional[str]:
        """Generate response - returns None if KB doesn't have the answer"""
        query_lower = query.lower()
        
        # Check for personnel
        if 'principal' in query_lower:
            return f"The Principal is {self.kb['personnel']['principal']}."
        
        if 'hod' in query_lower or 'head' in query_lower:
            for dept, hod in self.kb['personnel']['hod'].items():
                if dept in query_lower:
                    return f"The HOD of {dept.upper()} is {hod}."
        
        # Check for timings
        if 'timing' in query_lower or 'hours' in query_lower:
            return f"Working hours: {self.kb['timings']['working_hours']}."
        
        # Check for history
        if 'established' in query_lower or 'founded' in query_lower:
            return f"TKRCET was established in {self.kb['history']['established']}."
        
        # No KB answer - return None to trigger LLM
        return None
