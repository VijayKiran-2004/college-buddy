"""
Multi-Language Support for College Chatbot
Supports Telugu and Hindi translation
"""

from typing import Tuple


class Translator:
    """Simple translation system for Telugu and Hindi"""
    
    def __init__(self):
        """Initialize translator"""
        # Common Telugu keywords
        self.telugu_keywords = ['ఎవరు', 'ఏమిటి', 'ఎక్కడ', 'ఎప్పుడు', 'ఎలా', 'కాలేజీ', 'ప్రిన్సిపాల్']
        
        # Common Hindi keywords  
        self.hindi_keywords = ['कौन', 'क्या', 'कहाँ', 'कब', 'कैसे', 'कॉलेज', 'प्रिंसिपल']
        
        # Basic translation dictionaries (expandable)
        self.telugu_to_english = {
            'ప్రిన్సిపాల్ ఎవరు': 'who is the principal',
            'కాలేజీ ఎక్కడ ఉంది': 'where is the college',
            'ఫీజు ఎంత': 'what are the fees',
        }
        
        self.hindi_to_english = {
            'प्रिंसिपल कौन है': 'who is the principal',
            'कॉलेज कहाँ है': 'where is the college',
            'फीस कितनी है': 'what are the fees',
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        # Check for Telugu
        if any(char in text for char in self.telugu_keywords):
            return 'telugu'
        
        # Check for Hindi
        if any(char in text for char in self.hindi_keywords):
            return 'hindi'
        
        # Default to English
        return 'english'
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate query to English for processing"""
        if source_lang == 'telugu':
            # Check dictionary first
            for telugu, english in self.telugu_to_english.items():
                if telugu in text:
                    return english
            
            # Fallback: use Google Translate API or return as-is
            return text
        
        elif source_lang == 'hindi':
            # Check dictionary first
            for hindi, english in self.hindi_to_english.items():
                if hindi in text:
                    return english
            
            # Fallback: use Google Translate API or return as-is
            return text
        
        return text
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate response back to user's language"""
        if target_lang == 'english':
            return text
        
        # For now, return English with language note
        # In production, use Google Translate API or local model
        if target_lang == 'telugu':
            return f"[తెలుగు అనువాదం అందుబాటులో లేదు] {text}"
        elif target_lang == 'hindi':
            return f"[हिंदी अनुवाद उपलब्ध नहीं] {text}"
        
        return text
    
    def process_query(self, query: str) -> Tuple[str, str]:
        """
        Process query with language detection and translation
        Returns: (translated_query, detected_language)
        """
        lang = self.detect_language(query)
        
        if lang != 'english':
            translated = self.translate_to_english(query, lang)
            return translated, lang
        
        return query, 'english'
    
    def process_response(self, response: str, target_lang: str) -> str:
        """Translate response to user's language"""
        if target_lang == 'english':
            return response
        
        return self.translate_from_english(response, target_lang)


if __name__ == "__main__":
    # Test translator
    translator = Translator()
    
    # Test Telugu
    query_te = "ప్రిన్సిపాల్ ఎవరు"
    translated, lang = translator.process_query(query_te)
    print(f"Telugu: '{query_te}' → '{translated}' (detected: {lang})")
    
    # Test Hindi
    query_hi = "प्रिंसिपल कौन है"
    translated, lang = translator.process_query(query_hi)
    print(f"Hindi: '{query_hi}' → '{translated}' (detected: {lang})")
    
    # Test English
    query_en = "who is the principal"
    translated, lang = translator.process_query(query_en)
    print(f"English: '{query_en}' → '{translated}' (detected: {lang})")
