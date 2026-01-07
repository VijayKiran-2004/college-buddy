import json
import os
import hashlib   


def chunk_hash(chunk, emb):   
    raw = chunk["text"] + str(emb["embedding"])
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


with open(r"data/chunks/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

with open(r"data/embeddings/chunks_embeddings.json", encoding="utf-8") as f:
    embeddings = json.load(f)

assert len(chunks) == len(embeddings), "Length mismatch!"


if os.path.exists(r"app\database\vectordb\unified_vectors.json"):
    with open(r"app\database\vectordb\unified_vectors.json", "r", encoding="utf-8") as f:
        old_merged = json.load(f)
else:
    old_merged = []


old_map = {}
for item in old_merged:
    h = chunk_hash(item, item)
    old_map[h] = item

merged = []

for i in range(len(chunks)):
    h = chunk_hash(chunks[i], embeddings[i])   
    if h in old_map:
        merged.append(old_map[h])    
    else:
        merged.append({              
            "chunk_id": f"chunk_{i:05d}",
            "text": chunks[i]["text"],
            "embedding": embeddings[i]["embedding"],
            "metadata": {
                "section": chunks[i]["section"],
                "source_url": chunks[i]["source_url"]
            }
        })


with open(r"app\database\vectordb\unified_vectors.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

print(f"Merged {len(merged)} records successfully")
