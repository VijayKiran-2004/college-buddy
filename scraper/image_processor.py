"""
Image and PDF text extraction module for scraper.
Extracts text from images using OCR and PDFs using PyMuPDF.
"""

import io
import logging
import requests
from typing import Optional, List
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure tesseract path for Windows (you may need to adjust this)
# Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass  # Will use system PATH


def extract_text_from_image_url(image_url: str, timeout: int = 10) -> Optional[str]:
    """
    Download image from URL and extract text using OCR.
    
    Args:
        image_url: URL of the image
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text or None if failed
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Open image
        image = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image, lang='eng')
        
        # Clean extracted text
        text = text.strip()
        
        if text:
            logger.info(f"✓ Extracted {len(text)} chars from image: {image_url[:60]}...")
            return text
        else:
            logger.debug(f"No text found in image: {image_url}")
            return None
            
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract not installed. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return None
    except Exception as e:
        logger.warning(f"Failed to extract text from image {image_url}: {str(e)}")
        return None


def extract_text_from_image_file(image_path: str) -> Optional[str]:
    """
    Extract text from local image file using OCR.
    
    Args:
        image_path: Path to local image file
        
    Returns:
        Extracted text or None if failed
    """
    try:
        image = Image.open(image_path)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        text = pytesseract.image_to_string(image, lang='eng')
        text = text.strip()
        
        if text:
            logger.info(f"✓ Extracted {len(text)} chars from file: {image_path}")
            return text
        return None
        
    except Exception as e:
        logger.warning(f"Failed to extract text from file {image_path}: {str(e)}")
        return None


def extract_text_from_pdf_url(pdf_url: str, timeout: int = 30) -> Optional[str]:
    """
    Download PDF from URL and extract text using PyMuPDF.
    
    Args:
        pdf_url: URL of the PDF
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text or None if failed
    """
    try:
        # Download PDF
        response = requests.get(pdf_url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Open PDF from bytes
        pdf_document = fitz.open(stream=response.content, filetype="pdf")
        
        # Extract text from all pages
        extracted_text = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            if text.strip():
                extracted_text.append(text)
        
        pdf_document.close()
        
        full_text = "\n\n".join(extracted_text)
        
        if full_text.strip():
            logger.info(f"✓ Extracted {len(full_text)} chars from PDF: {pdf_url[:60]}... ({len(pdf_document)} pages)")
            return full_text
        else:
            logger.debug(f"No text found in PDF: {pdf_url}")
            return None
            
    except Exception as e:
        logger.warning(f"Failed to extract text from PDF {pdf_url}: {str(e)}")
        return None


def extract_text_from_pdf_file(pdf_path: str) -> Optional[str]:
    """
    Extract text from local PDF file using PyMuPDF.
    
    Args:
        pdf_path: Path to local PDF file
        
    Returns:
        Extracted text or None if failed
    """
    try:
        pdf_document = fitz.open(pdf_path)
        
        extracted_text = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            if text.strip():
                extracted_text.append(text)
        
        pdf_document.close()
        
        full_text = "\n\n".join(extracted_text)
        
        if full_text.strip():
            logger.info(f"✓ Extracted {len(full_text)} chars from PDF file: {pdf_path}")
            return full_text
        return None
        
    except Exception as e:
        logger.warning(f"Failed to extract text from PDF file {pdf_path}: {str(e)}")
        return None


def find_images_in_html(soup) -> List[str]:
    """
    Find all image URLs in BeautifulSoup parsed HTML.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        List of image URLs
    """
    image_urls = []
    
    # Find all img tags
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if src:
            image_urls.append(src)
    
    return image_urls


def find_pdfs_in_html(soup) -> List[str]:
    """
    Find all PDF URLs in BeautifulSoup parsed HTML.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        List of PDF URLs
    """
    pdf_urls = []
    
    # Find all links to PDFs
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
            pdf_urls.append(href)
    
    return pdf_urls
