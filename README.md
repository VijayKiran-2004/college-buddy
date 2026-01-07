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
```
college-buddy/
├── app/
│   ├── services/         # RAG, Chain, Prompt Construction
│   └── database/         # Vector DB & SQLite
├── data/                 # Raw & Processed Data
├── docs/                 # Documentation
├── terminal_chat.py      # Main Entry Point
├── unified_vectors.json  # Vector Store
└── requirements.txt      # Dependencies
```

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
