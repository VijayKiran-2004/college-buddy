"""
Scrapy-based web scraper with BeautifulSoup fallback parser
Main scraping uses Scrapy, falls back to BeautifulSoup for complex parsing
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import json
import csv
import re
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TKRCETSpider(scrapy.Spider):
    """Scrapy spider for TKRCET website with BeautifulSoup fallback"""
    
    name = 'tkrcet_spider'
    allowed_domains = ['tkrcet.ac.in']
    start_urls = []  # Will be populated from CSV or method parameter
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0.5,  # Be polite to the server
        'RETRY_TIMES': 3,
        'FEED_EXPORT_ENCODING': 'utf-8',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraped_data = []
    
    def parse(self, response):
        """Main parsing method using Scrapy selectors with BeautifulSoup fallback"""
        
        url = response.url
        logger.info(f"Scraping: {url}")
        
        try:
            # Primary method: Use Scrapy's CSS selectors
            page_title = self._extract_title_scrapy(response)
            page_content = self._extract_content_scrapy(response)
            
            # Fallback: If content is too short, use BeautifulSoup
            if len(page_content) < 100:
                logger.warning(f"Low content from Scrapy, using BeautifulSoup fallback for {url}")
                page_title, page_content = self._extract_with_beautifulsoup(response)
            
            # Store the scraped data
            data = {
                'url': url,
                'page_name': page_title,
                'content': page_content
            }
            
            self.scraped_data.append(data)
            
            yield data
            
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            # Final fallback to BeautifulSoup
            try:
                page_title, page_content = self._extract_with_beautifulsoup(response)
                data = {
                    'url': url,
                    'page_name': page_title,
                    'content': page_content
                }
                self.scraped_data.append(data)
                yield data
            except Exception as fallback_error:
                logger.error(f"BeautifulSoup fallback also failed for {url}: {fallback_error}")
    
    def _extract_title_scrapy(self, response) -> str:
        """Extract page title using Scrapy selectors"""
        # Try multiple selectors
        title = (
            response.css('title::text').get() or
            response.css('h1::text').get() or
            response.css('.page-title::text').get() or
            'Untitled Page'
        )
        return title.strip()
    
    def _extract_content_scrapy(self, response) -> str:
        """Extract main content using Scrapy selectors"""
        # Remove script and style elements
        content_parts = []
        
        # Try to get main content area
        main_content = response.css('main, article, .content, .main-content, #content')
        
        if main_content:
            # Extract all text from main content area
            text = ' '.join(main_content.css('::text').getall())
            content_parts.append(text)
        else:
            # Fallback: get body text
            text = ' '.join(response.css('body ::text').getall())
            content_parts.append(text)
        
        # Clean up whitespace
        content = ' '.join(content_parts)
        content = ' '.join(content.split())  # Normalize whitespace
        
        return content
    
    def _extract_with_beautifulsoup(self, response) -> tuple:
        """Fallback extraction using BeautifulSoup for complex parsing"""
        logger.info(f"Using BeautifulSoup parser for {response.url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        h1_tag = soup.find('h1')
        title = (
            title_tag.get_text().strip() if title_tag else
            h1_tag.get_text().strip() if h1_tag else
            'Untitled Page'
        )
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Extract text from main content
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find(class_='content') or
            soup.find(id='content') or
            soup.find('body')
        )
        
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
        else:
            content = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        content = ' '.join(content.split())
        
        return title, content
    
    def closed(self, reason):
        """Called when spider finishes - save data to JSON"""
        logger.info(f"Spider closed: {reason}")
        logger.info(f"Total pages scraped: {len(self.scraped_data)}")


def run_scrapy_scraper(output_file: str = 'data/scraped/scraped_data.json', urls: Optional[List[str]] = None, csv_path: str = 'data/links/structured_links.csv') -> List[Dict]:
    """
    Run the Scrapy scraper and save results
    
    Args:
        output_file: Path to save scraped data
        urls: Optional list of URLs to scrape (if None, reads from csv_path)
        csv_path: Path to CSV file with URLs (used if urls is None)
    
    Returns:
        List of scraped data dictionaries
    """
    
    logger.info("Starting Scrapy scraper with BeautifulSoup fallback...")
    
    # If no URLs provided, read from CSV
    if urls is None:
        logger.info(f"Reading URLs from {csv_path}...")
        urls = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                url_regex = r"https?://[^\s,]+"
                for row in reader:
                    if not row:
                        continue
                    line = ",".join(row)
                    found_urls = re.findall(url_regex, line)
                    urls.extend(found_urls)
            logger.info(f"Found {len(urls)} URLs in CSV")
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return []
    
    # Ensure we have URLs to scrape
    if not urls:
        logger.error("No URLs to scrape")
        return []
    
    # Configure the crawler
    process = CrawlerProcess(settings={
        'FEEDS': {
            output_file: {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            }
        },
        'LOG_LEVEL': 'INFO',
    })
    
    # If custom URLs provided, override start_urls
    if urls:
        TKRCETSpider.start_urls = urls
    
    # Run the spider
    process.crawl(TKRCETSpider)
    process.start()  # This blocks until crawling is finished
    
    # Load and return the scraped data
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        logger.info(f"✅ Successfully scraped {len(scraped_data)} pages")
        logger.info(f"📄 Data saved to {output_file}")
        return scraped_data
    except Exception as e:
        logger.error(f"Error loading scraped data: {e}")
        return []


if __name__ == "__main__":
    # Run the scraper
    data = run_scrapy_scraper()
    
    # Print summary
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    print(f"Total pages scraped: {len(data)}")
    print(f"Average content length: {sum(len(d['content']) for d in data) / len(data):.0f} chars")
    print("\nPages scraped:")
    for item in data:
        print(f"  - {item['page_name']} ({len(item['content'])} chars)")
