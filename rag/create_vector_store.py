import json
import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

def create_vector_store_from_scraped_data(json_path: str, collection_name: str, persist_directory: str, additional_context_path: Optional[str] = None):
    """Creates a Chroma vector store from scraped data and optional additional context."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {json_path} was not found.")
        return

    if not scraped_data:
        print("No data found in scraped_data.json. Nothing to do.")
        return

    print(f"Found {len(scraped_data)} documents to add to the vector store.")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create Document objects from scraped data
    documents = []
    for item in scraped_data:
        doc = Document(
            page_content=item.get("content", ""),
            metadata={"source": item.get("url", ""), "title": item.get("page_name", "")}
        )
        documents.append(doc)
    
    # Add additional context file if provided
    if additional_context_path and os.path.exists(additional_context_path):
        print(f"Adding additional context from {additional_context_path}")
        with open(additional_context_path, 'r', encoding='utf-8') as f:
            additional_content = f.read()
            doc = Document(
                page_content=additional_content,
                metadata={
                    "source": "additional_context", 
                    "title": "TKRCET Additional Information"
                }
            )
            documents.append(doc)
            print("Additional context added successfully")

    # Create and persist the Chroma vector store
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    print(f"Vector store created with {len(documents)} total documents and persisted to {persist_directory}")

if __name__ == "__main__":
    create_vector_store_from_scraped_data(
        json_path='scraped_data.json',
        collection_name='college_buddy',
        persist_directory='./chroma',
        additional_context_path='additional_context.txt'
    )