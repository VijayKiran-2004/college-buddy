import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Tuple, Optional, List

class AutonomousPortalScraper:
    """Scraper for TKRCET Autonomous portal (tkrcetautonomous.org) - ASP.NET"""
    
    def __init__(self):
        self.base_url = "https://www.tkrcetautonomous.org"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.session = None
        self.is_logged_in = False
        self.student_name = None
        
    def _convert_to_uppercase(self, text: str) -> str:
        return text.upper() if text else text
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Login to autonomous portal (ASP.NET)"""
        try:
            username = self._convert_to_uppercase(username)
            # password = self._convert_to_uppercase(password) # User password as is
            
            print(f"  [Logging in to Autonomous Portal as: {username}]")
            
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': self.login_url
            })
            
            # Step 1: GET login page (Landing)
            print(f"  [Fetching login page: {self.login_url}]")
            response = self.session.get(self.login_url, timeout=10)
            
            if response.status_code != 200:
                print(f"  [Login Page Status: {response.status_code}]")
                return False, f"Failed to load login page (Status: {response.status_code})"
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Step 1.5: Click "Student Login" if present
            lnkStudent = soup.find(id="lnkStudent")
            if lnkStudent:
                print("  [Found 'Student Login' link. Clicking it...]")
                payload = {}
                for hidden in soup.find_all("input", type="hidden"):
                    payload[hidden.get("name")] = hidden.get("value")
                
                payload["__EVENTTARGET"] = "lnkStudent"
                payload["__EVENTARGUMENT"] = ""
                
                # Post click
                response = self.session.post(self.login_url, data=payload, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
            
            # Step 2: Extract Login Fields
            if not soup.find("input", id="txtUserId"):
                 return False, "Could not find login fields (txtUserId). Check connection."
            
            payload = {}
            for hidden in soup.find_all("input", type="hidden"):
                payload[hidden.get("name")] = hidden.get("value")
            
            payload["txtUserId"] = username
            payload["txtPwd"] = password
            payload["btnLogin"] = "Login"
            
            print("  [Submitting credentials...]")
            response = self.session.post(self.login_url, data=payload, timeout=10)
            
            # Step 3: Verify Login
            if "Logout" in response.text or "Student/Home.aspx" in response.url or "Dashboard" in response.text:
                self.is_logged_in = True
                self.student_name = username
                print("  [✓ Autonomous Login successful]")
                return True, "Login successful"
            else:
                 # Try to parse error
                 err = soup.find(id="lblMsg")
                 msg = err.get_text(strip=True) if err else "Unknown error"
                 return False, f"Login failed: {msg}"

        except Exception as e:
            print(f"  [Login Error: {str(e)}]")
            return False, f"Login error: {str(e)}"

    def fetch_results(self) -> Dict[str, Any]:
        """Fetch results from autonomous portal"""
        if not self.is_logged_in:
            return {"success": False, "error": "Not logged in"}
            
        try:
            print("  [Fetching results from autonomous portal...]")
            
            # User Requirement: Go directly to this URL
            target_url = f"{self.base_url}/StudentLogin/Student/OverallMarksSemwise.aspx"
            
            print(f"  [Navigating to: {target_url}]")
            resp = self.session.get(target_url, timeout=15)
            
            if resp.status_code != 200:
                 target_url = f"{self.base_url}/Student/OverallMarksSemwise.aspx"
                 print(f"  [Retrying alternate URL: {target_url}]")
                 resp = self.session.get(target_url, timeout=15)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results_data = {"success": False, "results": [], "overall": {}}
            
            # --- EXTRACT HEADER INFO ---
            full_text = soup.get_text()
            cgpa_match = re.search(r'Final CGPA\s*[:=]\s*(\d+\.?\d*)', resp.text)
            credits_match = re.search(r'Total Credits\s*[:=]\s*(\d+\.?\d*)', resp.text)
            due_match = re.search(r'Due Subjects\s*[:=]\s*([0-9/]+)', resp.text)
            
            if cgpa_match: results_data["overall"]["CGPA"] = cgpa_match.group(1)
            if credits_match: results_data["overall"]["Total Credits"] = credits_match.group(1)
            if due_match: results_data["overall"]["Due Subjects"] = due_match.group(1)
            
            # --- SEMESTER SELECTION LOGIC ---
            roman_pattern = re.compile(r'\b[IVX]+\s+YEAR\s+[IVX]+\s+SEM[EI]STER', re.IGNORECASE)
            sem_buttons = []
            
            # Scan INPUTS (type=submit/button)
            for inp in soup.find_all('input', type=['submit', 'button']):
                val = inp.get('value', '').upper()
                if roman_pattern.search(val):
                    sem_buttons.append({
                        "text": val,
                        "name": inp.get('name'),
                        "element": inp
                    })
            
            # Fallback to links
            if not sem_buttons:
                for a in soup.find_all('a', href=True):
                    text = a.get_text(strip=True).upper()
                    if roman_pattern.search(text):
                         sem_buttons.append({"text": text, "href": a['href'], "element": a})

            if sem_buttons:
                # Select Latest (Right-Most)
                chosen_btn = sem_buttons[-1]
                print(f"  [Selecting Latest: {chosen_btn['text']}]")
                
                # Perform Click / PostBack
                payload = {}
                for hidden in soup.find_all("input", type="hidden"):
                     payload[hidden.get("name")] = hidden.get("value")
                
                if "name" in chosen_btn:
                     payload[chosen_btn["name"]] = chosen_btn["element"].get("value")
                elif "href" in chosen_btn:
                     match = re.search(r"__doPostBack\('([^']+)'", chosen_btn['href'])
                     if match:
                         payload["__EVENTTARGET"] = match.group(1)
                         payload["__EVENTARGUMENT"] = ""
                
                print(f"  [Posting selection for {chosen_btn['text']}...]")
                resp = self.session.post(target_url, data=payload, timeout=15)
                soup = BeautifulSoup(resp.text, 'html.parser')

            else:
                print("  [No specific semester buttons found. Assuming latest results displayed.]")

            # --- EXTRACT RESULTS TABLE ---
            target_table = None
            for table in soup.find_all("table"):
                header_text = table.get_text(strip=True).lower()
                if "exam code" in header_text and "subject" in header_text:
                    target_table = table
                    break
            
            if target_table:
                print("  [Found Results Table]")
                rows = []
                # Header
                header_row = target_table.find("tr", class_=lambda x: x and ("header" in x or "title" in x)) or target_table.find("tr")
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
                    if headers: rows.append(headers)
                
                # Data Rows
                for tr in target_table.find_all("tr"):
                    if tr == header_row: continue 
                    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if len(cells) >= 5 and "Subject" not in cells[2]: 
                        rows.append(cells)
                
                results_data["results"].append({
                    "source": "Overall Marks Semwise",
                    "data": rows
                })
                results_data["success"] = True
            else:
                 return {"success": False, "error": "Could not find results table."}

            return results_data
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout(self):
        if self.session:
            self.session.close()
            self.is_logged_in = False

    def __del__(self):
        self.logout()
