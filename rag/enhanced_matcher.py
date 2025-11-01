import csv
import re
import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
from rag.retriever import ABBREVIATION_MAP

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_FILE = 'data/scraped/scraped_data.json'

class RuleMatcher:
    def __init__(self, csv_path: Optional[str] = None):
        if not csv_path:
            csv_path = "data/links/structured_links.csv"
        self.csv_path = Path(csv_path).resolve()
        self.rules = self.load_rules()
        self.scraped_data = self.load_scraped_data()
        self.previous_context = None

    def load_rules(self) -> List[Dict]:
        """Load and parse rules from CSV file."""
        rules = []
        try:
            with open(self.csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # Skip header
                for row in reader:
                    if not row or len(row) < 2 or not any(row):
                        continue
                    link = row[0].strip()
                    page_name = row[1].strip()
                    if page_name and (link.startswith('http') or link.startswith('www')):
                        keywords = self._extract_keywords(page_name)
                        category = self._determine_category(page_name, link)
                        rule = {
                            "link": link,
                            "page_name": page_name,
                            "keywords": keywords,
                            "category": category
                        }
                        rules.append(rule)
                        logger.info(f"Loaded rule: {rule}")
            logger.info(f"Successfully loaded {len(rules)} rules")
            return rules
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return []

    def load_scraped_data(self) -> Dict[str, str]:
        """Load scraped data from cache file."""
        scraped_data = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    scraped_data[item['url']] = item['content']
        return scraped_data

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords with variations for better matching."""
        # A simpler regex to split by space, comma, slash, or hyphen
        base_keywords = [kw.strip() for kw in re.split(r'[\s/,-]+', text.lower()) 
                        if kw.strip() and len(kw.strip()) > 2]
        
        keywords = set(base_keywords)
        # Add the original text as a keyword, stripped of special characters
        keywords.add(re.sub(r'[^\w\s]', '', text.lower()))

        return list(keywords)

    def _determine_category(self, page_name: str, link: str) -> str:
        """Categorize content for better response formatting."""
        text = f"{page_name} {link}".lower()
        categories = {
            'academic': ['course', 'academic', 'faculty', 'department', 'syllabus'],
            'admission': ['admission', 'apply', 'entrance', 'eligibility'],
            'facilities': ['library', 'hostel', 'canteen', 'lab', 'facility'],
            'placement': ['placement', 'career', 'job', 'recruit'],
            'about': ['about', 'history', 'overview', 'vision', 'mission'],
            'contact': ['contact', 'location', 'address', 'reach'],
            'events': ['event', 'workshop', 'seminar', 'conference'],
            'finance': ['fee', 'finance', 'payment', 'tuition']
        }
        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def find_matches(self, question: str) -> List[Tuple[Dict, float, List[str]]]:
        """Find all matching rules with scores."""
        question_lower = question.lower()
        matches = []
        logger.info(f"Finding matches for question: {question_lower}")

        # Remove stop words to focus on meaningful keywords
        stop_words = {'a', 'an', 'the', 'is', 'are', 'in', 'of', 'what', 'r', 'tell', 'me', 'about', 'college', 'tkrcet'}
        question_keywords = {word for word in re.split(r'\W+', question_lower) if word not in stop_words and len(word) > 2}

        for rule in self.rules:
            score = 0
            matched_keywords = []

            # Keyword matching against the filtered question keywords
            for keyword in rule["keywords"]:
                if keyword in question_keywords:
                    score += 1
                    matched_keywords.append(keyword)

            # Content matching (remains the same)
            if rule['link'] in self.scraped_data:
                content = self.scraped_data[rule['link']].lower()
                if question_lower in content:
                    score += 5 # High score for direct match in content

            if matched_keywords:
                # Boost score for more matched keywords
                score += len(matched_keywords) * 1.5
                score += sum(len(kw) for kw in matched_keywords) / 10
                
                similarity = SequenceMatcher(None, question_lower, rule["page_name"].lower()).ratio()
                score += similarity * 2

                if self.previous_context and rule["category"] == self.previous_context["category"]:
                    score += 0.5
                
                if score > 0:
                    logger.info(f"Rule '{rule['page_name']}' matched with score {score} and keywords {matched_keywords}")
                    matches.append((rule, score, matched_keywords))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def get_answer(self, question: str) -> Tuple[str, Optional[str]]:
        """Get an enhanced answer with better context handling."""
        if not question:
            return "", None
            
        question_lower = question.lower()
        
        # Handle timing related queries
        if any(word in question_lower for word in ["timing", "schedule", "working hours", "college hours"]):
            response = ("The college working hours are from **9:40 AM to 4:20 PM** from Monday to Saturday. "
                      "The daily schedule is divided into periods:\n\n"
                      "- Morning Session: 9:40 AM - 1:10 PM\n"
                      "- Lunch Break: 1:10 PM - 1:50 PM\n"
                      "- Afternoon Session: 1:50 PM - 4:20 PM\n\n"
                      "Special activities like NPTEL/MOOCS, Library, and Sports are scheduled in the later hours.")
            return response, None
    
        # Handle full form queries
        if "full form" in question_lower or "fullform" in question_lower:
            for abbr, expansion in ABBREVIATION_MAP.items():
                if abbr in question_lower:
                    answer = f"The full form of {abbr.upper()} is **{expansion}**."
                    return answer, None
        
        # Handle regular queries
        matches = self.find_matches(question)
        if not matches:
            return ("", None)

        best_match = matches[0][0]
        category = best_match["category"]

        if best_match["page_name"] == "College Timings":
            response = f"The college buses arrive at 9:15 AM and depart at 4:50 PM. This suggests that the college timings are from 9:15 AM to 4:50 PM. For more details, you can check the transport page: {best_match['link']}"
            return response, best_match["link"]
        
        if best_match["page_name"] == "Scholarships and Financial Aid":
            response = f"For information about scholarships and fee reimbursement, you can contact Mr. Somi Reddy, the Scholarship In-charge, at 9949141962. You can also find more details on the contact page: {best_match['link']}"
            return response, best_match["link"]

        responses = {
            "academic": "This is related to academic information at TKRCET.",
            "admission": "This contains important admission-related details.",
            "facilities": "TKRCET provides this facility for students and staff.",
            "placement": "This is related to career opportunities and placements.",
            "about": "Here's some general information about TKRCET.",
            "contact": "You can find contact and location details here.",
            "events": "This is about events and activities at TKRCET.",
            "finance": "This is related to financial information, including fees."
        }
        
        base_response = responses.get(category, "Here's what I found")
        response = f"{base_response}\n\n**Regarding:** '{best_match['page_name']}'\n\nDetailed information can be found here: {best_match['link']}"
        
        self.previous_context = {
            "category": category,
            "page_name": best_match["page_name"],
            "link": best_match["link"]
        }
        
        return response, best_match["link"]

# Create a global instance
_matcher = RuleMatcher()

def get_answer(question: str) -> Tuple[str, Optional[str]]:
    """Get an answer to a question."""
    if not question:
        return "", None
    return _matcher.get_answer(question)

def get_answer_with_link(question: str) -> Tuple[str, Optional[str]]:
    """Get both the answer and source link."""
    if not question:
        return "", None
    return _matcher.get_answer(question)