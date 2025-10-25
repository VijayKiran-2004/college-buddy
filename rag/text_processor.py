"""
Text processing utilities with robust error handling.
"""
import re
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive topic patterns for intelligent query classification
TOPIC_PATTERNS = {
    "faculty": [
        r"faculty", r"professor", r"teacher", r"staff", r"department head", r"hod",
        r"lecturer", r"teaching", r"instructor", r"faculties", r"teaching staff",
        r"who teaches", r"who is", r"faculty member", r"faculty profile"
    ],
    "timing": [
        r"timing", r"schedule", r"hour", r"time", r"working", r"class",
        r"period", r"duration", r"college timing", r"what time", r"when does",
        r"office hour", r"academic calendar", r"timetable", r"time table"
    ],
    "admission": [
        r"admission", r"apply", r"join", r"enroll", r"register", r"application",
        r"entrance", r"selection", r"seat", r"intake", r"how to apply",
        r"eligibility", r"criteria", r"admission process", r"get admission",
        r"admission procedure", r"admission form", r"counseling"
    ],
    "fee": [
        r"fee", r"payment", r"cost", r"amount", r"charge", r"expense",
        r"scholarship", r"financial", r"pay", r"tuition", r"how much",
        r"price", r"fee structure", r"total fee", r"annual fee", r"semester fee",
        r"reimbursement", r"fee details", r"fee payment"
    ],
    "facility": [
        r"facility", r"infrastructure", r"lab", r"laboratory", r"library",
        r"hostel", r"canteen", r"campus", r"amenity", r"facilities",
        r"sports", r"gym", r"playground", r"auditorium", r"seminar hall",
        r"workshop", r"cafeteria", r"transport", r"bus", r"wifi", r"internet"
    ],
    "placement": [
        r"placement", r"job", r"career", r"company", r"recruit", r"package",
        r"salary", r"internship", r"employment", r"placed", r"placements",
        r"highest package", r"average package", r"recruitment", r"companies visited",
        r"placement record", r"placement statistics", r"placement drive"
    ],
    "course": [
        r"course", r"branch", r"stream", r"program", r"department", r"degree",
        r"major", r"specialization", r"subject", r"curriculum", r"syllabus",
        r"what courses", r"which branch", r"programs offered", r"departments",
        r"course structure", r"course details"
    ],
    "exam": [
        r"exam", r"examination", r"test", r"assessment", r"marks", r"grade",
        r"result", r"score", r"evaluation", r"mid-term", r"semester exam",
        r"final exam", r"internal", r"exam schedule", r"exam pattern",
        r"revaluation", r"supplementary", r"passing criteria"
    ],
    "hostel": [
        r"hostel", r"accommodation", r"residence", r"staying", r"room",
        r"mess", r"residential", r"boys hostel", r"girls hostel",
        r"hostel facility", r"hostel admission", r"hostel fee", r"hostel rules"
    ],
    "accreditation": [
        r"accreditation", r"accredited", r"naac", r"nba", r"aicte", r"ugc",
        r"approval", r"recognition", r"affiliation", r"ranking", r"nirf",
        r"rating", r"autonomous", r"certified", r"approved", r"affiliated"
    ],
    "events": [
        r"event", r"fest", r"festival", r"cultural", r"technical", r"workshop",
        r"seminar", r"conference", r"competition", r"hackathon", r"symposium",
        r"guest lecture", r"activities", r"annual day", r"sports event",
        r"extra-curricular", r"club", r"student activity"
    ],
    "research": [
        r"research", r"r&d", r"innovation", r"patent", r"publication",
        r"research project", r"phd", r"research center", r"research paper",
        r"research scholar", r"research facility", r"research work"
    ],
    "contact": [
        r"contact", r"address", r"phone", r"email", r"location", r"reach",
        r"how to reach", r"where is", r"contact detail", r"contact information",
        r"helpline", r"enquiry", r"contact number", r"office address"
    ]
}

# Common abbreviations and their expansions
ABBREVIATIONS = {
    "tkr": "Teegala Krishna Reddy Engineering College",
    "tkrcet": "Teegala Krishna Reddy College of Engineering and Technology",
    "cse": "Computer Science and Engineering",
    "ece": "Electronics and Communication Engineering",
    "eee": "Electrical and Electronics Engineering",
    "it": "Information Technology",
    "mech": "Mechanical Engineering",
    "civil": "Civil Engineering",
    "ai": "Artificial Intelligence",
    "ml": "Machine Learning",
    "hod": "Head of Department",
    "lab": "Laboratory",
    "dept": "Department",
    "prof": "Professor",
    "asst": "Assistant",
    "assoc": "Associate"
}

def preprocess_query(query: str) -> str:
    """
    Preprocess the query with error handling.
    """
    try:
        if not isinstance(query, str):
            logger.warning(f"Invalid query type: {type(query)}. Converting to string.")
            query = str(query)
        
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Remove special characters except alphanumeric and basic punctuation
        query = re.sub(r'[^a-zA-Z0-9\s.,?!-]', ' ', query)
        
        return query
    except Exception as e:
        logger.error(f"Error in preprocess_query: {str(e)}")
        return query  # Return original query if processing fails

def detect_topics(query: str) -> List[str]:
    """
    Detect topics in the query with error handling.
    """
    try:
        query = preprocess_query(query)
        detected_topics = []
        
        for topic, patterns in TOPIC_PATTERNS.items():
            # Use flexible matching - pattern can appear anywhere in a word
            if any(re.search(pattern, query, re.IGNORECASE) for pattern in patterns):
                detected_topics.append(topic)
                
        return detected_topics
    except Exception as e:
        logger.error(f"Error in detect_topics: {str(e)}")
        return []

def expand_query(query: str, detected_topics: Optional[List[str]] = None) -> str:
    """
    Expand query with topic-specific terms and abbreviations.
    """
    try:
        if detected_topics is None:
            detected_topics = detect_topics(query)
            
        # Expand abbreviations
        expanded_query = query
        for abbr, full_form in ABBREVIATIONS.items():
            expanded_query = re.sub(r'\b' + re.escape(abbr) + r'\b', 
                                  f"{abbr} {full_form}", 
                                  expanded_query, 
                                  flags=re.IGNORECASE)
        
        # Add topic-specific terms
        topic_terms = []
        for topic in detected_topics:
            topic_terms.extend(TOPIC_PATTERNS.get(topic, []))
        
        if topic_terms:
            expanded_query = f"{expanded_query} {' '.join(topic_terms)}"
            
        return expanded_query
    except Exception as e:
        logger.error(f"Error in expand_query: {str(e)}")
        return query  # Return original query if expansion fails

def extract_key_phrases(query: str) -> List[str]:
    """
    Extract key phrases from the query.
    """
    try:
        query = preprocess_query(query)
        phrases = []
        
        # Extract quoted phrases
        quoted = re.findall(r'"([^"]*)"', query)
        if quoted:
            phrases.extend(quoted)
            
        # Extract noun phrases (simple heuristic)
        words = query.split()
        for i in range(len(words)):
            if i < len(words) - 1:
                # Two-word phrases
                phrase = f"{words[i]} {words[i+1]}"
                if any(topic in phrase for topic in TOPIC_PATTERNS.keys()):
                    phrases.append(phrase)
        
        return list(set(phrases))  # Remove duplicates
    except Exception as e:
        logger.error(f"Error in extract_key_phrases: {str(e)}")
        return []