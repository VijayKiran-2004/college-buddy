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
