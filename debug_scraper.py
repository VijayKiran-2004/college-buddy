import requests
from bs4 import BeautifulSoup
import re
import time

class DebugScraper:
    def __init__(self):
        self.base_url = "https://www.tkrcetautonomous.org"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': self.login_url
        })

    def login(self, username, password):
        print(f"Logging in as {username}...")
        try:
            # Step 1: Get Landing Page
            print(f"Fetching Landing: {self.login_url}")
            resp = self.session.get(self.login_url, timeout=10)
            print(f"Landing Status: {resp.status_code}")
            
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Check if we need to click "Student Login" (lnkStudent)
            lnkStudent = soup.find(id="lnkStudent")
            if lnkStudent:
                print("Found 'Student Login' link. Clicking it...")
                payload = {}
                for hidden in soup.find_all("input", type="hidden"):
                    payload[hidden.get("name")] = hidden.get("value")
                
                payload["__EVENTTARGET"] = "lnkStudent"
                payload["__EVENTARGUMENT"] = ""
                
                print("Posting 'lnkStudent' click...")
                resp = self.session.post(self.login_url, data=payload, timeout=10)
                print(f"Click Status: {resp.status_code}")
                soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Step 2: Now we should have txtUserId / txtPwd
            if not soup.find("input", id="txtUserId"):
                 print("ERROR: Still no txtUserId found! Dumping response.")
                 with open("post_click_err.html", "w", encoding="utf-8") as f:
                     f.write(resp.text)
                 return False

            print("Found Login Fields! Submitting...")
            
            payload = {}
            for hidden in soup.find_all("input", type="hidden"):
                payload[hidden.get("name")] = hidden.get("value")
            
            payload["txtUserId"] = username
            payload["txtPwd"] = password
            payload["btnLogin"] = "Login"
            
            resp = self.session.post(self.login_url, data=payload, timeout=10)
            print(f"Login Post Status: {resp.status_code}")
            
            # Dump result to check success
            with open("login_result.html", "w", encoding="utf-8") as f:
                 f.write(resp.text)
            
            if "Logout" in resp.text or "Student/Home.aspx" in resp.url or "Dashboard" in resp.text:
                print(f"Login SUCCESS!")
                return True
            else:
                print(f"Login FAILED")
                soup_fail = BeautifulSoup(resp.text, 'html.parser')
                err = soup_fail.find(id="lblMsg")
                if err: print(f"  Error Msg: {err.get_text(strip=True)}")
                
                return False

        except Exception as e:
            print(f"Login Exception: {e}")
            return False

scraper = DebugScraper()
# Try Uppercase
if not scraper.login("22K91A05C0", "22K91A05C0"):
    print("Trying Lowercase password...")
    scraper = DebugScraper()
    scraper.login("22K91A05C0", "22k91a05c0")
