"""
Auto-fix import statements after reorganization
Updates all Python files to use new module paths
"""
import os
import re
from pathlib import Path

# Import mapping (old → new)
IMPORT_MAPPING = {
    'from core.cache import': 'from core.cache import',
    'import core.cache as response_cache': 'import core.cache as response_cache',
    'from core.analytics import': 'from core.analytics import',
    'import core.analytics as analytics_logger': 'import core.analytics as analytics_logger',
    'from core.feedback import': 'from core.feedback import',
    'import core.feedback as feedback_collector': 'import core.feedback as feedback_collector',
    'from core.typo_corrector import': 'from core.typo_corrector import',
    'import core.typo_corrector': 'import core.typo_corrector',
    'from core.background_analytics import': 'from core.background_analytics import',
    'import core.background_analytics': 'import core.background_analytics',
}

# File path updates
PATH_MAPPING = {
    "'data/cache/response_cache.json'": "'data/cache/response_cache.json'",
    '"data/cache/response_cache.json"': '"data/cache/response_cache.json"',
    "'data/analytics/analytics_data.json'": "'data/analytics/analytics_data.json'",
    '"data/analytics/analytics_data.json"': '"data/analytics/analytics_data.json"',
    "'data/analytics/background_analytics.json'": "'data/analytics/background_analytics.json'",
    '"data/analytics/background_analytics.json"': '"data/analytics/background_analytics.json"',
    "'data/scraped/scraped_data.json'": "'data/scraped/scraped_data.json'",
    '"data/scraped/scraped_data.json"': '"data/scraped/scraped_data.json"',
    "'data/links/structured_links.csv'": "'data/links/structured_links.csv'",
    '"data/links/structured_links.csv"': '"data/links/structured_links.csv"',
    "'data/student/": "'data/student/",
    '"data/student/': '"data/student/',
}

def update_file(file_path):
    """Update imports and paths in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Update imports
        for old_import, new_import in IMPORT_MAPPING.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes.append(f"  ✓ {old_import} → {new_import}")
        
        # Update file paths
        for old_path, new_path in PATH_MAPPING.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                changes.append(f"  ✓ {old_path} → {new_path}")
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📝 Updated: {file_path}")
            for change in changes:
                print(change)
            return True
        return False
    
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all Python files in the project"""
    print("🔄 Updating import statements and file paths...\n")
    
    # Directories to scan
    scan_dirs = ['.', 'rag', 'scraper', 'core', 'scripts', 'tests']
    
    updated_count = 0
    total_files = 0
    
    for directory in scan_dirs:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            # Skip venv and __pycache__
            dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git', 'chroma']]
            
            for file in files:
                if file.endswith('.py'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    if update_file(file_path):
                        updated_count += 1
    
    print(f"\n✅ Done! Updated {updated_count}/{total_files} files")
    
    if updated_count > 0:
        print("\n⚠️  IMPORTANT:")
        print("1. Test your application: python main.py")
        print("2. Run tests: pytest tests/")
        print("3. Check for any remaining import errors")
    else:
        print("\nNo changes needed - all imports are already correct!")

if __name__ == '__main__':
    main()
