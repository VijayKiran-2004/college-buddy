#!/usr/bin/env python3
"""
Complete Data Pipeline for TKRCET Chatbot
Scrapes website -> Chunks -> Embeds -> Vector DB
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def step_1_scrape_website():
    """Step 1: Scrape TKRCET website"""
    print("\n" + "=" * 70)
    print("STEP 1: SCRAPING TKRCET WEBSITE")
    print("=" * 70)
    
    from app.scraper.web import crawl, site_data
    
    print("Starting web scraper...")
    print("Target: https://tkrcet.ac.in/")
    print("Max pages: 50")
    print("Max depth: 3")
    
    # This will populate site_data and save to webdata.json
    print("\nNote: Run 'python app/scraper/web.py' separately to scrape")
    print("Status: Scraper configured and ready")

def step_2_clean_data():
    """Step 2: Clean scraped data"""
    print("\n" + "=" * 70)
    print("STEP 2: CLEANING SCRAPED DATA")
    print("=" * 70)
    
    input_file = "data/scraped_data/webdata.json"
    output_file = "data/scraped_data/webdata_cleaned.json"
    
    if not os.path.exists(input_file):
        print(f"WARNING: {input_file} not found")
        print("Run the scraper first: python app/scraper/web.py")
        return False
    
    print(f"Reading: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    cleaned_data = {}
    
    for url, page_data in raw_data.items():
        cleaned_sections = {}
        
        for section, content in page_data.get("sections", {}).items():
            texts = content.get("texts", [])
            tables = content.get("tables", [])
            
            # Clean and filter texts
            cleaned_texts = [
                t.strip() for t in texts
                if t.strip() and len(t.strip()) > 20
            ]
            
            # Convert tables to readable text
            table_texts = []
            for table in tables:
                table_text = " | ".join([" ".join(row) for row in table])
                if len(table_text) > 20:
                    table_texts.append(table_text)
            
            all_content = cleaned_texts + table_texts
            if all_content:
                cleaned_sections[section] = all_content
        
        if cleaned_sections:
            cleaned_data[url] = {
                "url": url,
                "title": page_data.get("title", ""),
                "sections": cleaned_sections
            }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned {len(cleaned_data)} pages")
    print(f"Saved to: {output_file}")
    return True

def step_3_create_chunks():
    """Step 3: Create chunks from cleaned data"""
    print("\n" + "=" * 70)
    print("STEP 3: CREATING CHUNKS")
    print("=" * 70)
    
    input_file = "data/scraped_data/webdata_cleaned.json"
    output_file = "data/chunks/chunks.json"
    
    if not os.path.exists(input_file):
        print(f"WARNING: {input_file} not found")
        return False
    
    print(f"Reading: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        cleaned_data = json.load(f)
    
    chunks = []
    chunk_size = 300  # characters
    overlap = 50  # characters
    
    for url, page_data in cleaned_data.items():
        title = page_data.get("title", "")
        
        for section, texts in page_data.get("sections", {}).items():
            for text in texts:
                # Create overlapping chunks
                for i in range(0, len(text), chunk_size - overlap):
                    chunk_text = text[i:i + chunk_size]
                    if len(chunk_text.strip()) > 20:
                        chunks.append({
                            "text": chunk_text.strip(),
                            "source": url,
                            "title": title,
                            "section": section
                        })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(chunks)} chunks")
    print(f"Chunk size: {chunk_size} chars with {overlap} char overlap")
    print(f"Saved to: {output_file}")
    return True

def step_4_create_embeddings():
    """Step 4: Create embeddings for chunks"""
    print("\n" + "=" * 70)
    print("STEP 4: CREATING EMBEDDINGS")
    print("=" * 70)
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Installing sentence-transformers...")
        os.system("pip install sentence-transformers")
        from sentence_transformers import SentenceTransformer
    
    input_file = "data/chunks/chunks.json"
    output_file = "data/embeddings/chunks_embeddings.json"
    
    if not os.path.exists(input_file):
        print(f"WARNING: {input_file} not found")
        return False
    
    print(f"Reading: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"Loading embedding model: all-MiniLM-L6-v2")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print(f"Embedding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_tensor=False)
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding.tolist()
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    
    print(f"Created embeddings for {len(chunks)} chunks")
    print(f"Saved to: {output_file}")
    return True

def step_5_create_vector_db():
    """Step 5: Create unified vector database"""
    print("\n" + "=" * 70)
    print("STEP 5: CREATING UNIFIED VECTOR DATABASE")
    print("=" * 70)
    
    input_file = "data/embeddings/chunks_embeddings.json"
    output_file = "app/database/vectordb/unified_vectors.json"
    
    if not os.path.exists(input_file):
        print(f"WARNING: {input_file} not found")
        return False
    
    print(f"Reading: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        chunks_with_embeddings = json.load(f)
    
    # Filter out chunks without embeddings
    valid_chunks = [c for c in chunks_with_embeddings if "embedding" in c]
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(valid_chunks, f, indent=2)
    
    print(f"Created unified vector database with {len(valid_chunks)} documents")
    print(f"Saved to: {output_file}")
    print(f"\nTotal chunks: {len(chunks_with_embeddings)}")
    print(f"Valid chunks: {len(valid_chunks)}")
    
    return True

def main():
    """Run complete pipeline"""
    print("\n" + "=" * 70)
    print("TKRCET CHATBOT - DATA PIPELINE")
    print("=" * 70)
    
    print("\nThis script processes data in 5 steps:")
    print("1. Scrape TKRCET website (https://tkrcet.ac.in/)")
    print("2. Clean and organize scraped data")
    print("3. Create chunks from cleaned data")
    print("4. Create embeddings for chunks")
    print("5. Create unified vector database")
    
    print("\n" + "=" * 70)
    print("STEP 0: CHECKING REQUIREMENTS")
    print("=" * 70)
    
    required_dirs = [
        "data/scraped_data",
        "data/chunks",
        "data/embeddings",
        "app/database/vectordb"
    ]
    
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"\u2713 {dir_path}")
    
    # Check which steps need to be run
    step_1_exists = os.path.exists("data/scraped_data/webdata.json")
    step_2_exists = os.path.exists("data/scraped_data/webdata_cleaned.json")
    step_3_exists = os.path.exists("data/chunks/chunks.json")
    step_4_exists = os.path.exists("data/embeddings/chunks_embeddings.json")
    step_5_exists = os.path.exists("app/database/vectordb/unified_vectors.json")
    
    print("\n" + "=" * 70)
    print("CHECKING EXISTING DATA")
    print("=" * 70)
    print(f"Step 1 (Raw data):       {'\u2713 DONE' if step_1_exists else '\u2717 MISSING'}")
    print(f"Step 2 (Cleaned data):   {'\u2713 DONE' if step_2_exists else '\u2717 MISSING'}")
    print(f"Step 3 (Chunks):         {'\u2713 DONE' if step_3_exists else '\u2717 MISSING'}")
    print(f"Step 4 (Embeddings):     {'\u2713 DONE' if step_4_exists else '\u2717 MISSING'}")
    print(f"Step 5 (Vector DB):      {'\u2713 DONE' if step_5_exists else '\u2717 MISSING'}")
    
    # Run missing steps
    if not step_1_exists:
        print("\n" + "!" * 70)
        print("IMPORTANT: Step 1 requires manual execution")
        print("!" * 70)
        print("Run: python app/scraper/web.py")
        print("This will scrape https://tkrcet.ac.in/ and save to data/scraped_data/webdata.json")
        return
    
    if not step_2_exists:
        if not step_2_clean_data():
            return
    else:
        print("\u2713 Step 2 already completed")
    
    if not step_3_exists:
        if not step_3_create_chunks():
            return
    else:
        print("\u2713 Step 3 already completed")
    
    if not step_4_exists:
        if not step_4_create_embeddings():
            return
    else:
        print("\u2713 Step 4 already completed")
    
    if not step_5_exists:
        if not step_5_create_vector_db():
            return
    else:
        print("\u2713 Step 5 already completed")
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print("\nYou can now run the chatbot:")
    print("python terminal_chat.py")
    print("\nOr start the web interface:")
    print("python app/app.py")

if __name__ == "__main__":
    main()
