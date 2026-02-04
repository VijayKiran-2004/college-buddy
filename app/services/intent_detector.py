"""
Intent Detector - Routes queries to RAG or SQL system
"""
import re

class IntentDetector:
    def __init__(self):
        """Initialize intent detector with keyword patterns"""
        
        # Keywords that indicate student-specific queries
        self.student_keywords = [
            'student', 'students', 'cgpa', 'attendance', 
            'marks', 'grade', 'roll number', 'student id',
            'name', 'section', 'year', 'batch', 'semester'
        ]
        
        # Keywords that indicate general college queries
        self.general_keywords = [
            'college', 'department', 'hod', 'principal',
            'facility', 'library', 'hostel', 'admission',
            'fee', 'course', 'program', 'timings', 'contact',
            'placement', 'faculty', 'dean', 'ncc', 'nss'
        ]
    
    def detect_intent(self, query):
        """
        Detect query intent
        
        Returns:
            'student' - Query about specific student(s)
            'general' - Query about college info
            'hybrid' - Query needs both RAG and SQL
        """
        query_lower = query.lower()
        
        # Check for student-related patterns
        has_student_keywords = any(kw in query_lower for kw in self.student_keywords)
        has_general_keywords = any(kw in query_lower for kw in self.general_keywords)
        
        # Check for student ID pattern (numeric)
        has_student_id = bool(re.search(r'\b\d{5,10}\b', query))
        
        # Check for CGPA/attendance conditions
        has_student_condition = bool(re.search(r'(cgpa|attendance)\s*[><=]', query_lower))
        
        # Decision logic
        if (has_student_keywords or has_student_id or has_student_condition) and has_general_keywords:
            return 'hybrid'  # Needs both systems
        elif has_student_keywords or has_student_id or has_student_condition:
            return 'student'  # SQL only
        else:
            return 'general'  # RAG only
    
    def extract_entities(self, query):
        """
        Extract entities from query
        
        Returns dict with:
            - student_id
            - department
            - name
            - cgpa_condition
            - attendance_condition
        """
        query_lower = query.lower()
        entities = {}
        
        # Extract student ID
        student_id_match = re.search(r'\b(\d{5,10})\b', query)
        if student_id_match:
            entities['student_id'] = student_id_match.group(1)
        
        # Extract department
        departments = ['cse', 'ece', 'eee', 'civil', 'mechanical', 'it', 'mba']
        for dept in departments:
            if dept in query_lower:
                entities['department'] = dept.upper()
                break
        
        # Extract name (capitalized words)
        name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', query)
        if name_match:
            entities['name'] = name_match.group(1)
        
        return entities

if __name__ == "__main__":
    # Test intent detector
    detector = IntentDetector()
    
    test_queries = [
        "Who is the principal?",  # general
        "What is the CGPA of student 12345?",  # student
        "List CSE students",  # student
        "What are college timings?",  # general
        "Which CSE students are eligible for placements?",  # hybrid
        "Show students with CGPA > 8.5 and tell me about placement process",  # hybrid
    ]
    
    print("Testing Intent Detector...")
    print("="*70 + "\n")
    
    for query in test_queries:
        intent = detector.detect_intent(query)
        entities = detector.extract_entities(query)
        print(f"Query: {query}")
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        print()
