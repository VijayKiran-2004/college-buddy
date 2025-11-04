"""
Optimized cache builder - Clean, fast, organized scraping.
Focuses on essential content only for maximum speed.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import csv
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

CACHE_FILE = 'data/scraped/scraped_data.json'
LINKS_FILE = 'data/links/structured_links.csv'

def clean_text(text: str) -> str:
    """Remove extra whitespace and clean text."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def scrape_page_optimized(url: str, page_name: str, timeout: int = 10) -> Optional[Dict]:
    """
    Fast, clean scraping - extract only essential content.
    """
    try:
        logger.info(f"📄 {page_name}")
        
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove noise - keep only content
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                             'sidebar', 'menu', 'iframe', 'noscript']):
            element.decompose()
        
        # Target main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
        
        if main_content:
            # Extract clean text
            text = main_content.get_text(separator='\n', strip=True)
            cleaned = clean_text(text)
            
            # Only store if substantial content
            if len(cleaned) > 100:
                logger.info(f"  ✓ {len(cleaned)} chars")
                return {
                    'url': url,
                    'page_name': page_name,
                    'content': cleaned,
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                logger.warning(f"  ⚠ Too short ({len(cleaned)} chars)")
        
        return None
        
    except requests.Timeout:
        logger.error(f"  ✗ Timeout")
        return None
    except Exception as e:
        logger.error(f"  ✗ {str(e)[:50]}")
        return None


def build_optimized_cache():
    """
    Build clean, fast cache - organized and optimized.
    """
    # Load URLs
    urls_to_scrape = []
    
    try:
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    link = row[0].strip()
                    page_name = row[1].strip()
                    if link.startswith('http'):
                        urls_to_scrape.append((link, page_name))
    except Exception as e:
        logger.error(f"Failed to load URLs: {e}")
        return
    
    if not urls_to_scrape:
        logger.error("No URLs found!")
        return
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 OPTIMIZED SCRAPING - {len(urls_to_scrape)} pages")
    logger.info(f"   Fast & Clean | Essential Content Only")
    logger.info(f"{'='*70}\n")
    
    scraped_data = []
    success_count = 0
    
    for i, (url, page_name) in enumerate(urls_to_scrape, 1):
        print(f"[{i}/{len(urls_to_scrape)}] ", end='')
        
        result = scrape_page_optimized(url, page_name)
        
        if result:
            scraped_data.append(result)
            success_count += 1
        
        # Respectful rate limiting
        time.sleep(0.5)
    
    # Save cache
    try:
        Path(CACHE_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ SCRAPING COMPLETE!")
        logger.info(f"   Success: {success_count}/{len(urls_to_scrape)} pages")
        logger.info(f"   Cache: {CACHE_FILE}")
        logger.info(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║           OPTIMIZED CACHE BUILDER                          ║
║  Clean • Fast • Organized • Essential Content Only         ║
╚════════════════════════════════════════════════════════════╝
""")
    
    input("Press Enter to start optimized scraping (2-3 minutes)...\n")
    
    start_time = time.time()
    build_optimized_cache()
    elapsed = time.time() - start_time
    
    print(f"\n⏱ Completed in {elapsed:.1f} seconds")
    print("\n✅ Next: Restart backend to rebuild vector database")
    print("   Command: python main.py\n")
