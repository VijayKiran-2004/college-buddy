"""
Simplified AgentCPM-based MCP system
Pure MCP approach with smart caching - works without full AgentCPM complexity
"""

import json
import time
from app.services.mcp_tools import CollegeMCPTools


class SimplifiedMCPAgent:
    """
    Simplified MCP Agent for College Buddy
    Uses intelligent tool selection without requiring full AgentCPM setup
    """
    
    def __init__(self):
        print("\nInitializing Simplified MCP Agent...")
        
        # Initialize tools
        self.tools = CollegeMCPTools()
        self.tool_map = {
            "check_static_facts": self.tools.check_static_facts,
            "scrape_latest_notices": self.tools.scrape_latest_notices,
            "scrape_placements": self.tools.scrape_placements,
            "search_website": self.tools.search_website,
            "query_student_portal": self.tools.query_student_portal
        }
        
        # Check if Ollama is available for LLM formatting
        self.llm_available = self._check_ollama_health()
        
        # Initialize analytics system
        try:
            from app.services.analytics import AnalyticsSystem
            self.analytics = AnalyticsSystem()
        except Exception as e:
            print(f"⚠ Analytics system unavailable: {e}")
            self.analytics = None
        
        # Conversation context for follow-up questions
        self.conversation_history = []  # Last 3 queries
        self.last_topic = None  # Track current topic (e.g., "placements", "admissions")
        
        # State management for login flow
        self.waiting_for_credential = False
        self.temp_username = None
        
        # Multi-language support
        try:
            from app.services.translator import Translator
            self.translator = Translator()
        except Exception as e:
            print(f"⚠ Translator unavailable: {e}")
            self.translator = None
        
        print("✓ MCP Agent ready!\n")
    
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama is running and available"""
        print("  Checking Ollama connection...")
        try:
            import requests
            # Try to connect to Ollama
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                print("  ✓ Ollama LLM available (friendly mode enabled)")
                return True
        except Exception as e:
            print(f"  ⚠ Ollama connection failed: {str(e)}")
            pass
        
        print("  ⚠ Ollama not available - System will use FAST RAW MODE (no personality)")
        print("  ℹ To enable friendly mode: 'ollama run gemma2:2b' in a new terminal")
        return False
    
    def _should_use_llm(self, raw_data: str, tool_name: str) -> bool:
        """Decide if LLM formatting is worth the time"""
        
        # Don't use LLM if not available
        if not self.llm_available:
            return False
        
        # Skip LLM for very short, clear answers (under 150 chars)
        if tool_name == "check_static_facts" and len(raw_data) < 150:
            return False
        
        # Skip if raw data is already friendly (has emojis or exclamation)
        if "😊" in raw_data or "🎉" in raw_data or raw_data.count("!") > 1:
            return False
        
        # Use LLM for complex/long responses
        return True
    
    def _resolve_context(self, query: str) -> str:
        """Resolve context references and follow-up questions"""
        query_lower = query.lower()
        
        # Handle follow-up patterns
        follow_up_patterns = {
            'what about': self.last_topic,
            'and': self.last_topic,
            'also': self.last_topic,
            'how about': self.last_topic,
        }
        
        # If query starts with follow-up pattern and we have context
        for pattern, topic in follow_up_patterns.items():
            if query_lower.startswith(pattern) and topic:
                # Extract the new subject (e.g., "what about CSE?" → "CSE")
                new_subject = query_lower.replace(pattern, '').strip()
                # Combine with last topic (e.g., "placement statistics for CSE")
                resolved = f"{topic} {new_subject}"
                print(f"  [Context resolved: '{query}' → '{resolved}']")
                return resolved
        
        # Update topic based on query
        if 'placement' in query_lower or 'placed' in query_lower:
            self.last_topic = 'placement statistics for'
        elif 'admission' in query_lower:
            self.last_topic = 'admission information for'
        elif 'fee' in query_lower:
            self.last_topic = 'fee structure for'
        elif 'hod' in query_lower:
            self.last_topic = 'head of department for'
        
        return query
    
    def _is_college_related(self, query: str) -> bool:
        """Scope validation - only reject obvious non-college topics"""
        query_lower = query.lower()
        
        # Only reject obvious non-college topics (math, science problems)
        non_college = [
            'formula', 'equation', 'calculate', 'solve', 'math problem',
            'physics problem', 'chemistry problem', '^2', '=', 'x+y', 
            'integral', 'derivative', 'theorem', 'proof'
        ]
        
        # Reject if it's clearly a math/science problem
        if any(kw in query_lower for kw in non_college):
            # But allow if it mentions college
            if 'college' in query_lower or 'tkrcet' in query_lower:
                return True
            return False
        
        # Accept everything else (assume college-related)
        return True
    
    def _select_tool(self, query: str) -> str:
        """Intelligently select which tool to use"""
        query_lower = query.lower()
        
        # Check for latest/recent information - always scrape fresh
        if any(kw in query_lower for kw in ['latest', 'recent', 'current', 'new', 'notice', 'announcement']):
            return "scrape_latest_notices"
        
        # Check for student portal queries
        if any(kw in query_lower for kw in ['my result', 'my attendance', 'login', 'student portal', 'dashboard', 'my grade', 'my mark']):
            # We need to check if we have credentials
            # This will be handled in the call method
            return "query_student_portal"
            
        # FORCE: If query contains a roll number (e.g., 22k91a05c0), force portal tool
        import re
        if re.search(r'\b\d{2}[kK]\d{2}[a-zA-Z0-9]+\b', query_lower) and ('result' in query_lower or 'mark' in query_lower):
             return "query_student_portal"
        
        # Check for placement/student database queries (STRICT ROUTING)
        # These keywords should ALWAYS go to the database, never the scraper
        sql_keywords = [
            'how many', 'students placed', 'placement rate', 'placement statistics', 
            'cgpa', 'average', 'top companies', 'recruiters', 'students in',
            'highest', 'lowest', 'package', 'salary', 'count', 'number of',
            'total', 'percent', 'database', 'db', 'record'
        ]
        if any(kw in query_lower for kw in sql_keywords):
            return "query_database"
        
        # Check for placement queries - scrape website
        if any(kw in query_lower for kw in ['placement', 'placed', 'company', 'companies', 'job']):
            # If asking about numbers/stats, use database
            if any(kw in query_lower for kw in ['how many', 'statistics', 'rate', 'percentage']):
                return "query_database"
            # Otherwise scrape website for general placement info
            return "scrape_placements"
        
        # For everything else: try static facts first (instant), then search website
        # This is the pure MCP approach - always get fresh data when static facts don't have it
        return "check_static_facts"  # Will auto-fallback to search_website
    
    def __call__(self, query: str) -> str:
        """Main entry point"""
        query = query.strip()
        
        if not query:
            return "Please enter a question."
        
        # Multi-language support: detect and translate
        user_language = 'english'
        if self.translator:
            query, user_language = self.translator.process_query(query)
            if user_language != 'english':
                print(f"  [Language detected: {user_language}, translated query]")
        
        # Greetings
        greetings = ['hi', 'hello', 'hey', 'how are you', 'how r u', 'how are u', 'whats up', "what's up"]
        if any(g == query.lower() for g in greetings):
            response = "Hello! I'm TKRCET College Assistant. How can I help you today? 😊"
            if self.translator and user_language != 'english':
                response = self.translator.process_response(response, user_language)
            return response
        
        # Resolve context for follow-up questions
        original_query = query
        query = self._resolve_context(query)
        
        # Scope validation (only reject obvious non-college topics)
        if not self._is_college_related(query):
            response = "I'm a TKRCET College Assistant. I can help with college-related questions, but that seems like a math or science problem. Try asking about admissions, courses, facilities, placements, or campus life!"
            if self.translator and user_language != 'english':
                response = self.translator.process_response(response, user_language)
            return response
            
        # --- LOGIN STATE HANDLING ---
        if self.waiting_for_credential:
            # Case 1: Waiting for Roll Number
            if not self.temp_username:
                self.temp_username = query.strip().upper()
                return "Thanks! Now please enter your password:"
            
            # Case 2: Waiting for Password (we have username)
            else:
                password = query.strip()
                # Store credentials temporarily (username, password, portal_type)
                # User specified tkrecautonomous.org, so we force 'autonomous'
                self.tools.portal_credentials = (self.temp_username, password, "autonomous")
                
                # Reset state
                self.waiting_for_credential = False
                self.temp_username = None
                
                # Trigger the portal query
                print(f"  [Credentials received. Logging in to Autonomous Portal...]")
                query = "my results" # generic trigger
        # ----------------------------
        
        # Add to conversation history
        self.conversation_history.append(original_query)
        if len(self.conversation_history) > 3:
            self.conversation_history.pop(0)
        
        # Select and execute tool
        tool_name = self._select_tool(query)
        
        # Track start time for analytics
        start_time = time.time()
        success = False
        error_msg = None
        
        try:
            if tool_name == "check_static_facts":
                # Try static facts first (instant if cached)
                result = self.tools.check_static_facts(query)
                
                # If not found in static facts, ALWAYS search website (Pure MCP!)
                if not result.get("success"):
                    print("  [Searching website for fresh information...]")
                    result = self.tools.search_website(query)
                    tool_name = "search_website"
                    
            elif tool_name == "scrape_latest_notices":
                result = self.tools.scrape_latest_notices()
                
            elif tool_name == "scrape_placements":
                result = self.tools.scrape_placements()
            
            elif tool_name == "query_database":
                result = self.tools.query_database(query)
            
            elif tool_name == "query_student_portal":
                # Check for credentials
                if not self.tools.portal_credentials:
                    # Enable login state
                    self.waiting_for_credential = True
                    return "To access your results from the Student Portal, I need your **Roll Number** (I'll ask for your password next):"
                
                # Use stored credentials
                if len(self.tools.portal_credentials) == 3:
                    username, password, portal_type = self.tools.portal_credentials
                else:
                    username, password = self.tools.portal_credentials
                    portal_type = "regular"
                
                # Determine data type based on query
                data_type = "all"
                if "result" in query.lower() or "grade" in query.lower() or "mark" in query.lower():
                    data_type = "results"
                elif "dashboard" in query.lower() or "attendance" in query.lower():
                    data_type = "dashboard"
                    
                result = self.tools.query_student_portal(username, password, data_type, portal_type)
                
            else:  # search_website
                result = self.tools.search_website(query)
            
            success = result.get("success", False)
            
            # Format response with LLM
            response = self._format_response(result, tool_name, query)
            
            # Log analytics
            if self.analytics:
                response_time_ms = int((time.time() - start_time) * 1000)
                cached = result.get("cached", False)
                self.analytics.log_query(query, tool_name, response_time_ms, success, cached)
            
            # Translate response if needed
            if self.translator and user_language != 'english':
                response = self.translator.process_response(response, user_language)
            
            return response
        
        except Exception as e:
            error_msg = str(e)
            
            # Log failed query
            if self.analytics:
                response_time_ms = int((time.time() - start_time) * 1000)
                self.analytics.log_query(query, tool_name, response_time_ms, False, False, error_msg)
            
            error_response = f"I apologize, but I encountered an error: {error_msg}. Please try again."
            
            # Translate error if needed
            if self.translator and user_language != 'english':
                error_response = self.translator.process_response(error_response, user_language)
            
            return error_response
    
    def _format_response(self, result: dict, tool_name: str, query: str) -> str:
        """Format tool result into user-friendly response with smart LLM usage"""
        
        if not result.get("success"):
            return "I couldn't find specific information. Please try rephrasing your question or visit https://tkrcet.ac.in for more details."
        
        # Extract raw data based on tool type
        if tool_name == "query_student_portal":
            data = result.get("data", {})
            portal_name = result.get("portal", "Student Portal")
            raw_data = f"✓ Login Successful ({portal_name}): {result.get('login_message', 'OK')}\n\n"
            
            if "results" in data and data["results"].get("success"):
                raw_data += "🎓 RESULTS FETCHED:\n"
                
                # Check for overall performance
                overall = data["results"].get("overall_performance", {})
                if overall:
                    if "cgpa" in overall:
                        raw_data += f"Overall CGPA: {overall['cgpa']}\n"
                    if "percentage" in overall:
                        raw_data += f"Percentage: {overall['percentage']}\n"
                
                # List result sources found
                found_results = data["results"].get("results", [])
                
                if found_results:
                    for i, res in enumerate(found_results):
                        source = res.get("source", "Unknown Source")
                        table_data = res.get("data", [])
                        
                        raw_data += f"\n--- Source: {source} ---\n"
                        
                        # Format as text table
                        if table_data:
                            # Calculate column widths
                            col_widths = {}
                            for row in table_data:
                                for j, col in enumerate(row):
                                    col_widths[j] = max(col_widths.get(j, 0), len(str(col)))
                            
                            # Print rows
                            for row in table_data:
                                line = " | ".join(str(col).ljust(col_widths.get(j, 0)) for j, col in enumerate(row))
                                raw_data += line + "\n"
                        else:
                            raw_data += "(Empty table)\n"
                else:
                    raw_data += "No result tables found.\n"
            
            if "dashboard" in data and data["dashboard"].get("success"):
                dash = data["dashboard"]
                raw_data += "\n📊 DASHBOARD INFO:\n"
                if "student_name" in dash:
                    raw_data += f"Name: {dash['student_name']}\n"
                if "branch" in dash:
                    raw_data += f"Branch: {dash['branch']}\n"
                if "current_semester" in dash:
                    raw_data += f"Current Semester: {dash['current_semester']}\n"
                if "attendance" in dash:
                    raw_data += f"Attendance: {dash['attendance']}\n"
            
            return raw_data  # Return directly without LLM processing to preserve formatting

        elif tool_name == "check_static_facts":
            raw_data = result.get("answer", "")
        
        elif tool_name == "scrape_latest_notices":
            notices = result.get("notices", [])
            if not notices:
                return "No recent notices found. Please check the college website at https://tkrcet.ac.in/notifications"
            
            raw_data = "Latest notices from TKRCET:\n"
            for i, notice in enumerate(notices[:3], 1):
                raw_data += f"{i}. {notice.get('title', 'Notice')}\n"
        
        elif tool_name == "scrape_placements":
            data = result.get("data", {})
            content = data.get("content", "")
            raw_data = f"Placement information from TKRCET:\n{content[:500]}"
        
        elif tool_name == "query_database":
            raw_data = result.get("data", "No student data found in database. (Database might be empty)")
        
        else:  # search_website
            raw_data = result.get("results", "")
        
        # Smart decision: use LLM only when beneficial
        if self._should_use_llm(raw_data, tool_name):
            friendly_response = self._make_friendly(raw_data, query)
            # If LLM succeeded, return it; otherwise fall back to raw
            if friendly_response != raw_data:
                return friendly_response
        
        # Fast path: return raw data (instant response!)
        return raw_data
    
    def _make_friendly(self, raw_data: str, query: str) -> str:
        """Use Gemma 2:2b to create friendly, contextual response"""
        
        prompt = f"""You are TKRCET College Assistant, a helpful and friendly chatbot. Answer the student's question based on the information provided.

Student asked: {query}

Information available:
{raw_data}

Instructions:
- Be warm, friendly, and conversational
- Keep response concise (2-4 sentences)
- Use simple, clear language
- Add 1-2 relevant emojis if appropriate
- If information is incomplete, suggest visiting the website or contacting the college
- Don't make up information not in the data

Your friendly response:"""

        try:
            import requests
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'gemma2:2b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': 150  # Limit response length
                    }
                },
                timeout=30  # Increased from 10s to 30s
            )
            
            if response.status_code == 200:
                llm_response = response.json().get('response', '').strip()
                if llm_response:
                    return llm_response
        
        except Exception as e:
            # Silently fall back to raw data (expected behavior when Ollama is slow/unavailable)
            pass
        
        # Fallback: return raw data
        return raw_data

