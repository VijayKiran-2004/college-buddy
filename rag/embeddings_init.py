from langchain_huggingface import HuggingFaceEmbeddings
import time
from pathlib import Path
import logging
import os

def init_embeddings(retries=3, delay=2):
    """Initialize HuggingFace embeddings with retries and error handling."""
    cache_dir = Path.home() / ".cache" / "huggingface"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["HF_HUB_OFFLINE"] = "1"  # Force offline mode
    
    for attempt in range(retries):
        try:
            return HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-en",
                model_kwargs={'device': 'cpu', 'local_files_only': True},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            if attempt == retries - 1:  # Last attempt
                # Try fallback model
                logging.warning("Trying fallback model: all-MiniLM-L6-v2")
                try:
                    return HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        model_kwargs={'device': 'cpu', 'local_files_only': True},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                except:
                    raise Exception(f"Failed to initialize embeddings after {retries} attempts: {e}")
            logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff