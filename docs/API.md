# API Documentation

## WebSocket Endpoint

### Connect to Chat

**Endpoint:** `ws://localhost:8001/chat` or `wss://your-domain.com/chat`

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8001/chat');
```

**Message Format (Client → Server):**
```json
{
    "query": "Tell me about CSE department",
    "session_id": "user-session-123"
}
```

**Response Format (Server → Client):**
```json
{
    "response": "The Computer Science and Engineering department...",
    "clarifications": null,
    "sources": ["https://tkrcet.ac.in/cse/", "student_records"],
    "timestamp": "2025-11-01T10:30:00"
}
```

**Clarification Response:**
```json
{
    "response": "I found multiple topics. What would you like to know?",
    "clarifications": [
        "a) CSE Department Overview",
        "b) CSE Course Structure", 
        "c) CSE Faculty Details",
        "d) CSE Placements"
    ]
}
```

**Follow-up (Client → Server):**
```json
{
    "query": "a",
    "session_id": "user-session-123"
}
```

---

## REST Endpoints

### Health Check

**GET** `/`

**Response:**
```json
{
    "status": "ok",
    "message": "College Buddy API is running",
    "version": "2.0.0"
}
```

---

## Error Handling

**Connection Error:**
```json
{
    "error": "connection_failed",
    "message": "Failed to connect to server"
}
```

**Query Error:**
```json
{
    "error": "query_processing_failed",
    "message": "Unable to process your question"
}
```

**Rate Limit:**
```json
{
    "error": "rate_limit_exceeded",
    "message": "Too many requests. Please try again in 60 seconds."
}
```

---

## RAG System Internals

### Query Processing Pipeline

1. **Text Preprocessing** (`text_processor.py`)
   - Language detection
   - Entity extraction
   - Query normalization
   - Typo correction

2. **Vector Retrieval** (`retriever.py`)
   - Topic classification (13 categories)
   - Query expansion with synonyms
   - Semantic search in ChromaDB
   - Context ranking

3. **Response Generation** (`chain.py`)
   - LangChain + Gemini integration
   - Context-aware generation
   - Tone adjustment (friendly, student-focused)
   - Source citation

4. **Clarification Handling** (`enhanced_matcher.py`)
   - Fuzzy matching for user responses
   - Context preservation across turns
   - Option selection (a/b/c or 1/2/3)

### Vector Database Schema

**Document Types:**
- `website_pages`: Scraped college website content
- `student_records`: Individual student data
- `branch_statistics`: Department-level statistics

**Metadata Fields:**
```python
{
    "source": "website_pages | student_records | branch_statistics",
    "title": "Page title or student name",
    "url": "Source URL (for website pages)",
    "roll_no": "Student roll number (for students)",
    "branch": "Department code (CSE, EEE, etc.)"
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | None |
| `PORT` | Server port | 8001 |
| `HOST` | Server host | 0.0.0.0 |
| `DEBUG` | Enable debug mode | False |

### Rate Limiting

- **Default**: 10 requests per minute per IP
- **Configurable** in `main.py`

---

## Data Sources

### 1. Website Scraping
- **Source**: `structured_links.csv` (92 URLs)
- **Content**: College info, departments, admissions, placements
- **Update frequency**: Manual (run scraper when website changes)

### 2. Student Data
- **Source**: `Student data/Final_student_dataset.xlsx`
- **Records**: 1,648 students
- **Fields**: Roll no, name, branch, CGPA, placement status
- **Update frequency**: Annually

### 3. Branch Statistics
- **Generated from**: Student data
- **Departments**: 7 (CSE, EEE, ECE, MECH, CIVIL, IT, MBA)
- **Metrics**: Student count, average CGPA, placement rate

---

## Testing

### Test WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8001/chat');

ws.onopen = () => {
    console.log('Connected!');
    ws.send(JSON.stringify({
        query: "Hello",
        session_id: "test-session"
    }));
};

ws.onmessage = (event) => {
    console.log('Response:', JSON.parse(event.data));
};
```

### Test with curl (HTTP upgrade)
```bash
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://localhost:8001/chat
```

---

## Performance

### Metrics
- **Response time**: ~2-3 seconds (including AI generation)
- **Vector search**: <100ms
- **Concurrent users**: 100+ (tested)
- **Database size**: 92.12 MB
- **Memory usage**: ~500 MB (with vector DB loaded)

### Optimization Tips
1. Enable response caching (`response_cache.json`)
2. Use connection pooling
3. Implement query deduplication
4. Cache frequently asked questions
5. Use CDN for frontend (GitHub Pages)

---

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Rebuilding Vector Database
```bash
# After updating scraped data or student records
python rag/create_vector_store.py
```

### Re-scraping Website
```bash
# Using Scrapy (recommended)
python scraper/scrapy_scraper.py

# Using BeautifulSoup fallback
python scraper/cache_builder.py
```

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/VijayKiran-2004/college-buddy/issues
- **Email**: info@tkrcet.ac.in
