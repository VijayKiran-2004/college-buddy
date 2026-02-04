"""
Corpus Converter - Convert unified_vectors.json to UltraRAG JSONL format
"""
import json
import argparse
from pathlib import Path

def convert_to_ultrarag_format(input_path, output_path):
    """
    Convert unified_vectors.json to UltraRAG corpus format (JSONL)
    
    UltraRAG expects JSONL format where each line is:
    {"id": "doc_id", "contents": "text content", "metadata": {...}}
    """
    print(f"Reading from: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Convert to JSONL format
    converted_count = 0
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, chunk in enumerate(chunks):
            # Create UltraRAG document
            doc = {
                "id": f"doc_{idx}",
                "contents": chunk.get('text', ''),
                "metadata": {
                    "source": chunk.get('source', 'unknown'),
                    "url": chunk.get('url', ''),
                    "original_index": idx
                }
            }
            
            # Write as JSONL (one JSON object per line)
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            converted_count += 1
    
    print(f"✓ Converted {converted_count} documents to {output_path}")
    return converted_count

def verify_conversion(jsonl_path):
    """Verify the converted JSONL file"""
    print(f"\nVerifying: {jsonl_path}")
    
    count = 0
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                doc = json.loads(line)
                assert 'id' in doc, f"Missing 'id' in line {line_num}"
                assert 'contents' in doc, f"Missing 'contents' in line {line_num}"
                count += 1
            except Exception as e:
                print(f"✗ Error on line {line_num}: {e}")
                return False
    
    print(f"✓ Verified {count} documents - all valid!")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert unified_vectors.json to UltraRAG format')
    parser.add_argument('--input', default='app/database/vectordb/unified_vectors.json',
                        help='Input JSON file path')
    parser.add_argument('--output', default='app/database/vectordb/corpus_ultrarag.jsonl',
                        help='Output JSONL file path')
    parser.add_argument('--verify', action='store_true',
                        help='Verify the output file after conversion')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CORPUS CONVERTER - UltraRAG Format")
    print("=" * 70 + "\n")
    
    # Convert
    count = convert_to_ultrarag_format(args.input, args.output)
    
    # Verify if requested
    if args.verify:
        verify_conversion(args.output)
    
    print(f"\n✓ Conversion complete! Output: {args.output}")
