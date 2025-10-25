import os
import logging
import json
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup
from rag.retriever import get_docs
from rag.text_processor import preprocess_query, detect_topics
from rag.rules import find_conversational_rule
from dotenv import load_dotenv
import time

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ChainException(Exception):
    """Custom exception for chain-related errors."""
    pass

def generate_clarification_question(question: str, docs: List[Document], history: Optional[list] = None) -> Optional[str]:
    """Generate a clarification question if the query is ambiguous."""
    if not model or len(docs) < 3:
        return None

    context = "\n".join([d.page_content for d in docs])
    history_context = ""
    if history:
        for item in history:
            role = item.get("role")
            parts = item.get("parts")
            if role and parts:
                history_context += f"{role.capitalize()}: {parts[0]}\n"

    prompt = f"""You are a helpful assistant for a college chatbot. Your task is to analyze a user's query, the conversation history, and the retrieved information to determine if a clarifying question is needed.

**Crucially, if the user's latest message seems to be an answer to your previous clarification question, you should not ask another one.**

A clarifying question is needed ONLY if:
- The user's query is very broad and this is the first time they are asking about it (e.g., "tell me about the college").
- The retrieved information contains multiple, very distinct topics that could all be valid answers.

Conversation History:
{history_context}

User's Query: "{question}"

Retrieved Information:
{context}

Based on the above, is a clarifying question absolutely necessary? If the user is already trying to narrow down their query, do not ask another question. If a clarifying question is not needed, respond with "No clarification needed.". Otherwise, generate a concise and friendly question with clear options."""

    try:
        response = model(prompt)
        if response and "no clarification needed" not in response.lower():
            return response
    except Exception as e:
        logger.error(f"Error generating clarification question: {e}")
    
    return None

def extract_faculty_info(docs: List[Document]) -> Dict[str, List[Dict[str, str]]]:
    """Extract and organize faculty information from documents."""
    faculty_info = {
        'hods': [],
        'deans': [],
        'principal': [],
        'other_leaders': []
    }
    
    def clean_info(text: str) -> Dict[str, str]:
        """Extract name and designation from text."""
        text = text.strip()
        parts = [p.strip() for p in text.split('|') if p.strip()]
        if not parts:
            parts = [p.strip() for p in text.split('-') if p.strip()]
        
        info = {'full_text': text}
        for part in parts:
            if 'name' not in info and any(n in part.lower() for n in ['dr.', 'mr.', 'mrs.', 'ms.', 'prof']):
                info['name'] = part.strip()
            elif 'role' not in info and any(r in part.lower() for r in ['hod', 'head', 'dean', 'principal', 'director', 'controller']):
                info['role'] = part.strip()
            elif 'department' not in info and any(d in part.lower() for d in ['cse', 'ece', 'eee', 'mech', 'civil', 'it', 'mba']):
                info['department'] = part.strip()
        return info
    
    for doc in docs:
        content = doc.page_content.split('\n')
        for line in content:
            line_lower = line.lower()
            info = clean_info(line)
            
            if 'hod' in line_lower or 'head of' in line_lower:
                if info not in faculty_info['hods']:
                    faculty_info['hods'].append(info)
            elif 'dean' in line_lower:
                if info not in faculty_info['deans']:
                    faculty_info['deans'].append(info)
            elif 'principal' in line_lower:
                if info not in faculty_info['principal']:
                    faculty_info['principal'].append(info)
            elif any(role in line_lower for role in ['vice', 'director', 'controller']):
                if info not in faculty_info['other_leaders']:
                    faculty_info['other_leaders'].append(info)
    
    return faculty_info

def log_interaction(query: str, response: str, error: Optional[str] = None):
    """Log user interactions and system responses."""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "error": error,
            "topics": detect_topics(query)
        }
        logger.info(f"Interaction: {json.dumps(log_entry, indent=2)}")
    except Exception as e:
        logger.error(f"Failed to log interaction: {str(e)}")

load_dotenv()

# Load and configure API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found. Will use local model only.")

# Model configuration
USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "gemma3:4b")
LOCAL_MODEL_TIMEOUT = int(os.getenv("LOCAL_MODEL_TIMEOUT", "15"))  # seconds

# Initialize local model (Ollama)
local_model = None
if USE_LOCAL_MODEL:
    try:
        # Test Ollama connection
        test_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if test_response.status_code == 200:
            logger.info(f"✅ Ollama connected at {OLLAMA_BASE_URL}")
            
            def generate_with_ollama(prompt: str, timeout: int = LOCAL_MODEL_TIMEOUT) -> Optional[str]:
                """Generate text using local Ollama model with timeout."""
                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{OLLAMA_BASE_URL}/api/generate",
                        json={
                            "model": LOCAL_MODEL_NAME,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.7,
                                "top_p": 0.9,
                                "num_predict": 512
                            }
                        },
                        timeout=timeout
                    )
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json().get("response", "")
                        logger.info(f"🟢 Ollama response in {elapsed:.1f}s")
                        return result
                    else:
                        logger.error(f"Ollama error: {response.status_code}")
                        return None
                except requests.Timeout:
                    logger.warning(f"⏱️ Ollama timeout after {timeout}s")
                    return None
                except Exception as e:
                    logger.error(f"Ollama generation error: {e}")
                    return None
            
            local_model = generate_with_ollama
            logger.info(f"✅ Local model ready: {LOCAL_MODEL_NAME}")
        else:
            logger.warning("❌ Ollama not responding")
    except Exception as e:
        logger.warning(f"⚠️ Ollama not available: {e}")

# Initialize Gemini model (fallback)
gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        from google.generativeai.generative_models import GenerativeModel
        from google.generativeai.client import configure
        
        # Set up environment
        os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
        configure(api_key=GEMINI_API_KEY)
        
        # Create a function to handle text generation
        def generate_with_gemini(prompt: str) -> Optional[str]:
            try:
                model_instance = GenerativeModel('gemini-2.5-flash')
                response = model_instance.generate_content(prompt)
                logger.info("🔵 Gemini response")
                return response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                logger.error(f"Gemini generation error: {e}")
                return None
        
        # Skip test - Gemini will be tested on first actual use
        gemini_model = generate_with_gemini
        logger.info("✅ Gemini fallback ready (will test on first use)")
    except Exception as e:
        logger.warning(f"⚠️ Gemini not available: {e}")

# Hybrid model function
def generate_text(prompt: str) -> Optional[str]:
    """Generate text using hybrid approach: Local (Ollama) → Gemini fallback."""
    
    # Try local model first
    if local_model:
        response = local_model(prompt)
        if response and len(response.strip()) > 20:  # Valid response check
            return response
        logger.warning("⚠️ Local model failed or returned poor response")
    
    # Fallback to Gemini
    if gemini_model:
        logger.info("↪️ Using Gemini fallback")
        return gemini_model(prompt)
    
    # No models available
    logger.error("❌ No models available!")
    return None

# Set model reference for compatibility
model = generate_text if (local_model or gemini_model) else None

if not model:
    logger.error("❌ CRITICAL: No LLM models available! Install Ollama or set GEMINI_API_KEY.")

def enhance_response_for_students(response: str, question: str) -> str:
    """
    Enhance any response (rule-based or RAG) to be more friendly and natural for students.
    Makes the language conversational, warm, and easy to understand.
    """
    if not gemini_model:
        # If no Gemini available, return original response
        return response
    
    try:
        enhancement_prompt = f"""You are a friendly college chatbot assistant helping students. Your job is to rewrite the following response to make it more natural, warm, and student-friendly.

**Guidelines:**
1. Use casual, friendly language (like talking to a friend)
2. Add encouraging words and helpful suggestions
3. Keep all important information (dates, names, links)
4. Preserve all hyperlinks in markdown format [text](url)
5. Use emojis sparingly (1-2 max) for warmth
6. Keep it concise (3-5 sentences or 4-6 bullet points)
7. Sound excited to help!

**Student's Question:** {question}

**Original Response:**
{response}

**Your Enhanced Response (friendly, natural, student-focused):**"""

        enhanced = gemini_model(enhancement_prompt)
        
        if enhanced and len(enhanced.strip()) > 20:
            # Ensure no HTML tags slipped through
            enhanced = re.sub(r'<[^>]+>', '', enhanced)
            logger.info("✨ Response enhanced for student-friendly tone")
            return enhanced.strip()
        else:
            return response
            
    except Exception as e:
        logger.warning(f"⚠️ Could not enhance response: {e}")
        return response

# Basic definitions
BASIC_DEFINITIONS = {
    "tkr": "**TKR** stands for **Teegala Krishna Reddy**. The full name of our institution is **Teegala Krishna Reddy Engineering College (TKRCET)**.",
    "tkrcet": "**TKRCET** stands for **Teegala Krishna Reddy College of Engineering and Technology**.",
    "courses": """TKRCET offers the following engineering courses:

1. **B.Tech Programs**:
   - Computer Science Engineering (CSE)
   - Electronics and Communication Engineering (ECE)
   - Electrical and Electronics Engineering (EEE)
   - Mechanical Engineering
   - Civil Engineering
   - Information Technology (IT)
   - CSE with AI & ML specialization
   - Computer Science and Design (CSD)

2. **Post Graduate Programs**:
   - Master of Business Administration (MBA)

3. **Diploma Programs** are also available."""
}

# Updated system prompt for better relevance checking
SYSTEM_PROMPT_TEMPLATE = """You are College Buddy, an intelligent assistant for Teegala Krishna Reddy College of Engineering and Technology (TKRCET).

IMPORTANT: For questions about college timings, class schedule, bus timings, or operating hours:
- The college operates from 4:20 AM to 9:40 PM
- Classes run from 9:40 AM to 4:20 PM (7 periods)
- **ALWAYS LIST ALL 7 PERIODS INDIVIDUALLY** when asked about class timings or schedule:
  Period 1: 9:40 - 10:30 AM
  Period 2: 10:30 - 11:20 AM
  Short Break: 11:20 - 11:30 AM
  Period 3: 11:30 AM - 12:20 PM
  Period 4: 12:20 - 1:10 PM
  Lunch Break: 1:10 - 1:50 PM
  Period 5: 1:50 - 2:40 PM
  Period 6: 2:40 - 3:30 PM
  Period 7: 3:30 - 4:20 PM
- Buses arrive by 9:15 AM and depart at 4:50 PM
- DO NOT summarize periods (e.g., "Period 1 begins...Period 7 ends"). List each period with its time.

CRITICAL FORMATTING RULES:
1. **Be Concise**: Maximum 3-4 sentences OR 4-5 bullet points. No long paragraphs.
   **EXCEPTION**: For timing/schedule questions, you may use up to 12 bullet points to list all periods.
2. **Use ONLY Markdown Format** - NEVER use HTML tags:
   - ✅ Correct: **Dr. A. Suresh Rao** (markdown bold)
   - ❌ Wrong: <strong>Dr. A. Suresh Rao</strong> (HTML)
   - ✅ Correct: [Read more →](URL) (markdown link)
   - ❌ Wrong: <a href="URL">Read more</a> (HTML)
   - ✅ Correct: • Item text (bullet with •, *, or -)
   - ❌ Wrong: <li>Item text</li> (HTML)
3. **Structure Your Response**:
   - Start with a direct answer (1-2 sentences)
   - Follow with bullet points (• or * or -) for lists
   - Use **bold** (double asterisks) for important names, numbers, dates
   - End with ONE clean hyperlink: [Read more about XYZ →](URL)
4. **Skip Unnecessary Phrases**: Don't use "According to the context" or "Based on the information"
5. **Be Specific**: Use actual names, numbers, dates instead of general statements

Answer in {lang} language only.
"""

def answer_from_rule(rule: dict, question: str) -> str:
    """
    Generates a detailed answer from a matched rule by fetching and summarizing its web content.
    """
    try:
        print(f"Found matching rule: {rule['page_name']}. Fetching content from {rule['link']}...")
        # Fetch web content using requests
        response = requests.get(rule['link'], timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse HTML and extract text using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get text from main content areas, fallback to all paragraphs
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            text_content = ' '.join(p.get_text() for p in main_content.find_all('p'))
        else:
            text_content = ' '.join(p.get_text() for p in soup.find_all('p'))

        if not text_content.strip():
            # Fallback if no content is found
            return f"I found a potentially relevant page for **{rule['page_name']}**, but I couldn't extract any readable text. You can visit it here: {rule['link']}"

        # Use the generative model to create a nice summary from the page content
        summary_prompt = f"""A user asked: '{question}'.
You have found a relevant page titled '{rule['page_name']}'.
Here is the text content from that page:
---
{text_content[:4000]}
---
Based ONLY on the text content above, provide a helpful summary that directly answers the user's question.
Use markdown for formatting (e.g., bolding, lists)."""
        
        try:
            if model:
                try:
                    response = model("Generate a concise summary: " + summary_prompt)
                    if response:
                        return f"Here's what I found about **{rule['page_name']}**:\n\n{response}\n\nSource: {rule['link']}"
                except Exception as e:
                    logger.error(f"Failed to generate summary: {e}")
            
            # Fallback to basic response
            return f"You can find information about **{rule['page_name']}** here: {rule['link']}"
        except Exception as e:
            print(f"[ERROR] Failed to generate summary: {str(e)}")
            
        return f"I found information about **{rule['page_name']}** but couldn't generate a summary. You can visit: {rule['link']}"

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch URL for rule: {e}")
        return f"I found a page for **{rule['page_name']}**, but I was unable to access it. You can try the link directly: {rule['link']}"
    except Exception as e:
        print(f"[ERROR] Failed to generate answer from rule: {e}")
        # Fallback to a simple response if anything else goes wrong
        return f"I found this page about **{rule['page_name']}**. You can find more information here: {rule['link']}"

def format_faculty_entry(entry: Dict[str, str]) -> str:
    """Format a single faculty entry."""
    if not entry:
        return ""
    
    parts = []
    if 'name' in entry:
        parts.append(f"**{entry['name']}**")
    if 'role' in entry:
        parts.append(entry['role'])
    if 'department' in entry:
        parts.append(f"({entry['department']})")
    
    return " - ".join(parts) if parts else entry.get('full_text', '')

def combine_documents(docs: List[Document], question: str) -> str:
    """
    Intelligently combines information from multiple documents based on relevance.
    """
    context_parts = []
    seen_urls = set()
    question_lower = question.lower()
    
    # Handle basic greeting queries
    greeting_responses = {
        "hi": "Hello! I'm College-Buddy, here to help you with information about TKRCET. You can ask me about courses, admissions, faculty, facilities, and more.",
        "hello": "Hi! I'm College-Buddy, your guide to TKRCET. Feel free to ask about any aspect of the college!",
        "how are you": "I'm doing well and ready to help you with information about TKRCET! What would you like to know?",
        "who are you": "I'm College-Buddy, an AI assistant designed to help you with information about TKRCET (Teegala Krishna Reddy College of Engineering and Technology). I can answer questions about courses, admissions, faculty, facilities, and more!"
    }
    
    # Check for greetings first
    for greeting in greeting_responses:
        if question_lower.strip("?!. ") == greeting:
            return greeting_responses[greeting]
    
    # Identify query type
    is_faculty_query = any(word in question_lower for word in ["faculty", "professor", "teacher", "staff"])
    is_timing_query = any(word in question_lower for word in ["timing", "schedule", "hours", "time", "working"])
    is_leadership_query = any(word in question_lower for word in ["chairman", "director", "principal", "dean", "head", "hod"])
    is_college_query = any(word in question_lower for word in ["about college", "tell me about", "college info", "tkr", "tkrcet"])
    
    # Group documents by source/URL
    url_groups = {}
    faculty_info = []
    
    for doc in docs:
        url = doc.metadata.get("source", "")
        if url not in url_groups:
            url_groups[url] = []
        url_groups[url].append(doc)
        
        # Extract faculty information if relevant
        if is_faculty_query:
            content = doc.page_content
            for line in content.split('\n'):
                if any(title in line.upper() for title in ["PROFESSOR", "FACULTY", "TEACHER", "HOD", "DEAN", "DIRECTOR"]):
                    faculty_info.append(line.strip())
    
    # Process documents based on query type
    if is_timing_query:
        # Extract timing information
        timing_info = []
        schedule_info = []
        
        for doc in docs:
            content = doc.page_content
            lines = content.split('\n')
            current_section = []
            
            for line in lines:
                # Look for time patterns
                if any(timing_word in line.lower() for timing_word in ["am", "pm", "hours", "timing", "-", ":"]):
                    # Skip lines that are just dashes or too short
                    if len(line.strip('-: \t')) > 3:
                        current_section.append(line.strip())
                # If we hit an empty line and have collected timing info, store it
                elif line.strip() == "" and current_section:
                    if any(":" in line for line in current_section):
                        timing_info.extend(current_section)
                    else:
                        schedule_info.extend(current_section)
                    current_section = []
            
            # Handle any remaining section
            if current_section:
                if any(":" in line for line in current_section):
                    timing_info.extend(current_section)
                else:
                    schedule_info.extend(current_section)
        
        # Format the timing information
        if timing_info:
            context_parts.append("**College Working Hours:**\n" + "\n".join(sorted(set(timing_info))))
        if schedule_info:
            context_parts.append("**Daily Schedule:**\n" + "\n".join(schedule_info))
                    
    elif is_leadership_query:
        # Extract leadership information
        leadership_info = []
        for doc in docs:
            content = doc.page_content
            lines = content.split('\n')
            for line in lines:
                if any(role in line.upper() for role in ["CHAIRMAN", "DIRECTOR", "PRINCIPAL", "DEAN", "HEAD", "TREASURER"]):
                    if not any(skip in line.upper() for skip in ["ASSISTANT", "LIST", "TABLE"]):
                        leadership_info.append(line.strip())
        if leadership_info:
            context_parts.append("**College Leadership:**\n" + "\n".join(set(leadership_info)))
            
    elif is_college_query:
        # Extract college overview information
        college_info = []
        for doc in docs:
            content = doc.page_content
            if "TKRCET" in content or "TKR" in content:
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if len(para.split()) > 10 and ("college" in para.lower() or "institution" in para.lower()):
                        college_info.append(para.strip())
        if college_info:
            context_parts.append("**About TKRCET:**\n" + "\n\n".join(set(college_info)))
            
    elif is_faculty_query:
        # Extract and organize faculty information
        faculty_info = []
        for doc in docs:
            content = doc.page_content
            for line in content.split('\n'):
                if any(title in line.upper() for title in ["PROFESSOR", "FACULTY", "TEACHER", "HOD", "DEAN", "DIRECTOR"]):
                    faculty_info.append(line.strip())
                    
        if faculty_info:
            # Group by roles
            leadership = []
            professors = []
            associate_profs = []
            assistant_profs = []
            others = []
            
            for info in set(faculty_info):  # Remove duplicates
                if "DEAN" in info.upper() or "DIRECTOR" in info.upper() or "PRINCIPAL" in info.upper():
                    leadership.append(info)
                elif "PROFESSOR" in info.upper() and "ASSOCIATE" not in info.upper() and "ASSISTANT" not in info.upper():
                    professors.append(info)
                elif "ASSOCIATE PROFESSOR" in info.upper():
                    associate_profs.append(info)
                elif "ASSISTANT PROFESSOR" in info.upper():
                    assistant_profs.append(info)
                else:
                    others.append(info)
            
            faculty_summary = []
            if leadership: faculty_summary.append("**Leadership:**\n" + "\n".join(sorted(leadership)))
            if professors: faculty_summary.append("**Professors:**\n" + "\n".join(sorted(professors)))
            if associate_profs: faculty_summary.append("**Associate Professors:**\n" + "\n".join(sorted(associate_profs)))
            if assistant_profs: faculty_summary.append("**Assistant Professors:**\n" + "\n".join(sorted(assistant_profs)))
            if others: faculty_summary.append("**Other Faculty Members:**\n" + "\n".join(sorted(others)))
            
            context_parts.append("\n\n".join(faculty_summary))
    
    else:
        # Default processing for other queries
        for url, url_docs in url_groups.items():
            content = "\n".join(d.page_content for d in url_docs)
            title = url_docs[0].metadata.get("title", "Untitled")
            if url and url not in seen_urls:
                context_parts.append(f"Information from {title}:\n{content}")
                seen_urls.add(url)
    
    return "\n\n---\n\n".join(context_parts)


def handle_error_response(error_type: str) -> str:
    """Generate appropriate error responses."""
    error_responses = {
        "no_context": (
            "I apologize, but I couldn't find relevant information to answer your question. "
            "Please try:\n"
            "1. Rephrasing your question\n"
            "2. Being more specific\n"
            "3. Asking about a different topic"
        ),
        "model_error": (
            "I encountered an issue while processing your question. "
            "Please try again with a simpler query or contact support if the issue persists."
        ),
        "general_error": (
            "I apologize, but something went wrong while processing your request. "
            "Please try again in a moment."
        )
    }
    return error_responses.get(error_type, error_responses["general_error"])

def format_faculty_response(faculty_info: Dict[str, List[Dict[str, str]]], query_type: str = 'all') -> str:
    """Format faculty information into a readable response."""
    response_parts = []
    
    def format_section(title: str, entries: List[Dict[str, str]]) -> str:
        if not entries:
            return ""
        formatted = [f"### {title}"]
        for entry in entries:
            formatted.append(f"- {format_faculty_entry(entry)}")
        return "\n".join(formatted)
    
    if query_type == 'principal' or query_type == 'all':
        if faculty_info['principal']:
            response_parts.append(format_section("Principal", faculty_info['principal']))
            
    if query_type == 'deans' or query_type == 'all':
        if faculty_info['deans']:
            response_parts.append(format_section("Deans", faculty_info['deans']))
            
    if query_type == 'hods' or query_type == 'all':
        if faculty_info['hods']:
            response_parts.append(format_section("Heads of Departments", faculty_info['hods']))
            
    if query_type == 'other' or query_type == 'all':
        if faculty_info['other_leaders']:
            response_parts.append(format_section("Other Academic Leaders", faculty_info['other_leaders']))
    
    if not response_parts:
        return "I apologize, but I couldn't find any specific faculty information matching your query."
        
    return "\n\n".join(response_parts)

def rag_answer(question: str, history: Optional[list] = None, lang: str = "english") -> dict:
    """
    Generate an answer using RAG (Retrieval Augmented Generation).
    
    Args:
        question (str): The user's question
        history (list): Optional conversation history
        lang (str): Language to respond in
        
    Returns:
        dict: A dictionary with 'answer' (str) and 'sources' (list) keys
    """
    try:
        # Handle numbered responses to clarification questions
        if question.strip().isdigit() and history and history[-1].get("role") == "model":
            last_bot_response = history[-1].get("parts", [""])[0]
            options = re.findall(r"^\d+\.\s+(.*)", last_bot_response, re.MULTILINE)
            if options:
                try:
                    choice_index = int(question.strip()) - 1
                    if 0 <= choice_index < len(options):
                        question = options[choice_index]
                except (ValueError, IndexError):
                    pass # Not a valid choice, treat as a regular query

        # Input validation
        if not isinstance(question, str) or not question.strip():
            error_msg = "Question must be a non-empty string"
            error_response = f"I apologize, but {error_msg}. Please try again."
            log_interaction(question, error_response, error_msg)
            return {"answer": error_response, "sources": []}
        if lang is not None and (not isinstance(lang, str) or not lang.strip()):
            error_msg = "Language must be a non-empty string when provided"
            error_response = f"I apologize, but {error_msg}. Please try again."
            log_interaction(question, error_response, error_msg)
            return {"answer": error_response, "sources": []}
        if history is not None and not isinstance(history, list):
            error_msg = "History must be a list when provided"
            error_response = f"I apologize, but {error_msg}. Please try again."
            log_interaction(question, error_response, error_msg)
            return error_response

        # Process the question
        processed_question = preprocess_query(question)
        question_lower = processed_question.strip(" ?!.")

        # Check conversational rules first (for placement, contact, etc.)
        conversational_answer = find_conversational_rule(question_lower)
        if conversational_answer:
            log_interaction(question, conversational_answer)
            return {"answer": conversational_answer, "sources": []}

        # Check for basic definitions first
        if any(phrase in question_lower for phrase in [
            "what courses", "which courses", "courses available",
            "what branches", "which branches", "branches available",
            "what programs", "which programs", "programs available",
            "courses offered", "branches offered", "programs offered"
        ]):
            response = BASIC_DEFINITIONS["courses"]
            # Enhance response for student-friendly tone
            response = enhance_response_for_students(response, question)
            log_interaction(question, response)
            return {"answer": response, "sources": []}

        # Check for full form questions
        for key, definition in BASIC_DEFINITIONS.items():
            if any(pattern in question_lower for pattern in [
                f"{key} full form",
                f"{key} fullform",
                f"{key} full name",
                f"what is {key}",
                f"{key} means",
                f"what does {key} mean",
                f"what's {key}",
                f"what {key} stands for"
            ]):
                # Enhance response for student-friendly tone
                definition = enhance_response_for_students(definition, question)
                log_interaction(question, definition)
                return {"answer": definition, "sources": []}

        # Get relevant documents
        try:
            source_docs = get_docs(question, history, k=10)

            if not source_docs:
                # Get detected topics for better error handling
                topics = detect_topics(question_lower)
                logger.info(f"No documents found for topics: {topics}")

                # Topic-specific guidance
                topic_responses = {
                    "fee": (
                        "I apologize, but I couldn't find the current fee details. Please:\n"
                        "1. Visit the college admission office\n"
                        "2. Check the college website's admission section\n"
                        "3. Contact the administrative office for the latest fee structure"
                    ),
                    "faculty": (
                        "I apologize, but I couldn't find the faculty information you're looking for. Please:\n"
                        "1. Visit the specific department's page on our website\n"
                        "2. Contact the department office directly\n"
                        "3. Check the college directory for contact details"
                    ),
                    "timing": (
                        "I apologize, but I couldn't find the current timing information. Please:\n"
                        "1. Contact the college office\n"
                        "2. Check the college website\n"
                        "3. Refer to your department notice board"
                    ),
                    "admission": (
                        "I apologize, but I couldn't find the admission information you're looking for. Please:\n"
                        "1. Visit the admissions office\n"
                        "2. Check the college website's admission section\n"
                        "3. Contact the administrative office"
                    ),
                    "facility": (
                        "I apologize, but I couldn't find specific facility information. Please:\n"
                        "1. Visit the relevant department\n"
                        "2. Check the college website\n"
                        "3. Contact the administrative office"
                    )
                }

                # Find matching topic response
                for topic in topics:
                    if topic in topic_responses:
                        response = topic_responses[topic]
                        log_interaction(question, response)
                        return {"answer": response, "sources": []}
                
                # Default response if no specific topic found
                response = handle_error_response("no_context")
                log_interaction(question, response)
                return {"answer": response, "sources": []}

        except Exception as retrieve_error:
            logger.error(f"Error retrieving documents: {str(retrieve_error)}")
            response = handle_error_response("general_error")
            log_interaction(question, response, str(retrieve_error))
            return {"answer": response, "sources": []}

        # Generate a clarification question if needed
        clarification = generate_clarification_question(question, source_docs, history)
        if clarification:
            log_interaction(question, clarification, "Clarification needed")
            return {"answer": clarification, "sources": []}

        # Extract source information
        sources = []
        for doc in source_docs:
            url = doc.metadata.get("source", "")
            title = doc.metadata.get("title", "")
            if url and title and (url, title) not in sources:
                sources.append((url, title))

        # Prepare context and generate response
        try:
            # Combine documents
            context = combine_documents(source_docs, question)
            
            # Create prompt
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(lang=lang)
            prompt = f"""{system_prompt}

CONTEXT INFORMATION:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer in 3-4 sentences or 4-5 bullet points maximum
2. Use **bold** for important names/numbers/dates
3. Structure with bullet points (•) for lists
4. Add ONE hyperlink at the end in format: [Read more about XYZ →](URL)
5. Be direct - skip phrases like "According to" or "Based on"

Generate a beautifully structured, concise answer now:"""

            # Try model generation first
            if model:
                try:
                    response = model(prompt)
                    if response:
                        # CRITICAL: Strip any HTML tags that model might output
                        # Remove HTML tags like <strong>, <a>, <li>, <div>, etc.
                        response = re.sub(r'<[^>]+>', '', response)
                        
                        # Check if response already has hyperlinks, if not add source
                        if sources and '[' not in response and '](' not in response:
                            # Add the most relevant source as a clean hyperlink
                            url, title = sources[0]
                            response = f"{response}\n\n[View {title} →]({url})"

                        log_interaction(question, response)
                        return {"answer": response, "sources": [url for url, _ in sources[:3]]}
                except Exception as model_error:
                    logger.error(f"Model error: {str(model_error)}")
                    # Fall through to backup handling

            # Backup: Provide structured response from context
            segments = []
            for i, doc in enumerate(source_docs[:3]):  # Limit to top 3 docs
                content = doc.page_content.strip()
                if content:
                    # Summarize content if too long
                    if len(content) > 200:
                        content = content[:200] + "..."
                    segments.append(f"• {content}")

            if segments:
                backup_response = "\n".join(segments)
                if sources:
                    url, title = sources[0]
                    backup_response = f"{backup_response}\n\n[Learn more about {title} →]({url})"

                log_interaction(question, backup_response, "Used backup response")
                return {"answer": backup_response, "sources": [url for url, _ in sources[:3]]}

            # If no valid content found
            response = handle_error_response("no_context")
            log_interaction(question, response, "No valid content")
            return {"answer": response, "sources": []}

        except Exception as process_error:
            logger.error(f"Error processing response: {str(process_error)}")
            response = handle_error_response("general_error")
            log_interaction(question, response, str(process_error))
            return {"answer": response, "sources": []}

    except Exception as e:
        logger.error(f"Unhandled error in rag_answer: {str(e)}")
        response = handle_error_response("general_error")
        log_interaction(question, response, str(e))
        return {"answer": response, "sources": []}
