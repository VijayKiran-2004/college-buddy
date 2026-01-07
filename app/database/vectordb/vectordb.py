import json
import chromadb
import os

with open("data/embeddings/faq_embeddings.json", encoding="utf-8") as f:
    faqs = json.load(f)

with open("app/database/vectordb/unified_vectors.json", encoding="utf-8") as f:
    webdocs = json.load(f)

# Initialize ChromaDB with new API
client = chromadb.PersistentClient(path="app/database/vectordb")

# Delete old collections if they exist to avoid dimension mismatch
try:
    client.delete_collection(name="faqs_collection")
    print("Deleted old faqs_collection")
except:
    pass

try:
    client.delete_collection(name="webdocs_collection")
    print("Deleted old webdocs_collection")
except:
    pass

# Create fresh collections
faqs_collection = client.get_or_create_collection(name="faqs_collection")
webdocs_collection = client.get_or_create_collection(name="webdocs_collection")

faqs_collection.upsert(    
    ids=[f"faq_{f['faq_id']:05d}" for f in faqs],
    documents=[f["combined_text"] for f in faqs],
    embeddings=[f["embedding"] for f in faqs],
    metadatas=[
        {
            "type": "faq",
            "faq_id": f["faq_id"],
            "question": f["question"],
            "answer": f["answer"]
        }
        for f in faqs
    ]
)

print("✓ FAQs stored:", faqs_collection.count())

webdocs_collection.upsert(
    ids=[r["chunk_id"] for r in webdocs],
    documents=[r["text"] for r in webdocs],
    embeddings=[r["embedding"] for r in webdocs],
    metadatas=[r["metadata"] for r in webdocs]
)

print("✓ Web docs stored:", webdocs_collection.count())

print("\n" + "=" * 60)
print("CHROMADB INITIALIZATION COMPLETE")
print("=" * 60)
print(f"Total FAQs: {faqs_collection.count()}")
print(f"Total Web docs: {webdocs_collection.count()}")
print("=" * 60)
