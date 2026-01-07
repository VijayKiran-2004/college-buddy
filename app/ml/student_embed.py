import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sentence_transformers import SentenceTransformer


# ----------------------------
# 1. Load Dataset
# ----------------------------
df = pd.read_excel("student_dataset.xlsx")

# ----------------------------
# 2. Define Column Groups
# ----------------------------
text_cols = ["NAME", "EMAIL ID", "DEGREE NAME", "COMPANY PLACED"]
categorical_cols = ["BRANCH", "RESULT", "ADMISSION"]
numeric_cols = ["CREDITS", "CGPA", "JOINING YEAR", "PASSED YEAR"]

# ----------------------------
# 3. Load Text Embedding Model
# ----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text_column(series):
    texts = series.fillna("").astype(str).tolist()
    return np.vstack(model.encode(texts))


# ----------------------------
# 4. Generate TEXT Embeddings
# ----------------------------
text_embeddings_list = []

for col in text_cols:
    print(f"Embedding text column: {col}")
    emb = embed_text_column(df[col])
    text_embeddings_list.append(emb)

# Combine all text embeddings side-by-side
text_embeddings = np.hstack(text_embeddings_list)
print("Text Embedding Shape:", text_embeddings.shape)

# ----------------------------
# 5. Generate CATEGORICAL Embeddings (One-Hot)
# ----------------------------
ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
cat_emb = ohe.fit_transform(df[categorical_cols].fillna("Unknown"))
print("Categorical Embedding Shape:", cat_emb.shape)

# ----------------------------
# 6. Generate NUMERIC Embeddings (Scaled)
# ----------------------------
scaler = MinMaxScaler()
num_emb = scaler.fit_transform(df[numeric_cols].fillna(0))
print("Numeric Embedding Shape:", num_emb.shape)

# ----------------------------
# 7. HYBRID EMBEDDING (Final Output)
# ----------------------------
hybrid_embedding = np.hstack([text_embeddings, cat_emb, num_emb])

print("\n✅ Final Hybrid Embedding Generated!")
print("Hybrid Embedding Shape:", hybrid_embedding.shape)

# Optional: Save embeddings to a file
np.save("student_hybrid_embeddings.npy", hybrid_embedding)
print("\nEmbeddings saved to student_hybrid_embeddings.npy")



import json

# ----------------------------
# 8. SAVE EMBEDDINGS TO JSON
# ----------------------------

embedding_records = []

for idx, vector in enumerate(hybrid_embedding):
    record = {
        "row_id": int(idx),
        "embedding": vector.tolist()
    }
    embedding_records.append(record)

with open("student_hybrid_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(embedding_records, f, indent=2)

print("\n✅ Embeddings saved to student_hybrid_embeddings.json")


