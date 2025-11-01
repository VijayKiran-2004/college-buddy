# Changelog

All notable changes to College Buddy will be documented in this file.

## [Unreleased]

### Added
- GitHub Pages frontend deployment
- Split architecture (frontend on GitHub Pages, backend on Render)
- Scrapy-based web scraping with BeautifulSoup fallback
- Structured links CSV with 92 URLs (79 HTML + 13 PDFs)
- Student data preprocessing (1,648 records)
- Branch statistics for 7 departments

## [2.0.0] - 2025-11-01

### Added
- RAG (Retrieval Augmented Generation) system with ChromaDB
- Vector database with 1,748 documents (92.12 MB)
- Scrapy web scraper for efficient concurrent scraping
- Student data integration (1,648 students, 7 branches)
- BeautifulSoup fallback for complex HTML parsing
- Dynamic CSV reading for URLs
- Enhanced context-aware clarifications
- Fuzzy matching for follow-up questions

### Changed
- Migrated from simple requests to Scrapy framework
- Improved scraping architecture (Scrapy-first, BeautifulSoup fallback)
- Enhanced query processing with NLP
- Better error handling and logging

### Fixed
- Type hint errors in scrapy_scraper.py
- Removed dead code and redundant functions
- Cleaned up import statements

## [1.0.0] - Initial Release

### Added
- FastAPI backend with WebSocket support
- Google Gemini AI integration
- Voice input/output (Web Speech API)
- Responsive chat interface
- Multi-language support (English, Telugu, Hindi)
- Response caching
- Analytics system
- Rate limiting
- Feedback collection

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
