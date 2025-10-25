"""
Lightweight typo correction for common mistakes in user queries.
Uses fuzzy matching and common college-related vocabulary.
"""

from difflib import get_close_matches
import re

# Common college-related vocabulary
COLLEGE_VOCAB = {
    # Academic terms
    'academic', 'admission', 'admissions', 'semester', 'examination', 'exam', 'exams',
    'timetable', 'timetables', 'schedule', 'syllabus', 'curriculum', 'course', 'courses',
    'department', 'departments', 'faculty', 'professor', 'teacher', 'instructor',
    'lecture', 'lectures', 'lab', 'laboratory', 'practical', 'theory',
    'results', 'marks', 'grades', 'cgpa', 'gpa', 'percentage', 'performance',
    'assignment', 'assignments', 'homework', 'project', 'projects',
    
    # Departments
    'cse', 'ece', 'eee', 'civil', 'mechanical', 'mech', 'it', 'information', 'technology',
    'computer', 'science', 'engineering', 'electronics', 'electrical', 'communication',
    'mba', 'management', 'business', 'administration', 'aiml', 'artificial', 'intelligence',
    'machine', 'learning', 'data', 'diploma',
    
    # Administrative
    'principal', 'hod', 'head', 'office', 'staff', 'administration', 'management',
    'registrar', 'dean', 'chairman', 'director',
    
    # Facilities
    'library', 'hostel', 'canteen', 'cafeteria', 'sports', 'gym', 'gymnasium',
    'auditorium', 'playground', 'transport', 'bus', 'parking', 'wifi', 'internet',
    'laboratory', 'workshop', 'seminar', 'hall', 'room', 'building',
    
    # Admissions & Fees
    'fees', 'fee', 'tuition', 'scholarship', 'payment', 'eligibility', 'criteria',
    'entrance', 'test', 'application', 'form', 'deadline', 'cutoff', 'reservation',
    'quota', 'seats', 'intake', 'capacity',
    
    # Placements
    'placement', 'placements', 'recruitment', 'job', 'jobs', 'company', 'companies',
    'package', 'salary', 'internship', 'interview', 'campus', 'drive', 'offer',
    
    # Time & Schedule
    'timing', 'timings', 'time', 'hours', 'duration', 'period', 'session',
    'morning', 'afternoon', 'evening', 'weekend', 'weekday', 'holiday', 'vacation',
    'calendar', 'date', 'schedule',
    
    # General
    'college', 'university', 'institute', 'institution', 'campus', 'location',
    'address', 'contact', 'phone', 'email', 'website', 'online', 'offline',
    'student', 'students', 'class', 'classes', 'year', 'batch',
    'first', 'second', 'third', 'fourth', 'year', 'final',
    'about', 'information', 'details', 'help', 'guide', 'procedure',
    
    # TKRCET specific
    'tkrcet', 'tkr', 'teegala', 'krishna', 'reddy', 'hyderabad', 'meerpet',
    'autonomous', 'affiliated', 'jntuh', 'naac', 'nirf', 'iqac', 'aqar',
}

# Common typo patterns (typo -> correct)
COMMON_TYPOS = {
    # Academic typos
    'acedamic': 'academic',
    'acadamic': 'academic',
    'academik': 'academic',
    'accademic': 'academic',
    'admision': 'admission',
    'addmission': 'admission',
    'admisson': 'admission',
    'examinaton': 'examination',
    'examenation': 'examination',
    'timetabe': 'timetable',
    'timtable': 'timetable',
    'scedule': 'schedule',
    'schedual': 'schedule',
    'shedulle': 'schedule',
    'sylabbus': 'syllabus',
    'silabus': 'syllabus',
    'sillabus': 'syllabus',
    
    # Department typos
    'computr': 'computer',
    'compter': 'computer',
    'engneering': 'engineering',
    'enginering': 'engineering',
    'enggineering': 'engineering',
    'tecnology': 'technology',
    'techology': 'technology',
    'infomation': 'information',
    'informaton': 'information',
    'electonics': 'electronics',
    'elektronics': 'electronics',
    'comunication': 'communication',
    'comunications': 'communication',
    'machenical': 'mechanical',
    'mecanical': 'mechanical',
    
    # Facilities typos
    'libary': 'library',
    'librery': 'library',
    'labortory': 'laboratory',
    'laborotory': 'laboratory',
    'cantin': 'canteen',
    'cafateria': 'cafeteria',
    'auditoreum': 'auditorium',
    'auditorum': 'auditorium',
    
    # Common words
    'recieve': 'receive',
    'beleive': 'believe',
    'wiht': 'with',
    'teh': 'the',
    'adn': 'and',
    'taht': 'that',
    'thier': 'their',
    'wich': 'which',
    'wat': 'what',
    'whn': 'when',
    'whre': 'where',
    'hwo': 'how',
    'hw': 'how',
    'y': 'why',
    'u': 'you',
    'ur': 'your',
    'r': 'are',
    
    # Timing related
    'timeing': 'timing',
    'timigs': 'timings',
    'timng': 'timing',
    'schdule': 'schedule',
}

def correct_word(word: str) -> str:
    """
    Correct a single word using typo dictionary and fuzzy matching.
    
    Args:
        word: The word to correct (lowercase)
        
    Returns:
        Corrected word or original if no correction found
    """
    # Check direct typo mapping first
    if word in COMMON_TYPOS:
        return COMMON_TYPOS[word]
    
    # If word is already correct, return it
    if word in COLLEGE_VOCAB:
        return word
    
    # Try fuzzy matching with vocabulary (only if word is close enough)
    if len(word) >= 4:  # Only match words with 4+ characters
        matches = get_close_matches(word, COLLEGE_VOCAB, n=1, cutoff=0.8)
        if matches:
            return matches[0]
    
    # Return original word if no correction found
    return word

def correct_typos(text: str) -> tuple[str, bool]:
    """
    Correct typos in the entire text while preserving structure.
    
    Args:
        text: The input text to correct
        
    Returns:
        Tuple of (corrected_text, was_corrected)
    """
    if not text or len(text.strip()) == 0:
        return text, False
    
    # Preserve original for comparison
    original_text = text
    
    # Split into words while preserving punctuation and spaces
    words = re.findall(r'\b\w+\b|\W+', text)
    
    corrected_words = []
    was_corrected = False
    
    for word in words:
        # Only process actual words (not punctuation/spaces)
        if re.match(r'\b\w+\b', word):
            original_word = word
            lower_word = word.lower()
            
            # Correct the lowercase version
            corrected_lower = correct_word(lower_word)
            
            # Preserve original capitalization
            if corrected_lower != lower_word:
                was_corrected = True
                if word[0].isupper():
                    corrected_word = corrected_lower.capitalize()
                else:
                    corrected_word = corrected_lower
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(original_word)
        else:
            # Keep punctuation and spaces as-is
            corrected_words.append(word)
    
    corrected_text = ''.join(corrected_words)
    
    return corrected_text, was_corrected

def get_correction_message(original: str, corrected: str) -> str:
    """
    Generate a friendly message showing the correction.
    
    Args:
        original: Original text with typos
        corrected: Corrected text
        
    Returns:
        Message string or empty if no correction
    """
    if original.lower().strip() != corrected.lower().strip():
        return f"💡 I understood your question as: *{corrected}*"
    return ""

# Example usage and testing
if __name__ == "__main__":
    test_queries = [
        "acedamic timings?",
        "What is the admision procedure?",
        "Tell me about computr science engneering",
        "timtable for CSE",
        "libary timings",
        "What are the correct timings?",  # No typos
        "hwo to apply for admisson",
        "wat is the fees structure",
    ]
    
    print("Typo Correction Examples:\n")
    for query in test_queries:
        corrected, was_corrected = correct_typos(query)
        if was_corrected:
            print(f"Original:  {query}")
            print(f"Corrected: {corrected}")
            print(f"Message:   {get_correction_message(query, corrected)}")
            print()
        else:
            print(f"No typos:  {query}\n")
