#  Chunking Script — README

##  Overview
`chunking.py` is a Python script that processes scraped website data and breaks long text into smaller overlapping chunks. These chunks are essential for Retrieval-Augmented Generation (RAG), embedding generation, vector database indexing, and other NLP workflows.

The script reads structured data from `data/scraped_data/webdata.json`, applies chunking logic (500 characters with 100 characters of overlap), and outputs the results into `data/chunks/chunks.json`.

---

##  Features
- Splits large text into smaller, manageable chunks  
- Adds overlap between chunks for improved context retention  
- Stores metadata (section name and source URL)  
- Outputs clean, ready-to-use JSON  
- Uses only Python standard libraries (no external installations required)

---

## Chunk example

{
  "text": "chunk of text here...",
  "section": "About Us",
  "source_url": "https://example.com"
}

## How It Works

- Loads input JSON from webdata.json

- Iterates through all pages

- Iterates through all sections inside each page

- Reads text content from the "texts" list

- Splits text into chunks using:

    CHUNK_SIZE = 500

    OVERLAP = 100

- Attaches metadata (section, source_url)

- Saves all generated chunks to chunks.json

## Chunking Logic

The script uses a sliding window mechanism:

**Chunk size:** 500 characters  

**Overlap:** 100 characters  

### Example flow for a long text:

Chunk 1 → characters 0–500

Chunk 2 → characters 400–900

Chunk 3 → characters 800–1300

This overlap ensures context continuity so your RAG model returns accurate answers

## How to Run
1. Ensure webdata.json is present

Place it in the same folder as chunking.py.

2. Run the script

    python chunking.py

3. Output

    XXXX chunks saved to chunks.json

Generated file location : data/chunks/chunks.json

## Requirements

- This script uses only Python’s built-in standard libraries.

## Notes

- Ensure the directory data/chunks/ exists before running the script

- Ensure webdata.json file exists in path data/scraped_data.