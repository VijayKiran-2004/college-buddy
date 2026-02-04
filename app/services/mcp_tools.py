"""
MCP Tools for AgentCPM-Explore
Provides tools for static facts, web scraping, and database queries with smart caching
"""

import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional


class TwoTierCache:
    """Smart caching with static and dynamic tiers"""
    
    def __init__(self):
        self.static_cache = {}   # Never expires
        self.dynamic_cache = {}  # TTL-based
    
    def get_static(self, key: str) -> Optional[Any]:
        """Get from static cache"""
        return self.static_cache.get(key)
    
    def set_static(self, key: str, value: Any):
        """Set in static cache (permanent)"""
        self.static_cache[key] = value
    
    def get_dynamic(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        """Get from dynamic cache with TTL check"""
        if key in self.dynamic_cache:
            value, timestamp = self.dynamic_cache[key]
            if time.time() - timestamp < ttl_seconds:
                return value
        return None
    
    def set_dynamic(self, key: str, value: Any):
        """Set in dynamic cache with timestamp"""
        self.dynamic_cache[key] = (value, time.time())


class CollegeMCPTools:
    """MCP Tools for College Buddy - Pure MCP approach"""
    
    def __init__(self):
        self.cache = TwoTierCache()
        self.base_url = "https://tkrcet.ac.in"
        
        # Load knowledge base
        from app.services.ultra_rag import KNOWLEDGE_BASE
        self.kb = KNOWLEDGE_BASE
        
        # Initialize student portal scraper
        from app.services.student_portal_scraper import StudentPortalScraper, AutonomousPortalScraper
        self.portal_scraper = StudentPortalScraper()
        self.autonomous_scraper = AutonomousPortalScraper()
        self.portal_credentials = None  # Will be set when needed
        self.selected_portal = "regular"  # 'regular' or 'autonomous'
    
    def get_tool_definitions(self):
        """Return tool definitions for AgentCPM"""
        return [
            {
                "name": "check_static_facts",
                "description": "Check unchanging facts about the college (personnel, location, timings, history, accreditation). Use this FIRST for factual queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The factual query (e.g., 'principal', 'location', 'timings')"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "scrape_latest_notices",
                "description": "Scrape the latest notices and announcements from the college website. Use for queries about 'latest', 'recent', 'current' information.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "scrape_placements",
                "description": "Scrape placement statistics and information from the college website.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "search_website",
                "description": "Search the entire college website for specific information. Use as fallback when other tools don't have the answer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "query_database",
                "description": "Query student placement database for statistics. Returns ONLY aggregate data (placement rates, average CGPA, top companies). Individual student data is protected.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query about placements, students, or statistics (e.g., 'how many students placed?', 'placement rate in CSE?')"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "query_student_portal",
                "description": "Access student portal (tkrcet.in) to fetch personal results, attendance, and dashboard data. Requires student login credentials.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Student username (will be converted to uppercase)"
                        },
                        "password": {
                            "type": "string",
                            "description": "Student password (will be converted to uppercase)"
                        },
                        "data_type": {
                            "type": "string",
                            "description": "Type of data to fetch: 'results', 'dashboard', or 'all'"
                        },
                        "portal_type": {
                            "type": "string",
                            "description": "Which portal to access: 'regular' (tkrcet.in) or 'autonomous' (tkrcetautonomous.org)"
                        }
                    },
                    "required": ["username", "password", "data_type"]
                }
            }
        ]
    
    def check_static_facts(self, query: str) -> Dict[str, Any]:
        """
        Check static facts from knowledge base (0.1s)
        Cached permanently
        """
        query_lower = query.lower()
        
        # Check cache first
        cached = self.cache.get_static(query_lower)
        if cached:
            return {"success": True, "answer": cached, "cached": True}
        
        # Personnel queries (handle typos like 'principle')
        if ('principal' in query_lower or 'principle' in query_lower) and 'vice' not in query_lower:
            answer = f"The Principal of TKRCET is {self.kb['personnel']['principal']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        if 'vice principal' in query_lower:
            answer = f"The Vice Principal is {self.kb['personnel']['vice_principal']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        if 'secretary' in query_lower:
            answer = f"The Secretary of TKRCET is {self.kb['personnel']['secretary']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        if 'chairman' in query_lower:
            answer = f"The Chairman of TKRCET is {self.kb['personnel']['chairman']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        if 'founder' in query_lower or 'founded by' in query_lower or 'who started' in query_lower:
            answer = f"TKRCET was founded by {self.kb['history']['founder']} in {self.kb['history']['established']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        if 'hod' in query_lower or 'head of department' in query_lower:
            # Check for multiple departments in query
            found_hods = []
            for dept, hod in self.kb['personnel']['hod'].items():
                if dept in query_lower:
                    found_hods.append(f"The HOD of {dept.upper()} is {hod}")
            
            if found_hods:
                answer = ". ".join(found_hods) + "."
                self.cache.set_static(query_lower, answer)
                return {"success": True, "answer": answer, "cached": False}
        
        # Timings
        if 'timing' in query_lower or 'hours' in query_lower or 'time' in query_lower:
            answer = f"College timings: {self.kb['timings']['working_hours']}. Lunch break: {self.kb['timings']['lunch_break']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Location
        if 'location' in query_lower or 'address' in query_lower or 'where' in query_lower:
            answer = f"TKRCET is located at {self.kb['history']['location']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Established
        if 'established' in query_lower or 'founded' in query_lower or 'started' in query_lower:
            answer = f"TKRCET was established in {self.kb['history']['established']} on a {self.kb['history']['campus_size']} campus."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Courses/Branches (handle "how many branches")
        if 'course' in query_lower or 'program' in query_lower or 'branch' in query_lower or 'dept' in query_lower:
            ug = ', '.join(self.kb['courses']['ug'])
            pg = ', '.join(self.kb['courses']['pg'])
            answer = f"TKRCET offers {self.kb['courses']['total']}. UG Programs: {ug}. PG Programs: {pg}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Facilities (including transportation and sports)
        if 'facilit' in query_lower or 'infrastructure' in query_lower or 'transport' in query_lower or 'ground' in query_lower or 'playground' in query_lower or 'sports' in query_lower:
            answer = f"{self.kb['facilities']['main']} Special Features: {self.kb['facilities']['special']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Accreditation
        if 'naac' in query_lower or 'nba' in query_lower or 'accredit' in query_lower:
            answer = f"TKRCET is {self.kb['accreditation']['naac']} accredited, {self.kb['accreditation']['nba']}, and {self.kb['accreditation']['approvals']}."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Food/Canteen queries
        if 'food' in query_lower or 'canteen' in query_lower or 'mess' in query_lower or 'cafeteria' in query_lower:
            answer = "Yes, TKRCET has canteen facilities on campus providing food for students and staff. The college facilities include canteen services along with other amenities."
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # General "tell about college" or "college life"
        if any(phrase in query_lower for phrase in ['about college', 'tell about', 'college life', 'about tkrcet']):
            answer = f"TKRCET (Teegala Krishna Reddy Engineering College) was established in {self.kb['history']['established']} at {self.kb['history']['location']}. It is affiliated to {self.kb['history']['affiliation']} and is {self.kb['accreditation']['naac']} accredited. The college offers {self.kb['courses']['total']} with excellent facilities including {self.kb['facilities']['main']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Scholarship queries
        if 'scholarship' in query_lower or 'financial aid' in query_lower:
            sch = self.kb['scholarships']
            answer = f"TKRCET offers various scholarships: {', '.join(sch['types'])}. "
            answer += f"Merit scholarship: {sch['merit']}. "
            answer += f"{sch['fee_reimbursement']}. "
            answer += f"Apply through: {sch['application']}. Contact: {sch['contact']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Fee queries
        if 'fee' in query_lower or 'fees' in query_lower or 'cost' in query_lower or 'tuition' in query_lower:
            fees = self.kb['fees']
            answer = f"TKRCET Fee Structure (approximate): "
            answer += f"B.Tech: {fees['btech_annual']}, "
            answer += f"M.Tech: {fees['mtech_annual']}, "
            answer += f"MBA: {fees['mba_annual']}. "
            answer += f"Hostel: {fees['hostel']}, Transport: {fees['transport']}. "
            answer += f"Note: {fees['note']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Event queries
        if 'event' in query_lower or 'fest' in query_lower or 'festival' in query_lower or 'competition' in query_lower:
            events = self.kb['events']
            answer = f"TKRCET Events: "
            answer += f"Tech Fest: {events['tech_fest']}. "
            answer += f"Cultural Fest: {events['cultural_fest']}. "
            answer += f"Sports: {events['sports_day']}. "
            answer += f"Also: {events['hackathons']}, {events['workshops']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Exam schedule queries
        if 'exam' in query_lower or 'test' in query_lower or 'mid' in query_lower or 'semester' in query_lower:
            exams = self.kb['exam_schedule']
            answer = f"Exam Schedule: "
            answer += f"Mid-term 1: {exams['mid_term_1']}, "
            answer += f"Mid-term 2: {exams['mid_term_2']}, "
            answer += f"Semester End: {exams['semester_end']}. "
            answer += f"{exams['internal_marks']}. {exams['note']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Library queries
        if 'library' in query_lower or 'book' in query_lower:
            lib = self.kb['library']
            answer = f"{lib['name']}: {lib['collection']}. "
            answer += f"Timings: {lib['timings']}. "
            answer += f"Facilities: {lib['facilities']}. {lib['membership']}"
            self.cache.set_static(query_lower, answer)
            return {"success": True, "answer": answer, "cached": False}
        
        # Not found
        return {"success": False, "error": "No static fact found for this query"}
    
    def scrape_latest_notices(self) -> Dict[str, Any]:
        """
        Scrape latest notices from website (4-6s)
        Cached for 1 hour
        """
        cache_key = "latest_notices"
        
        # Check cache
        cached = self.cache.get_dynamic(cache_key, ttl_seconds=3600)
        if cached:
            return {"success": True, "notices": cached, "cached": True}
        
        # Scrape website
        try:
            url = f"{self.base_url}/notifications"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract notices (adjust selectors based on actual website)
            notices = []
            
            # Try common selectors
            for item in soup.select('.notice-item, .notification, article, .post')[:5]:
                title = item.get_text(strip=True)[:200]
                if title:
                    notices.append({'title': title, 'date': 'Recent'})
            
            # If no notices found, get recent text
            if not notices:
                text = soup.get_text(strip=True)[:500]
                notices = [{'title': 'Latest information from website', 'content': text}]
            
            # Cache result
            self.cache.set_dynamic(cache_key, notices)
            
            return {"success": True, "notices": notices, "cached": False}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scrape_placements(self) -> Dict[str, Any]:
        """
        Scrape placement data from website (4-6s)
        Cached for 1 hour
        """
        cache_key = "placements"
        
        # Check cache
        cached = self.cache.get_dynamic(cache_key, ttl_seconds=3600)
        if cached:
            return {"success": True, "data": cached, "cached": True}
        
        # Scrape website
        try:
            url = f"{self.base_url}/placements"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract placement data
            text = soup.get_text(strip=True)[:1000]
            
            # Check for Firewall/Block
            if "MalCare" in text or "Firewall" in text or "Blocked" in text:
                print("  ⚠ Scraper blocked by firewall - switching to backup database")
                db_result = self.query_database("placement statistics")
                # Wrap DB result to match scraper structure
                return {
                    "success": True, 
                    "data": {
                        "summary": "Placement Statistics (Fallback from Database)",
                        "content": db_result.get("data", "No data")
                    },
                    "cached": False
                }
            
            data = {
                "summary": "Placement information from TKRCET website",
                "content": text
            }
            
            # Cache result
            self.cache.set_dynamic(cache_key, data)
            
            return {"success": True, "data": data, "cached": False}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_database(self, query: str) -> Dict[str, Any]:
        """
        Query student database for placement statistics (privacy-protected)
        Returns ONLY aggregate data, never individual student records
        """
        cache_key = f"db_{query.lower()}"
        
        # Check cache
        cached = self.cache.get_dynamic(cache_key, ttl_seconds=3600)
        if cached:
            return {"success": True, "data": cached, "cached": True}
        
        try:
            # Import SQL system
            from app.services.sql_system import SQLSystem
            
            # Query database (privacy-protected)
            sql_system = SQLSystem()
            result = sql_system.query_students(query)
            sql_system.close()
            
            # Cache result
            self.cache.set_dynamic(cache_key, result)
            
            return {"success": True, "data": result, "cached": False}
        
        except Exception as e:
            print(f"  ⚠ SQL Query failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def search_website(self, query: str) -> Dict[str, Any]:
        """
        Search multiple relevant pages on website (5-10s)
        Cached for 1 hour per query
        """
        cache_key = f"search_{query.lower()}"
        
        # Check cache
        cached = self.cache.get_dynamic(cache_key, ttl_seconds=3600)
        if cached:
            return {"success": True, "results": cached, "cached": True}
        
        # Extract keywords from query (remove question words)
        query_lower = query.lower()
        stop_words = ['what', 'is', 'the', 'how', 'to', 'can', 'i', 'get', 'about', 'tell', 'me', 
                      'are', 'there', 'any', 'does', 'do', 'where', 'when', 'who', 'which', '?']
        
        keywords = []
        for word in query_lower.split():
            clean_word = word.strip('?,.')
            if clean_word not in stop_words and len(clean_word) > 2:
                keywords.append(clean_word)
        
        # If no keywords extracted, use original query
        if not keywords:
            keywords = [query_lower]
        
        # Define relevant pages to search
        pages_to_search = [
            "",  # Main page
            "/admissions",
            "/admission",
            "/facilities",
            "/placements",
            "/about",
            "/about-us",
            "/departments",
            "/academics",
            "/campus-life",
            "/contact",
            "/contact-us"
        ]
        
        # Search across multiple pages
        try:
            found_results = []
            
            for page in pages_to_search:
                try:
                    url = f"{self.base_url}{page}"
                    response = requests.get(url, timeout=3)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove navigation, header, footer, scripts, styles
                    for element in soup(['nav', 'header', 'footer', 'script', 'style', 'iframe']):
                        element.decompose()
                    
                    # Try to get main content area first
                    main_content = soup.find('main') or soup.find('article') or soup.find(class_=['content', 'main-content', 'page-content'])
                    
                    if main_content:
                        text = main_content.get_text()
                    else:
                        text = soup.get_text()
                    
                    text_lower = text.lower()
                    
                    # Search for ANY keyword in page text
                    matches = 0
                    for keyword in keywords:
                        if keyword in text_lower:
                            matches += 1
                    
                    # If found at least one keyword
                    if matches > 0:
                        # Find best context (around first keyword match)
                        first_keyword = keywords[0]
                        idx = text_lower.find(first_keyword)
                        
                        if idx != -1:
                            context = text[max(0, idx-150):min(len(text), idx+300)].strip()
                            # Clean up whitespace
                            context = ' '.join(context.split())
                            
                            found_results.append({
                                'page': page if page else 'home',
                                'url': url,
                                'context': context,
                                'matches': matches
                            })
                    
                    # Stop after finding 3 relevant pages
                    if len(found_results) >= 3:
                        break
                
                except:
                    continue  # Skip failed pages
            
            # Sort by number of keyword matches (best results first)
            found_results.sort(key=lambda x: x['matches'], reverse=True)
            
            # Format results
            if found_results:
                results = f"Found information about '{query}' on the TKRCET website:\n\n"
                for i, result in enumerate(found_results[:3], 1):
                    results += f"{i}. From {result['page'] if result['page'] else 'home'} page:\n"
                    results += f"   {result['context'][:250]}...\n\n"
                results += f"🔗 For more details, visit: {self.base_url}"
            else:
                # Provide helpful fallback
                results = f"I couldn't find specific information about '{query}' on the website. "
                results += f"However, you can:\n\n"
                combined_text = f"I couldn't find specific information about '{query}' on the website. "
                combined_text += f"However, you can:\n\n"
                combined_text += f"1. Visit the college website: https://tkrcet.ac.in\n"
                combined_text += f"2. Contact the college directly\n"
                combined_text += f"3. Try asking your question differently with more specific keywords"
            
            # Cache result
            self.cache.set_dynamic(cache_key, combined_text)
            
            # Suggest KB expansion if content is useful
            try:
                from app.services.kb_expander import KnowledgeBaseExpander
                expander = KnowledgeBaseExpander()
                expander.suggest_kb_update(query, combined_text)
            except:
                pass  # KB expansion is optional
            
            return {"success": True, "results": combined_text, "cached": False}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_student_portal(self, username: str, password: str, data_type: str = "all", portal_type: str = "regular") -> Dict[str, Any]:
        """
        Query student portal for personal data (results, attendance, etc.)
        Credentials are automatically converted to uppercase
        
        Args:
            username: Student username
            password: Student password
            data_type: Type of data to fetch ('results', 'dashboard', or 'all')
            portal_type: 'regular' or 'autonomous'
        
        Returns:
            Dictionary with portal data
        """
        # Determine scraper based on portal type (or stored preference)
        portal = portal_type if portal_type else getattr(self, "selected_portal", "regular")
        
        if portal == "autonomous":
            scraper = self.autonomous_scraper
            title = "Autonomous Portal"
        else:
            scraper = self.portal_scraper
            title = "Regular Portal"
            
        cache_key = f"portal_{portal}_{username.upper()}_{data_type}"
        
        # Check cache (5 minute TTL for portal data)
        cached = self.cache.get_dynamic(cache_key, ttl_seconds=300)
        if cached:
            return {"success": True, "data": cached, "cached": True}
        
        try:
            # Login to portal
            success, message = scraper.login(username, password)
            
            if not success:
                return {
                    "success": False,
                    "error": f"Login failed ({title}): {message}"
                }
            
            # Fetch requested data
            result = {
                "success": True,
                "login_message": message,
                "data": {},
                "portal": title
            }
            
            if data_type in ["results", "all"]:
                results = scraper.fetch_results()
                result["data"]["results"] = results
            
            # Dashboard might not be available for Autonomous yet, but try
            if data_type in ["dashboard", "all"] and hasattr(scraper, "fetch_dashboard_data"):
                dashboard = scraper.fetch_dashboard_data()
                result["data"]["dashboard"] = dashboard
            
            # Logout
            scraper.logout()
            
            # Cache the result
            self.cache.set_dynamic(cache_key, result["data"])
            
            return result
        
        except Exception as e:
            # Make sure to logout even on error
            try:
                scraper.logout()
            except:
                pass
            
            return {"success": False, "error": str(e)}
