import json
import hashlib
import os
from datetime import datetime
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- Constants ---
HASH_FILE = './chroma/.scraped_data.hash'

# --- Initialize Components ---
# Lazy-loaded to avoid startup issues
embeddings = None
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=60)

def _get_embeddings():
    """Lazy-load embeddings to avoid startup failures."""
    global embeddings
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

def _calculate_hash(file_path: str) -> str:
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def _save_hash(file_path: str, file_hash: str):
    """Saves the hash to the specified file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(file_hash)

def _load_hash(file_path: str) -> str | None:
    """Loads the hash from the specified file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
    return None

def ingest_from_cache(cache_path: str):
    """
    Loads scraped content from a JSON file, splits it into chunks,
    and ingests it into the Chroma vector database only if the data has changed.
    """
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            scraped_docs = json.load(f)
    except FileNotFoundError:
        print(f"[loader] Error: Cache file not found at {cache_path}. Please run the cache_builder.py script first.")
        return
    except json.JSONDecodeError:
        print(f"[loader] Error: Could not decode JSON from {cache_path}. The file might be empty or corrupted.")
        return

    if not scraped_docs:
        print("[loader] Cache file is empty. No data to ingest.")
        return

    # Check if the data has changed
    current_hash = _calculate_hash(cache_path)
    stored_hash = _load_hash(HASH_FILE)

    if current_hash == stored_hash:
        print("[loader] Scraped data has not changed. Skipping ingestion.")
        return

    print("[loader] Scraped data has changed. Starting ingestion...")

    all_chunks = []
    for doc in scraped_docs:
        chunks = splitter.split_text(doc['content'])
        for i, chunk in enumerate(chunks):
            heading = f"section-{i+1}"
            # Handle both webpage and document sources
            metadata = {
                "source": doc.get('url', ''),
                "title": doc.get('page_name', doc.get('title', '')),
                "heading": heading,
                "last_scraped": datetime.utcnow().isoformat()
            }
            all_chunks.append(Document(page_content=chunk, metadata=metadata))
    
    if not all_chunks:
        print("[loader] No text chunks were generated from the cache. Nothing to ingest.")
        return

    vectordb = Chroma(collection_name="college_buddy",
                      embedding_function=_get_embeddings(),
                      persist_directory="./chroma")
    
    vectordb.add_documents(all_chunks)
    _save_hash(HASH_FILE, current_hash)
    print(f"[loader] Successfully ingested {len(all_chunks)} text chunks from {len(scraped_docs)} documents into the database.")

if __name__ == "__main__":
    ingest_from_cache('scraped_data.json')