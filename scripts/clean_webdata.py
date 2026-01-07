import json
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../"))
DATA_FILE = os.path.join(PROJECT_ROOT, "data/scraped_data/webdata.json")
CLEAN_FILE = os.path.join(PROJECT_ROOT, "data/scraped_data/webdata_cleaned.json")


def hash_page(page):
    content = json.dumps(page, sort_keys=True).encode('utf-8')
    return hashlib.md5(content).hexdigest()


with open(DATA_FILE, "r", encoding="utf-8") as f:
    new_raw = json.load(f)


if os.path.exists(CLEAN_FILE):
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        old_clean = json.load(f)
else:
    old_clean = {}

old_hashes = {url: hash_page(old_clean[url]) for url in old_clean}

cleaned_output = {}


for url, page in new_raw.items():

    
    new_sections = {}

    for section, content in page["sections"].items():
        
        
        texts = list(dict.fromkeys(content.get("texts", [])))
        images = list(dict.fromkeys(content.get("images", [])))

        
        tables = content.get("tables", [])
        seen = set()
        unique_tables = []

        for tbl in tables:
            tbl_tuple = tuple(tuple(row) for row in tbl)
            if tbl_tuple not in seen:
                seen.add(tbl_tuple)
                unique_tables.append(tbl)

        new_sections[section] = {
            "texts": texts,
            "tables": unique_tables,
            "images": images
        }

    cleaned_page = {
        "url": page["url"],
        "title": page["title"],
        "sections": new_sections
    }

    
    new_hash = hash_page(cleaned_page)

    if url in old_hashes and old_hashes[url] == new_hash:
        
        cleaned_output[url] = old_clean[url]
        print(f"UNCHANGED → Using previous cleaned: {url}")
    else:
        
        cleaned_output[url] = cleaned_page
        print(f"UPDATED → Cleaned new/changed page: {url}")


with open(CLEAN_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned_output, f, indent=2, ensure_ascii=False)

print("\nCLEANING COMPLETE")
print(f"Saved cleaned data to: {CLEAN_FILE}")
print(f"Total pages processed: {len(cleaned_output)}")
