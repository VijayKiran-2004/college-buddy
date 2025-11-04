"""
Enhanced cache builder with image OCR and PDF extraction.
Scrapes text content, extracts text from images, and processes PDFs.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging
from scraper.image_processor import (
    extract_text_from_image_url,
    extract_text_from_pdf_url,
    find_images_in_html,
    find_pdfs_in_html
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_FILE = 'data/scraped/scraped_data.json'
LINKS_FILE = 'data/links/structured_links.csv'

def scrape_url_with_images(url: str, page_name: str, timeout: int = 15) -> Optional[Dict]:
    """
    Scrape a URL including text extraction from images and PDFs.
    
    Args:
        url: URL to scrape
        page_name: Name/title of the page
        timeout: Request timeout
        
    Returns:
        Dict with scraped content or None if failed
    """
    try:
        logger.info(f"Scraping: {page_name} ({url})")
        
        # Fetch the page
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main text content
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        main_text = soup.get_text(separator=' ', strip=True)
        
        # Find and process images
        image_texts = []
        image_urls = find_images_in_html(soup)
        logger.info(f"  Found {len(image_urls)} images")
        
        for img_url in image_urls[:10]:  # Limit to first 10 images to avoid slowdown
            # Convert relative URLs to absolute
            if not img_url.startswith('http'):
                img_url = urljoin(url, img_url)
            
            # Skip tiny icons and logos
            if any(x in img_url.lower() for x in ['icon', 'logo', 'favicon', 'sprite']):
                continue
            
            # Extract text from image
            img_text = extract_text_from_image_url(img_url, timeout=10)
            if img_text and len(img_text) > 20:  # Only include substantial text
                image_texts.append(f"[Image OCR]: {img_text}")
        
        # Find and process PDFs
        pdf_texts = []
        pdf_urls = find_pdfs_in_html(soup)
        logger.info(f"  Found {len(pdf_urls)} PDFs")
        
        for pdf_url in pdf_urls[:5]:  # Limit to first 5 PDFs
            # Convert relative URLs to absolute
            if not pdf_url.startswith('http'):
                pdf_url = urljoin(url, pdf_url)
            
            # Extract text from PDF
            pdf_text = extract_text_from_pdf_url(pdf_url, timeout=30)
            if pdf_text and len(pdf_text) > 50:
                pdf_texts.append(f"[PDF Content]: {pdf_text}")
        
        # Combine all content
        all_content = [main_text]
        all_content.extend(image_texts)
        all_content.extend(pdf_texts)
        
        combined_content = "\n\n".join(all_content)
        
        logger.info(f"✓ Scraped {len(main_text)} chars text + {len(image_texts)} images + {len(pdf_texts)} PDFs")
        
        return {
            'url': url,
            'page_name': page_name,
            'content': combined_content,
            'image_count': len(image_texts),
            'pdf_count': len(pdf_texts),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"✗ Failed to scrape {url}: {str(e)}")
        return None


def build_enhanced_cache():
    """
    Build cache with enhanced scraping including image OCR and PDF extraction.
    """
    # Load URLs from structured_links.csv
    urls_to_scrape = []
    
    try:
        import csv
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
        logger.error(f"Failed to load URLs from {LINKS_FILE}: {e}")
        return
    
    if not urls_to_scrape:
        logger.error("No URLs found to scrape")
        return
    
    logger.info(f"Starting enhanced scraping of {len(urls_to_scrape)} URLs...")
    logger.info("This includes: text extraction + image OCR + PDF processing")
    logger.info("=" * 70)
    
    scraped_data = []
    total_images = 0
    total_pdfs = 0
    
    for i, (url, page_name) in enumerate(urls_to_scrape, 1):
        logger.info(f"\n[{i}/{len(urls_to_scrape)}] Processing: {page_name}")
        
        result = scrape_url_with_images(url, page_name)
        
        if result:
            scraped_data.append(result)
            total_images += result.get('image_count', 0)
            total_pdfs += result.get('pdf_count', 0)
        
        # Rate limiting
        time.sleep(2)
    
    # Save to cache file
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 70)
        logger.info(f"✓ Enhanced scraping complete!")
        logger.info(f"  Pages scraped: {len(scraped_data)}/{len(urls_to_scrape)}")
        logger.info(f"  Images processed: {total_images}")
        logger.info(f"  PDFs processed: {total_pdfs}")
        logger.info(f"  Saved to: {CACHE_FILE}")
        
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")


if __name__ == '__main__':
    print("Enhanced Cache Builder with Image OCR and PDF Extraction")
    print("=" * 70)
    print("\nIMPORTANT: Make sure Tesseract OCR is installed!")
    print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("=" * 70)
    
    input("\nPress Enter to start enhanced scraping (this may take 10-15 minutes)...")
    
    build_enhanced_cache()
    
    print("\n✓ Done! Now run 'python main.py' to rebuild the vector database with enriched content.")
