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

## Prerequisites

- **OS**: Windows, Linux, or macOS
- **Python**: 3.8, 3.9, 3.10, or 3.11 (Python 3.12+ may have issues with some ML libraries)
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: ~2GB for models and data
- **Software**: 
  - [Ollama](https://ollama.com/) (Required for LLM)
  - [Git](https://git-scm.com/)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/VijayKiran-2004/college-buddy.git
cd college-buddy
```

### 2. Create Virtual Environment
It's critical to use a virtual environment to avoid conflicts.
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Ollama (Critical Step)
The chatbot relies on Ollama running locally.
1. Download and install [Ollama](https://ollama.com/).
2. Open a terminal and pull the optimized model:
   ```bash
   ollama pull gemma3:1b
   ```
3. Keep Ollama running in the background.

### 5. Run the Chatbot
```bash
python terminal_chat.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **ConnectionRefusedError** | Ensure Ollama is running (`ollama serve` or check system tray). |
| **Model not found** | Run `ollama pull gemma3:1b` to download the model. |
| **Out of Memory** | Close other apps. The `gemma3:1b` model uses ~800MB RAM. |
| **ImportError: DLL load failed** | Install MSVC runtime or reinstall `faiss-cpu`. |

## Data Flow
1. **User Query** → `terminal_chat.py`
2. **Hybrid Search** (`rag_system.py`):
   - **Vector Search**: Finds semantically similar chunks (FAISS).
   - **Keyword Search**: Finds exact matches (BM25).
3. **Reranking**: Top 10 results are re-scored using a Cross-Encoder.
4. **Prompt Building**: Best 5 chunks are formatted into a prompt.
5. **Generation**: Prompt sent to Ollama (`gemma3:1b`) for final answer.


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
│   └── database/
│       └── vectordb/
│           ├── unified_vectors.json  # Master vector store (Text + Embeddings + Metadata)
│           ├── faiss_index.bin       # FAISS index
│           └── bm25_index.pkl        # BM25 index
│
├── docs/                         # Technical documentation
│   ├── rag.md                    # RAG architecture details
│   └── vector_db.md              # Vector database schema
│
├── terminal_chat.py              # Main Entry Point (Run this to start)
└── requirements.txt              # Python dependencies
```

## Component Details

### 1. RAG System (`app/services/rag_system.py`)
The core engine that powers the chatbot's intelligence. It uses a multi-stage retrieval process:
- **Hybrid Search**: 
  - **Dense Retrieval**: Uses `all-MiniLM-L6-v2` embeddings with FAISS to find semantically similar concepts (e.g., "fees" matches "tuition").
  - **Sparse Retrieval**: Uses BM25 to find exact keyword matches (e.g., specific names like "Dr. Suresh Rao").
- **Reranking**: The top 10 results from hybrid search are re-scored using a Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`). This ensures that the most contextually relevant documents appear at the top, filtering out noise.
- **Generation**: The top 5 reranked chunks are injected into a prompt and sent to the `gemma3:1b` LLM via Ollama for final answer synthesis.

### 2. Fallback Mechanism (`app/services/chain.py`)
A robust safety net that ensures the chatbot works even if the LLM fails (e.g., connection timeout or 500 error).
- **Trigger**: Automatically activates if Ollama is unreachable or returns an error.
- **Logic**: Uses a deterministic "Chain of Thought" approach to analyze retrieved documents.
- **Extraction**: Scans text for specific patterns (e.g., "Dr.", "Professor", dates, times) to construct a coherent answer without generating new text.
- **Benefit**: Guarantees zero hallucinations and high availability.

### 3. Vector Store (`app/database/vectordb/unified_vectors.json`)
The centralized knowledge base of the application.
- **Structure**: A large JSON array where each object represents a text chunk.
- **Content**: 
  - `text`: The actual content from the college website.
  - `embedding`: A 384-dimensional vector representation of the text.
  - `metadata`: Source URL, page title, and chunk ID.
- **Loading**: On startup, embeddings are loaded into a FAISS index for sub-millisecond similarity search, while text is kept in memory for retrieval.

### 4. Prompt Engineering (`app/services/prompt_construction.py`)
The module responsible for communicating with the LLM. It dynamically builds prompts to maximize accuracy and minimize hallucinations.
- **Person Queries**: Detects questions about staff (HODs, Principals). Adds strict instructions: *"ONLY use names from context. DO NOT invent names."* This prevents the LLM from hallucinating fake names.
- **General Queries**: Uses a more relaxed prompt structure to encourage helpful, conversational responses about campus life and facilities.
- **Context Injection**: Automatically formats retrieved documents into bullet points (`•`) to help the LLM distinguish between separate pieces of information.

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
