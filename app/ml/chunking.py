import json
import os
import hashlib

INPUT_FILE = "data/scraped_data/webdata_cleaned.json"
OUTPUT_FILE = "data/chunks/chunks.json"

CHUNK_SIZE = 500
OVERLAP = 100

class RecursiveCharacterTextSplitter:
    def __init__(self, separators=None, chunk_size=500, overlap=100):
        self.separators = separators or ["\n\n", "\n", " ", ""]
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text):
        final_chunks = []
        # Start with the whole text as a single chunk
        chunks = [text]
        
        # Iterate through separators and split chunks that are too large
        for separator in self.separators:
            new_chunks = []
            for chunk in chunks:
                if len(chunk) > self.chunk_size:
                    # Split the chunk by the current separator
                    splits = chunk.split(separator)
                    
                    # Merge small splits together
                    merged_splits = []
                    current_split = ""
                    for s in splits:
                        if len(current_split) + len(s) + len(separator) > self.chunk_size:
                            if current_split:
                                merged_splits.append(current_split)
                            current_split = s
                        else:
                            if current_split:
                                current_split += separator + s
                            else:
                                current_split = s
                    if current_split:
                        merged_splits.append(current_split)
                    
                    new_chunks.extend(merged_splits)
                else:
                    new_chunks.append(chunk)
            chunks = new_chunks

        # Handle overlaps
        final_chunks_with_overlap = []
        for i in range(len(chunks)):
            chunk = chunks[i]
            if i > 0 and self.overlap > 0:
                prev_chunk = chunks[i-1]
                overlap_text = prev_chunk[-self.overlap:]
                if chunk.startswith(overlap_text):
                    final_chunks_with_overlap.append(chunk)
                else:
                    final_chunks_with_overlap.append(overlap_text + chunk)
            else:
                final_chunks_with_overlap.append(chunk)
                
        return final_chunks_with_overlap

def chunk_text(text):
    # Added "Principal" and "Secretary" as separators to ensure they are not in the same chunk
    separators = ["\n\n", "\n", ". ", " ", "", "Principal", "Secretary"]
    splitter = RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=CHUNK_SIZE,
        overlap=OVERLAP
    )
    return splitter.split_text(text)

def page_text_hash(page):
    full_text = ""
    for sec, content in page["sections"].items():
        for t in content["texts"]:
            full_text += t
    return hashlib.md5(full_text.encode()).hexdigest()


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    site_data = json.load(f)


if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        old_chunks = json.load(f)
else:
    old_chunks = []


old_lookup = {}
for ch in old_chunks:
    url = ch["source_url"]
    old_lookup.setdefault(url, []).append(ch)


URL_HASH_FILE = "data/chunks/url_hash_map.json"

if os.path.exists(URL_HASH_FILE):
    with open(URL_HASH_FILE, "r", encoding="utf-8") as f:
        old_hashes = json.load(f)
else:
    old_hashes = {}

new_chunks = []

for url, page in site_data.items():

    new_hash = page_text_hash(page)

    if url in old_hashes and old_hashes[url] == new_hash:
        
        print(f"UNCHANGED → {url}")
        new_chunks.extend(old_lookup.get(url, []))
    else:
        
        print(f"UPDATED/NEW → {url}")
        for section, content in page["sections"].items():
            for text in content["texts"]:
                for c in chunk_text(text):
                    new_chunks.append({
                        "text": c,
                        "section": section,
                        "source_url": url
                    })

        
        old_hashes[url] = new_hash


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(new_chunks, f, indent=2, ensure_ascii=False)


with open(URL_HASH_FILE, "w", encoding="utf-8") as f:
    json.dump(old_hashes, f, indent=2, ensure_ascii=False)

print(f"{len(new_chunks)} chunks saved successfully.")
