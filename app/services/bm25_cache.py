import pickle
import os

def save_bm25_index(bm25, file_path):
    """Saves a BM25 index to a file."""
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'wb') as f:
        pickle.dump(bm25, f)

def load_bm25_index(file_path):
    """Loads a BM25 index from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return None
