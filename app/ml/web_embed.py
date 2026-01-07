import json
import os
import hashlib
from sentence_transformers import SentenceTransformer

INPUT_FILE = "data/chunks/chunks.json"
OUTPUT_FILE = "data/embeddings/chunks_embeddings.json"
HASH_MAP_FILE = "data/embeddings/embedding_hash_map.json"

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

def text_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)


if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        old_embeddings = json.load(f)
else:
    old_embeddings = []


old_hash_map = {}
for item in old_embeddings:
    h = text_hash(item["text"])
    old_hash_map[h] = item["embedding"]


if os.path.exists(HASH_MAP_FILE):
    with open(HASH_MAP_FILE, "r", encoding="utf-8") as f:
        old_hashes = json.load(f)
else:
    old_hashes = {}

new_output = []
texts_to_embed = []
chunk_indexes = []

for idx, c in enumerate(chunks):
    t = c["text"]
    h = text_hash(t)

    
    if h in old_hash_map:
        c["embedding"] = old_hash_map[h]
        new_output.append(c)
    else:
        
        texts_to_embed.append(t)
        chunk_indexes.append(idx)
        new_output.append(c)


if texts_to_embed:
    print(f"Embedding {len(texts_to_embed)} new/updated chunks...")
    new_embeddings = model.encode(
        texts_to_embed,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    
    for i, emb in zip(chunk_indexes, new_embeddings):
        h = text_hash(chunks[i]["text"])
        new_output[i]["embedding"] = emb.tolist()
        old_hash_map[h] = emb.tolist()
else:
    print("No new chunks to embed. Reusing all previous embeddings.")


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(new_output, f, indent=2)


with open(HASH_MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(old_hash_map, f, indent=2)

print("Idempotent embeddings generation completed.")
