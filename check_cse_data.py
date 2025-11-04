import json

# Load scraped data
with open('data/scraped/scraped_data.json', encoding='utf-8') as f:
    data = json.load(f)

# Find CSE-related pages
cse_pages = [p for p in data if 'computer' in p['content'].lower() or 'cse' in p['content'].lower() or 'departments' in p['url'].lower()]

print(f"Found {len(cse_pages)} pages with CSE/department content\n")

for i, page in enumerate(cse_pages[:5]):
    print(f"\n{'='*80}")
    print(f"Page {i+1}: {page['url']}")
    print(f"Content length: {len(page['content'])} chars")
    print(f"Preview:\n{page['content'][:400]}...")
    print('='*80)

# Check if specific department page exists
dept_pages = [p for p in data if 'department' in p['url'].lower()]
print(f"\n\nTotal department pages: {len(dept_pages)}")
for dp in dept_pages:
    print(f"  - {dp['url']}")
