import json
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import hashlib   

def text_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

print(" Loading BGE-Large model...")
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

file_path = "data/datasets/faq_rows.json"

print(" Loading FAQ JSON...")
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

question_col = df.columns[0]
answer_col   = df.columns[1]

print("Detected columns:", question_col, answer_col)

df = df.dropna(subset=[question_col, answer_col])

faqs = (
    df[question_col].astype(str)
    + " | ANSWER: "
    + df[answer_col].astype(str)
).tolist()

print(f"Total FAQs processed: {len(faqs)}")

OUTPUT_FILE = "data/embeddings/faq_embeddings.json"

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        old_records = json.load(f)
else:
    old_records = []
old_map = {}
for rec in old_records:
    h = text_hash(rec["combined_text"])
    old_map[h] = rec["embedding"]


texts_to_embed = []
embed_indexes = []
final_embeddings = [None] * len(faqs)


for idx, txt in enumerate(faqs):
    h = text_hash(txt)

    if h in old_map:
        
        final_embeddings[idx] = old_map[h]
    else:
        texts_to_embed.append(txt)
        embed_indexes.append(idx)


if texts_to_embed:
    print(f"\nEmbedding {len(texts_to_embed)} new/updated FAQs...")
    new_embs = model.encode(
        texts_to_embed,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    
    for i, e in zip(embed_indexes, new_embs):
        final_embeddings[i] = e
else:
    print("\nNo new or updated FAQs.")

print("Embedding shape:", len(final_embeddings))


faq_records = []

for idx, vector in enumerate(final_embeddings):
    faq_records.append({
        "faq_id": idx,
        "question": df.iloc[idx][question_col],
        "answer": df.iloc[idx][answer_col],
        "combined_text": faqs[idx],
        "embedding": vector if isinstance(vector, list) else vector.tolist()

    })


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(faq_records, f, indent=2, ensure_ascii=False)

print("\n faq_embeddings file Generated Successfully (Idempotent)")
