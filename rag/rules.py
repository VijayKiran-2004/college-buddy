"""
SIMPLIFIED RULES SYSTEM
Only handles greetings and gratitude - ALL other questions go to RAG system
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# MINIMAL CONVERSATIONAL RULES - Only greetings and thanks
CONVERSATIONAL_RULES = [
    {
        "pattern": r"^(hi|hello|hey|namaste|good morning|good afternoon|good evening)$",
        "answer": "Hello! I'm College Buddy. How can I help you with information about TKRCET today?"
    },
    {
        "pattern": r"^(thank you|thanks|thank u|ty|tysm)$",
        "answer": "You're welcome! Let me know if you need anything else."
    },
    {
        "pattern": r"^(bye|goodbye|see you|cya|exit|quit)$",
        "answer": "Goodbye! Feel free to come back anytime you have questions about TKRCET."
    },
    {
        "pattern": r"(list of|all) (hod|hods|head of department|heads of department)",
        "answer": """Here are all the **Heads of Departments (HODs)** at TKRCET:

**Engineering Departments:**
• **Civil Engineering** - Dr. K. Satya Sai | 📞 8498085212 | 📧 civil@tkrcet.com
• **Electrical & Electronics (EEE)** - Dr. K. Raju | 📞 8498085213 | 📧 eee@tkrcet.com  
• **Mechanical Engineering** - Mr. D Rushi Kumar Reddy | 📞 8498085214 | 📧 mech@tkrcet.com
• **Electronics & Communication (ECE)** - Dr. M. Mahesh | 📞 8498085215 | 📧 ece@tkrcet.com
• **Computer Science (CSE)** - Dr. A. Suresh Rao | 📞 8498085216 | 📧 cse@tkrcet.com
• **CSE (AI & ML)** - Dr. B. Sunil Srinivas | 📞 8498993377 | 📧 csm@tkrcet.com
• **CSE (Data Science)** - Dr. V. Krishna | 📞 9100377791 | 📧 csd@tkrcet.com
• **Information Technology (IT)** - Dr. N. Satya Narayana | 📞 8498085217 | 📧 it@tkrcet.com

**Other Departments:**
• **MBA** - Dr. K. Gyaneshwari | 📞 8886878546
• **Humanities & Sciences** - Dr. D.V.S.R. Anil Kumar | 📞 8498085221 | 📧 anilkumar@tkrcet.com

[View Contact Information →](https://tkrcet.ac.in/contact-us/)"""
    }
]

# Stop words for cleaning user questions
STOP_WORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'can', 'may', 'might', 'must', 'of', 'in', 'on', 'at', 'to',
    'for', 'with', 'by', 'from', 'about', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'me', 'my', 'tell', 'give', 'please',
    'want', 'know', 'need', 'get', 'show'
}


def find_conversational_rule(question: str) -> Optional[str]:
    """
    Check if question matches any minimal conversational rule (greetings/thanks only).
    Returns answer if matched, None otherwise (let RAG handle it).
    """
    if not question:
        return None
    
    # Normalize question
    question_lower = question.lower().strip()
    
    # Remove punctuation from the end
    question_lower = re.sub(r'[?!.]+$', '', question_lower).strip()
    
    # Check each rule
    for rule in CONVERSATIONAL_RULES:
        if re.search(rule["pattern"], question_lower, re.IGNORECASE):
            logger.info(f"Matched conversational rule: {rule['pattern']}")
            # Return raw answer - will be enhanced by Gemini later
            return rule["answer"]
    
    # No match - let RAG system handle this question
    logger.info(f"No conversational rule matched. Sending to RAG: '{question}'")
    return None


def clean_question(question: str) -> str:
    """
    Clean and normalize user question for better matching.
    Removes stop words and normalizes spacing.
    """
    # Convert to lowercase
    question = question.lower().strip()
    
    # Remove punctuation
    question = re.sub(r'[^\w\s]', ' ', question)
    
    # Split into words
    words = question.split()
    
    # Remove stop words
    filtered_words = [w for w in words if w not in STOP_WORDS]
    
    # Return cleaned question
    return ' '.join(filtered_words) if filtered_words else question


# Export what's needed
__all__ = ['find_conversational_rule', 'clean_question', 'CONVERSATIONAL_RULES']
