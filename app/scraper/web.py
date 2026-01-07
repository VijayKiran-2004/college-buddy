from posthog import page
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
import urllib3
import hashlib

def hash_page(page):
    content = json.dumps(page["sections"], sort_keys=True).encode('utf-8')
    return hashlib.md5(content).hexdigest()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../.."))

SCRAPED_DIR = os.path.join(PROJECT_ROOT, "data/scraped_data")
os.makedirs(SCRAPED_DIR, exist_ok=True)

DATA_FILE = os.path.join(SCRAPED_DIR, "webdata.json")

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        old_data = json.load(f)
else:
    old_data = {}

old_hashes = {}
for url, pdata in old_data.items():
    old_hashes[url] = hash_page(pdata)

BASE_URL = "https://tkrcet.ac.in/"
DOMAIN = "tkrcet.ac.in"

MAX_PAGES = 50
MAX_DEPTH = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win32; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

visited = set()
site_data = {}  


def normalize_url(url):
    url = url.split("#")[0]
    if url.endswith("/"):
        url = url[:-1]
    return url

def is_internal(url):
    parsed = urlparse(url)
    return parsed.netloc == "" or DOMAIN in parsed.netloc

def clean_text(text):
    return " ".join(text.split())

def fetch(url):
    try:
        res = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            verify=False,
            allow_redirects=True
        )
        if res.status_code == 200:
            return res.text
    except:
        print(f" Fetch failed: {url}")
    return None


def extract_page(url, html):
    soup = BeautifulSoup(html, "html.parser")

    page = {
        "url": url,
        "title": soup.title.text.strip() if soup.title else "",
        "sections": {}
    }

    current_section = "General"
    page["sections"][current_section] = {
        "texts": [],
        "tables": [],
        "images": []
    }

    body = soup.body if soup.body else soup

    for el in body.descendants:
        if not hasattr(el, "name"):
            continue

        if el.name in ["h1", "h2", "h3", "h4"]:
            heading = clean_text(el.get_text())
            if heading:
                current_section = heading
                page["sections"].setdefault(
                    current_section,
                    {"texts": [], "tables": [], "images": []}
                )

        elif el.name in ["p", "li"]:
            text = clean_text(el.get_text())
            if len(text) > 40:
                page["sections"][current_section]["texts"].append(text)

        elif el.name == "table":
            rows = []
            for tr in el.find_all("tr"):
                cells = [clean_text(td.get_text()) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                page["sections"][current_section]["tables"].append(rows)

        elif el.name == "img":
            src = el.get("src")
            if src:
                page["sections"][current_section]["images"].append(urljoin(url, src))


    page["sections"] = dict(sorted(page["sections"].items()))

    new_hash = hash_page(page)

    if url in old_hashes and old_hashes[url] == new_hash:
        site_data[url] = old_data[url]
        print(f"UNCHANGED → {url}")
    else:
        site_data[url] = page
        print(f"ADDED/UPDATED → {url}")


def crawl(url, depth=0):
    if depth > MAX_DEPTH or len(visited) >= MAX_PAGES:
        return

    url = normalize_url(url)
    if url in visited:
        return

    visited.add(url)
    print(f"Crawling: {url}")

    html = fetch(url)
    if not html:
        return

    extract_page(url, html)

    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        next_url = normalize_url(urljoin(url, a["href"]))
        if is_internal(next_url):
            crawl(next_url, depth + 1)


print("Starting structured crawl...")
crawl(BASE_URL)


with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(site_data, f, indent=2, ensure_ascii=False)

print("\nFILE CREATED SUCCESSFULLY")
print(f"File location: {DATA_FILE}")
print(f"Total pages: {len(site_data)}")
