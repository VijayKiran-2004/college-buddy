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
The core engine uses a sophisticated **Hybrid Retrieval Pipeline**:
- **Step 1: Query Processing**: The user's query is analyzed for clarity. If vague, the system asks for clarification.
- **Step 2: Hybrid Search**:
  - **Dense Vector Search**: Uses `sentence-transformers/all-MiniLM-L6-v2` to encode the query into a 384-dimensional vector. FAISS (`IndexFlatL2`) performs a nearest-neighbor search to retrieve the top 5 semantic matches.
  - **Sparse Keyword Search**: Uses `rank_bm25` (Okapi BM25) to retrieve the top 5 exact keyword matches.
- **Step 3: Reciprocal Rank Fusion (RRF)**: Results from FAISS and BM25 are combined to ensure both semantic understanding and keyword precision.
- **Step 4: Reranking**: The top 10 fused results are passed to a Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`), which scores each document-query pair. The top 5 highest-scoring chunks are selected for the context window.

### 2. Fallback Mechanism (`app/services/chain.py`)
A deterministic backup system designed for **100% reliability** when the LLM is unavailable.
- **Query Classification**: Uses keyword matching to categorize queries into `person`, `timing`, `admission`, `contact`, or `general`.
- **Pattern Extraction**:
  - **Person Queries**: Scans for honorifics (`Dr.`, `Prof.`) and titles (`HOD`, `Principal`, `Dean`). It extracts full sentences containing these patterns to ensure context is preserved.
  - **Timing/Contact**: Looks for specific markers like `:`, `am`, `pm`, `@`, `phone`.
- **Response Generation**: Assembles extracted facts into a bulleted list, bypassing the generative model entirely.

### 3. Vector Store (`app/database/vectordb/unified_vectors.json`)
The centralized knowledge repository.
- **Storage Format**: A 35MB+ JSON file containing over 2,000 text chunks.
- **Schema**:
  ```json
  {
    "chunk_id": "chunk_001",
    "text": "Dr. A. Suresh Rao is the HOD of CSE...",
    "embedding": [-0.023, 0.145, ...], // 384 floats
    "metadata": { "source": "tkrcet.ac.in", "title": "Faculty" }
  }
  ```
- **Performance**: Embeddings are loaded into a FAISS index in RAM for O(1) search complexity, while text is indexed by ID for O(1) retrieval.

### 4. Prompt Engineering (`app/services/prompt_construction.py`)
Uses **Dynamic Context Injection** to control LLM behavior.
- **Anti-Hallucination Protocol**: For "Who is" queries, the system injects a strict system prompt:
  > "CRITICAL: ONLY use names that appear in the context. DO NOT invent names. If you don't see a name, say you don't have that information."
- **Context Formatting**: Retrieved chunks are formatted as bullet points with explicit separation to prevent information bleeding.
- **Tone Control**: Instructions guide the LLM to be "friendly and conversational" for general queries, but "direct and factual" for official inquiries.

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
