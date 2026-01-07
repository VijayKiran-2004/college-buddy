# College Buddy - AI Powered Campus Assistant

## Overview
College Buddy is an intelligent conversational AI designed to assist students, faculty, and visitors of TKRCET. It uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers about college departments, faculty, placements, and campus life.

## Key Features
- 🧠 **Advanced RAG Architecture**: Combines vector search (FAISS) with keyword search (BM25) for high-precision retrieval.
- 🤖 **Efficient LLM**: Powered by **Gemma 3 1B**, optimized for speed and low memory usage.
- 🛡️ **Anti-Hallucination**: Built-in safeguards to prevent inventing names or facts.
- 👥 **Faculty Intelligence**: Specialized handling for "Who is..." queries to provide complete details about HODs and Principals.
- ⚡ **Fast & Lightweight**: Runs efficiently on local hardware.

## Tech Stack
- **Language**: Python 3.8+
- **LLM**: Google Gemma 3 1B (via Ollama)
- **Embeddings**: all-MiniLM-L6-v2
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Reranker**: Cross-Encoder (ms-marco-MiniLM-L-6-v2)
- **Backend**: Custom RAG Pipeline

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/VijayKiran-2004/college-buddy.git
cd college-buddy
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Ollama & Model
1. Download and install [Ollama](https://ollama.com/)
2. Pull the required model:
```bash
ollama pull gemma3:1b
```

### 5. Run the Chatbot
```bash
python terminal_chat.py
```

## Project Structure

The project is organized into modular components for scalability and maintainability:

```
college-buddy/
├── app/
│   ├── services/
│   │   ├── rag_system.py         # Core RAG pipeline (Search + Rerank + Generate)
│   │   ├── chain.py              # Fallback logic & Chain of Thought generator
│   │   ├── prompt_construction.py # Context-aware prompt engineering
│   │   └── bm25_cache.py         # Caching for BM25 search index
│   ├── database/
│   │   └── vectordb/             # FAISS index & BM25 index files
│   └── scraper/                  # Web scraping utilities
│
├── data/
│   ├── chunks/                   # JSON files containing text chunks
│   ├── embeddings/               # Pre-computed vector embeddings
│   ├── scraped_data/             # Raw HTML/Text from college website
│   └── datasets/                 # Cleaned and structured datasets
│
├── scripts/
│   └── clean_webdata.py          # Data cleaning & preprocessing scripts
│
├── docs/                         # Technical documentation
│   ├── rag.md                    # RAG architecture details
│   └── vector_db.md              # Vector database schema
│
├── terminal_chat.py              # Main Entry Point (Run this to start)
├── unified_vectors.json          # Master vector store (Text + Embeddings + Metadata)
├── students.db                   # SQLite database for student records
├── run_data_pipeline.py          # Script to rebuild indices and process data
└── requirements.txt              # Python dependencies
```

## Component Details

### 1. RAG System (`app/services/rag_system.py`)
The heart of the chatbot. It orchestrates:
- **Hybrid Search**: Combines dense vector search (FAISS) with sparse keyword search (BM25).
- **Reranking**: Uses a Cross-Encoder to re-score top results for higher relevance.
- **Generation**: Sends context + query to the Ollama LLM.

### 2. Fallback Mechanism (`app/services/chain.py`)
Ensures reliability when the LLM is offline or fails.
- Uses `SimpleRAGResponder` to generate answers directly from retrieved documents.
- Implements "Chain of Thought" logic to extract key information without an LLM.

### 3. Vector Store (`unified_vectors.json`)
A massive JSON file acting as the central knowledge base. It contains:
- Text content
- Vector embeddings (384 dimensions)
- Metadata (Source URL, Title, Type)

### 4. Prompt Engineering (`app/services/prompt_construction.py`)
Dynamically builds prompts based on query type:
- **Person Queries**: Enforces strict anti-hallucination rules.
- **General Queries**: Optimizes for helpfulness and breadth.

## Team Roles
- **Vijay Kiran**: RAG Architecture & System Integration
- **Sanjana**: Data Pipeline & Chunking
- **Subhash Chandra**: Embeddings & SQL
- **Sathish**: Vector Database Optimization
- **Mokshagna**: LLM Integration
- **Vishnuvardhan**: Prompt Engineering
- **Praneetha**: Fine-Tuning & Evaluation

## License
This project is developed for academic purposes.
