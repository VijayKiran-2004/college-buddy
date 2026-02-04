"""
Query Router - Intelligent routing between RAG and SQL systems
"""
from app.services.intent_detector import IntentDetector
from app.services.ultra_rag import UltraRAGSystem  # Using new UltraRAG system
from app.services.sql_system import SQLSystem

class QueryRouter:
    def __init__(self):
        """Initialize query router with all systems"""
        print("Initializing Query Router...")
        
        self.intent_detector = IntentDetector()
        print("✓ Intent Detector loaded")
        
        self.rag_system = UltraRAGSystem()  # Using new UltraRAG system
        print("✓ UltraRAG System loaded")
        
        self.sql_system = SQLSystem()
        print("✓ SQL System loaded")
        
        print("✓ Query Router ready!\n")
    
    def route_query(self, query):
        """
        Route query to appropriate system(s)
        
        Args:
            query: Natural language query
        
        Returns:
            Response string
        """
        # Detect intent
        intent = self.intent_detector.detect_intent(query)
        
        if intent == 'general':
            # Use RAG system only
            return self.rag_system(query)
        
        elif intent == 'student':
            # Use SQL system only
            return self.sql_system(query)
        
        elif intent == 'hybrid':
            # Use both systems and combine results
            rag_result = self.rag_system(query)
            sql_result = self.sql_system(query)
            
            # Combine results intelligently
            response = "Based on your query:\n\n"
            response += f"**Student Data:**\n{sql_result}\n\n"
            response += f"**College Information:**\n{rag_result}"
            return response
        
        else:
            return "I couldn't understand your query. Please try rephrasing."
    
    def __call__(self, query):
        """Make class callable"""
        return self.route_query(query)
    
    def close(self):
        """Close all connections"""
        self.sql_system.close()

if __name__ == "__main__":
    # Test query router
    router = QueryRouter()
    
    print("="*70)
    print("TESTING QUERY ROUTER")
    print("="*70 + "\n")
    
    test_queries = [
        "Who is the principal?",  # general -> RAG
        "What are college timings?",  # general -> RAG
        "List all CSE students",  # student -> SQL
        "Show students with CGPA > 8.5",  # student -> SQL
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-"*70)
        response = router(query)
        print(f"Response: {response}")
        print("\n")
    
    router.close()
