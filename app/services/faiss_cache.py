import faiss
import numpy as np
import os

def save_faiss_index(index, file_path):
    """Saves a FAISS index to a file."""
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    faiss.write_index(index, file_path)

def load_faiss_index(file_path):
    """Loads a FAISS index from a file."""
    if os.path.exists(file_path):
        return faiss.read_index(file_path)
    return None
