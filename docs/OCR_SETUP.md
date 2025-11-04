# Image OCR Setup Guide

## Install Tesseract OCR (Required for Image Text Extraction)

### Windows:
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (tesseract-ocr-w64-setup-5.x.x.exe)
3. Install to default location: `C:\Program Files\Tesseract-OCR`
4. Tesseract will be automatically detected by the scraper

### Alternative: Add to PATH manually
If installed to a different location, update the path in `scraper/image_processor.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'YOUR_TESSERACT_PATH\tesseract.exe'
```

## Running Enhanced Scraper

After installing Tesseract:

```bash
# Run the enhanced cache builder with image OCR
python scraper/enhanced_cache_builder.py
```

This will:
- Extract text from web pages
- Extract text from images using OCR (tables, diagrams, infographics)
- Extract text from PDF documents
- Save enriched content to data/scraped/scraped_data.json

Then restart the backend to rebuild the vector database:
```bash
python main.py
```

## What Gets Extracted

✅ **Text Content**: All visible text from web pages
✅ **Image OCR**: Text from images (accreditation certificates, tables, diagrams)
✅ **PDF Content**: Full text from linked PDF documents
✅ **Tables**: Text from table images and screenshots

This solves queries about:
- Autonomy status (often shown in certificates/images)
- Accreditation details (in certificate images)
- Complex tables (placement statistics, fee structures)
- Scanned documents (prospectus, brochures)
