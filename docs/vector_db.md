# Vector Database Ingestion using ChromaDB

This project demonstrates how to **store text embeddings into a vector database** using **ChromaDB**, with support for **multiple data types** such as FAQs and web-scraped content.

The goal is to build a clean, scalable foundation for **semantic search** and **Retrieval-Augmented Generation (RAG)** systems.

---

## 📌 Problem Statement

We have two different types of data:

### 1️⃣ FAQ Data
- Short, direct Question–Answer pairs
- Each FAQ already has:
  - Question
  - Answer
  - Combined text (Question + Answer)
  - Precomputed embeddings

### 2️⃣ Web-Scraped Data
- Long-form content split into chunks
- Each chunk contains:
  - Text
  - Embedding
  - Metadata (section, source URL, etc.)

Since these two data types serve **different retrieval purposes**, they must be stored in **separate vector database collections**.

---

## 🧠 Why a Vector Database?

Traditional databases are not suitable for **semantic similarity search**.

A **vector database** allows us to:
- Store high-dimensional embedding vectors
- Perform fast similarity search using distance metrics
- Retrieve semantically relevant text instead of keyword matches

This is essential for:
- AI chatbots
- Question answering systems
- RAG pipelines
- Knowledge-base search

---

## 🚀 Why ChromaDB?

We use **ChromaDB** as our vector database for the following reasons:

### ✅ Simplicity
- Extremely easy to set up
- No external server required
- Ideal for learning, prototyping, and medium-scale production

### ✅ Native Support for RAG
- Stores **embeddings, documents, and metadata together**
- Perfect fit for Retrieval-Augmented Generation workflows

### ✅ Multiple Collections
- Allows clean separation of data:
  - `faqs_collection`
  - `webdocs_collection`

### ✅ Python-First
- Seamless integration with Python ML/NLP pipelines
- Works well with SentenceTransformers, OpenAI, HuggingFace, etc.

### ✅ Lightweight & Local
- Runs locally using DuckDB
- No cloud dependency unless required

---

## 🏗️ Project Structure

```text
vectordb-project/
│
├── faqs_embeddings.json          # FAQ embeddings JSON
├── web_chunks_embeddings.json    # Web-scraped chunks + embeddings + metadata
│
├── store_to_vectordb.py          # Script to store data into ChromaDB
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
