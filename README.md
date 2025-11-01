# 🎓 College Buddy - TKRCET AI Chatbot

An intelligent AI-powered chatbot for Teegala Krishna Reddy College of Engineering and Technology (TKRCET) that helps students get instant answers about admissions, courses, faculty, facilities, and more.

## ✨ Features

- 🤖 **AI-Powered Responses**: Uses RAG (Retrieval Augmented Generation) with Gemini AI
- 🎤 **Voice Input**: Multi-language voice search (English, Telugu, Hindi)
- 🔊 **Voice Response**: Natural text-to-speech with adjustable speed
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- ⚡ **Fast & Smart**: Intelligent caching and response optimization
- 🎯 **Student-Friendly**: Conversational, warm, and helpful responses
- 📊 **Analytics**: Background query analysis for continuous improvement

## 🚀 Tech Stack

- **Backend**: Python, FastAPI, WebSocket
- **AI/ML**: Google Gemini API (gemini-2.5-flash), LangChain
- **RAG System**: Retrieval Augmented Generation with ChromaDB vector store
- **Vector Embeddings**: Sentence Transformers (BAAI/bge-small-en, all-MiniLM-L6-v2)
- **Web Scraping**: Scrapy (primary), BeautifulSoup (fallback), concurrent processing
- **Data Processing**: Pandas, NumPy, OpenPyXL for student data preprocessing
- **Frontend**: HTML5, JavaScript, Tailwind CSS
- **Voice**: Web Speech API, Speech Synthesis API

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API Key

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd college-buddy
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Run the server:
```bash
python main.py
```

6. Open your browser to `http://localhost:8001`

## 🌐 Deployment

### Deploy to Render

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: college-buddy
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
6. Add Environment Variable: `GEMINI_API_KEY`
7. Click "Create Web Service"

Your bot will be live at: `https://college-buddy.onrender.com`

## 📁 Project Structure

```
college-buddy/
├── main.py                      # FastAPI server with WebSocket
├── rag/                         # RAG (Retrieval Augmented Generation) system
│   ├── chain.py                # LangChain response generation with Gemini
│   ├── retriever.py            # ChromaDB vector retrieval & query expansion
│   ├── text_processor.py       # NLP query processing & entity extraction
│   ├── enhanced_matcher.py     # Fuzzy matching for clarifications
│   ├── rules.py                # Conversational tone rules
│   └── create_vector_store.py  # Vector DB builder (1,748 documents)
├── scraper/                     # Web scraping & data ingestion
│   ├── scrapy_scraper.py       # Scrapy spider with BeautifulSoup parser
│   ├── cache_builder.py        # Scraping orchestrator (Scrapy-first)
│   ├── loader.py               # Document loader for ChromaDB
│   └── doc_loader.py           # Word document ingestion
├── Student data/                # Student records (1,648 students)
│   ├── students_processed.json # Preprocessed student data
│   ├── branch_statistics.json  # Department statistics (7 branches)
│   └── student_data_cleaned.csv# Cleaned student dataset
├── static/                      # Frontend
│   └── index.html              # Chat interface with voice support
├── structured_links.csv         # 92 URLs for scraping (79 HTML + 13 PDFs)
├── scraped_data.json           # Scraped website content
├── chroma/                      # ChromaDB vector database (92.12 MB)
├── requirements.txt             # Python dependencies
└── .env                        # Environment variables (API keys)
```

## 🎯 Usage

1. **Text Chat**: Type your question in the input box
2. **Voice Input**: Click the microphone icon or press Alt+V
3. **Voice Response**: Enable "Voice Response" in settings
4. **Adjust Speed**: Use the voice speed slider (0.7x - 1.5x)

## 🔧 Configuration

Edit `.env` file:
```env
GEMINI_API_KEY=your_api_key
PORT=8001
```

## 📊 Features in Detail

### RAG (Retrieval Augmented Generation) System
- **Vector Database**: ChromaDB with 1,748 documents (92.12 MB)
  - 93 scraped website pages (college info, departments, admissions)
  - 1,648 student records with CGPA, placements, branch data
  - 7 branch statistics (CSE, EEE, ECE, MECH, CIVIL, IT, MBA)
- **Intelligent Retrieval**: 13 topic categories with semantic search
- **Query Expansion**: Automatic synonym expansion for better matching
- **Context-Aware**: Clarification-aware follow-up question handling
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)

### Web Scraping Architecture
- **Primary Method**: Scrapy with concurrent requests (10 simultaneous)
- **Fallback Parser**: BeautifulSoup for complex HTML and PDFs
- **Rate Limiting**: 0.5s delay, automatic retries, custom user agent
- **Data Sources**: 92 URLs (79 HTML pages + 13 PDF documents)
- **Performance**: 5x faster than sequential scraping

### Smart Retrieval
- 13 topic categories with intelligent query expansion
- Semantic search with ChromaDB vector database
- Context-aware response generation

### Voice System
- Multi-language support (English, Telugu, Hindi)
- Perfect text-voice synchronization
- Natural voice selection (Neural/Premium voices)
- Adjustable speech speed

### Student-Friendly
- All responses enhanced through Gemini for warm, conversational tone
- Encouraging and supportive language
- Clear, concise answers with helpful links

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👥 Contact

For questions or support, please contact the TKRCET IT department.

---

**Made with ❤️ for TKRCET Students**
