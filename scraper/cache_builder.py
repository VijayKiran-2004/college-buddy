import requests, re, csv, json, os
from pypdf import PdfReader
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

def extract_text_from_url(session, url, page_name):
    """Extracts text from a given URL, handling both HTML and PDF."""
    try:
        print(f"[scraper] Processing {url}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = session.get(url, timeout=20, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/pdf' in content_type:
            # Handle PDF content
            with BytesIO(response.content) as f:
                reader = PdfReader(f)
                text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
            print(f"[scraper] Successfully extracted text from PDF: {url}")
        elif 'html' in content_type:
            # Handle HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            main_content = soup.find('div', class_='td-post-content') or \
                           soup.find('div', class_='td-page-content') or \
                           soup.find('div', class_='td-container')
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)

            if text:
                print(f"[scraper] Successfully extracted text from HTML: {url}")
            else:
                print(f"[scraper] No text extracted from HTML: {url}")
        else:
            print(f"[scraper] Skipping unsupported content type '{content_type}' at {url}")
            return None

        return {"url": url, "page_name": page_name, "content": text}

    except requests.exceptions.RequestException as e:
        print(f"[scraper] Request failed for {url}: {e}")
        return None
    except Exception as e:
        print(f"[scraper] Error processing {url}: {e}")
        return None

def build_cache_from_csv(csv_path: str, output_path: str):
    """Scrapes all URLs from a CSV and saves the content to a JSON file."""
    url_regex = r"https?://[^\s,]+"
    urls_to_scrape = set()

    # Read URLs and page names from CSV
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Skip header row
            for row in reader:
                if not row: continue
                line = ",".join(row)
                urls = re.findall(url_regex, line)
                page_name = row[1].strip() if len(row) > 1 and row[1].strip() else "Page"
                for url in urls:
                    urls_to_scrape.add((url, page_name))
    except FileNotFoundError:
        print(f"[scraper] Error: The file {csv_path} was not found.")
        return

    all_docs = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            future_to_url = {executor.submit(extract_text_from_url, session, url, name): url for url, name in urls_to_scrape}
            for future in as_completed(future_to_url):
                result = future.result()
                if result and result.get('content'):
                    all_docs.append(result)

    # Write the scraped content to the output JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, indent=4)
    
    print(f"\nScraping complete. {len(all_docs)} documents saved to {output_path}.")

if __name__ == "__main__":
    build_cache_from_csv('structured_links.csv', 'scraped_data.json')
