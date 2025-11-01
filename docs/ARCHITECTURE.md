# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│  GitHub Pages (Frontend)                                        │
│  • HTML5 + JavaScript + Tailwind CSS                           │
│  • Web Speech API (Voice Input)                                │
│  • Speech Synthesis API (Voice Output)                         │
│  • WebSocket Client                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ WebSocket (wss://)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND SERVER (Render)                      │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI + WebSocket                                            │
│  • main.py (Server entry point)                                │
│  • WebSocket handler (/chat endpoint)                          │
│  • Rate limiting (10 req/min)                                  │
│  • Session management                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM (Core Logic)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Query Processing (text_processor.py)                        │
│     ├── Language detection                                      │
│     ├── Entity extraction                                       │
│     ├── Typo correction                                        │
│     └── Query normalization                                     │
│                                                                  │
│  2. Vector Retrieval (retriever.py)                            │
│     ├── Topic classification (13 categories)                   │
│     ├── Query expansion (synonyms)                             │
│     ├── Semantic search (ChromaDB)                             │
│     └── Context ranking                                         │
│                                                                  │
│  3. Response Generation (chain.py)                             │
│     ├── LangChain orchestration                                │
│     ├── Gemini AI (gemini-2.5-flash)                          │
│     ├── Context injection                                       │
│     └── Tone adjustment                                         │
│                                                                  │
│  4. Clarification Handling (enhanced_matcher.py)               │
│     ├── Fuzzy matching                                         │
│     ├── Context preservation                                    │
│     └── Option selection (a/b/c or 1/2/3)                     │
│                                                                  │
└────────────────┬────────────────┬───────────────────────────────┘
                 │                │
                 ↓                ↓
┌────────────────────────┐  ┌──────────────────────────────────┐
│   VECTOR DATABASE      │  │      EXTERNAL AI SERVICE         │
│   (ChromaDB)           │  │      (Google Gemini API)         │
├────────────────────────┤  ├──────────────────────────────────┤
│ • 1,748 documents      │  │ • Model: gemini-2.5-flash       │
│ • 92.12 MB storage     │  │ • Context: 8,192 tokens         │
│ • Embeddings:          │  │ • Temperature: 0.7              │
│   all-MiniLM-L6-v2     │  │ • Max tokens: 2,048             │
│                        │  │ • Rate limit: 60 req/min        │
│ Data Sources:          │  └──────────────────────────────────┘
│ ├── 93 Website pages   │
│ ├── 1,648 Students     │
│ └── 7 Branch stats     │
└────────────────────────┘
         ↑
         │ Data Ingestion
         │
┌────────────────────────────────────────────────────────────────┐
│              WEB SCRAPING & DATA PIPELINE                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Data Sources                                               │
│     ├── structured_links.csv (92 URLs)                         │
│     ├── Student data Excel (1,648 records)                     │
│     └── Alumni Project Links Data                              │
│                                                                 │
│  2. Scrapy Spider (scrapy_scraper.py)                         │
│     ├── Concurrent requests (10 simultaneous)                  │
│     ├── Rate limiting (0.5s delay)                            │
│     ├── BeautifulSoup parser                                   │
│     └── PDF + HTML extraction                                  │
│                                                                 │
│  3. Data Processing (preprocess_student_data.py)              │
│     ├── Excel → CSV conversion                                 │
│     ├── Data cleaning (nulls, duplicates)                     │
│     ├── Branch name expansion                                  │
│     └── Statistics generation                                  │
│                                                                 │
│  4. Vector Store Builder (create_vector_store.py)             │
│     ├── Document loading                                       │
│     ├── Text chunking                                          │
│     ├── Embedding generation                                   │
│     └── ChromaDB indexing                                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

### User Query Flow
```
User types question
    ↓
Frontend captures input
    ↓
WebSocket sends JSON: {"query": "...", "session_id": "..."}
    ↓
Backend receives message
    ↓
Text Processor: Clean & normalize query
    ↓
Topic Classifier: Identify category (admissions/courses/etc.)
    ↓
Query Expander: Add synonyms
    ↓
Vector Retriever: Search ChromaDB for relevant docs
    ↓
Context Builder: Rank & select top docs
    ↓
LangChain: Inject context into prompt
    ↓
Gemini AI: Generate response
    ↓
Tone Adjuster: Make response friendly
    ↓
WebSocket sends JSON: {"response": "...", "sources": [...]}
    ↓
Frontend displays answer
    ↓
Speech Synthesis: Read aloud (if enabled)
```

### Clarification Flow
```
User query is ambiguous
    ↓
Retriever finds multiple relevant topics
    ↓
Generate clarification options (a/b/c/d)
    ↓
Send options to user
    ↓
User responds with letter/number
    ↓
Enhanced Matcher: Fuzzy match user input
    ↓
Context preserved from previous turn
    ↓
Retrieve specific topic
    ↓
Generate targeted response
```

## Technology Stack

### Frontend Layer
- **Hosting**: GitHub Pages (free CDN)
- **Framework**: Vanilla JavaScript (no build step)
- **Styling**: Tailwind CSS (CDN)
- **Voice**: Web Speech API, Speech Synthesis API
- **Communication**: WebSocket

### Backend Layer
- **Server**: FastAPI 0.100+
- **ASGI**: Uvicorn
- **WebSocket**: Native FastAPI support
- **Rate Limiting**: SlowAPI
- **Caching**: In-memory + JSON file

### AI/ML Layer
- **LLM**: Google Gemini (gemini-2.5-flash)
- **Orchestration**: LangChain
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
  - Primary: all-MiniLM-L6-v2
  - Fallback: BAAI/bge-small-en

### Data Layer
- **Scraping**: Scrapy 2.13+ (primary)
- **Parsing**: BeautifulSoup 4.14+ (fallback)
- **Processing**: Pandas 2.3+, NumPy 1.26+
- **Storage**: JSON, CSV, SQLite (via ChromaDB)

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    GitHub Pages                           │
│  https://vijaykiran-2004.github.io/college-buddy/        │
│                                                           │
│  • Static files (HTML/CSS/JS)                            │
│  • Served via GitHub CDN                                 │
│  • Free, unlimited bandwidth                             │
│  • Auto-deploy on push to main/docs                      │
└─────────────────────┬────────────────────────────────────┘
                      │
                      │ WebSocket Connection
                      │
┌─────────────────────▼────────────────────────────────────┐
│                   Render.com                              │
│  https://college-buddy.onrender.com                      │
│                                                           │
│  • Python runtime                                         │
│  • Auto-deploy from GitHub                               │
│  • Free tier: 750 hrs/month                              │
│  • Persistent storage (vector DB)                        │
│  • Environment variables (API keys)                      │
└───────────────────────────────────────────────────────────┘
```

## Security

### API Key Management
- ✅ Environment variables (`.env`)
- ✅ Never committed to git (`.gitignore`)
- ✅ Render secret management

### Rate Limiting
- ✅ 10 requests per minute per IP
- ✅ Prevents abuse
- ✅ Protects Gemini API quota

### CORS
- ✅ Configured for GitHub Pages origin
- ✅ WebSocket secure (wss://)

### Data Privacy
- ❌ No user data stored permanently
- ✅ Session IDs for context only
- ✅ Analytics anonymized

## Scalability

### Current Capacity
- **Vector DB**: 1,748 documents (can handle 100K+)
- **Concurrent users**: 100+ tested
- **Response time**: 2-3 seconds avg
- **Database size**: 92 MB (can grow to GB)

### Bottlenecks
1. **Gemini API**: 60 req/min limit
2. **Render free tier**: Goes to sleep after 15 min inactivity
3. **Vector search**: Linear with DB size (manageable up to 100K docs)

### Scaling Options
1. **Caching**: Implement Redis for responses
2. **Load balancing**: Multiple backend instances
3. **DB sharding**: Split vector DB by topic
4. **CDN**: Already using GitHub Pages
5. **Paid tiers**: Render Pro ($7/mo), Gemini Enterprise

## Monitoring

### Metrics to Track
- Response time (p50, p95, p99)
- Error rate
- Gemini API usage
- Vector DB query performance
- User session duration
- Most asked questions

### Logging
- Backend: Python logging module
- Analytics: `analytics_data.json`
- Errors: Console + file logging

---

## Future Enhancements

### Short Term
- [ ] Add Redis caching layer
- [ ] Implement query deduplication
- [ ] Add user feedback loop
- [ ] Create admin dashboard

### Medium Term
- [ ] Multi-language responses (Telugu, Hindi)
- [ ] Image search integration
- [ ] Mobile app (React Native)
- [ ] Advanced analytics

### Long Term
- [ ] Custom fine-tuned model
- [ ] Real-time data updates
- [ ] Integration with college ERP
- [ ] Voice-first interface
