"""
Database Cleanup and FAQ Enhancement Script
Fixes chatbot accuracy issues by:
1. Removing navigation menu duplicates
2. Resolving data conflicts (PhD year)
3. Adding explicit FAQ entries for all key personnel
4. Generating cleanup statistics
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class DatabaseCleanup:
    def __init__(self, db_path='app/database/vectordb/unified_vectors.json'):
        self.db_path = db_path
        self.backup_path = db_path + '.backup'
        self.chunks = []
        self.stats = {
            'original_count': 0,
            'removed_nav_menus': 0,
            'removed_duplicates': 0,
            'conflicts_resolved': 0,
            'faqs_added': 0,
            'final_count': 0
        }
    
    def load_data(self):
        """Load the database"""
        print("Loading database...")
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        self.stats['original_count'] = len(self.chunks)
        print(f"✓ Loaded {len(self.chunks)} chunks")
    
    def create_backup(self):
        """Create backup before modifications"""
        print(f"\nCreating backup: {self.backup_path}")
        with open(self.backup_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        print("✓ Backup created")
    
    def remove_navigation_menus(self):
        """Remove navigation menu duplicates"""
        print("\nRemoving navigation menu duplicates...")
        
        nav_patterns = [
            "About Vision& Mission About the Campus Chairman's Message",
            "About Vision&amp; Mission About the Campus Chairman",
            "Departments Civil Engineering Mechanical Engineering Electrical"
        ]
        
        cleaned_chunks = []
        for chunk in self.chunks:
            text = chunk.get('text', '')
            
            # Check if this is a navigation menu
            is_nav_menu = any(pattern in text for pattern in nav_patterns)
            
            # Also check if it's ONLY a navigation menu (short and repetitive)
            if is_nav_menu and len(text) < 300:
                self.stats['removed_nav_menus'] += 1
                continue
            
            cleaned_chunks.append(chunk)
        
        removed = len(self.chunks) - len(cleaned_chunks)
        self.chunks = cleaned_chunks
        print(f"✓ Removed {removed} navigation menu chunks")
    
    def resolve_conflicts(self):
        """Resolve data conflicts - use website data (2015 for PhD year)"""
        print("\nResolving data conflicts...")
        
        conflicts_fixed = 0
        for chunk in self.chunks:
            text = chunk.get('text', '')
            
            # Fix PhD year conflict - use 2015 (from website)
            if 'Dr. A. Suresh Rao' in text and 'in the year 2014' in text:
                chunk['text'] = text.replace('in the year 2014', 'in the year 2015')
                conflicts_fixed += 1
        
        self.stats['conflicts_resolved'] = conflicts_fixed
        print(f"✓ Resolved {conflicts_fixed} data conflicts")
    
    def add_faq_entries(self):
        """Add explicit FAQ entries for key personnel"""
        print("\nAdding FAQ entries...")
        
        faq_entries = [
            {
                "text": "Who is the Principal of TKRCET? | ANSWER: Dr. D. V. Ravi Shankar",
                "metadata": {"type": "faq", "category": "administration", "priority": "high"}
            },
            {
                "text": "Who is the Vice Principal of TKRCET? | ANSWER: Dr. A. Suresh Rao (also HoD of CSE & Dean Academics)",
                "metadata": {"type": "faq", "category": "administration", "priority": "high"}
            },
            {
                "text": "Who is the HOD of CSE? | ANSWER: Dr. A. Suresh Rao",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of CSE-AIML? | ANSWER: Dr. B. Sunil Srinivas",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of CSM? | ANSWER: Dr. B. Sunil Srinivas",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of CSE-DS? | ANSWER: Dr. V. Krishna",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of CSD? | ANSWER: Dr. V. Krishna",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of ECE? | ANSWER: Dr. D. Nageshwar Rao",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of EEE? | ANSWER: Dr. K. Raju",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of IT? | ANSWER: Dr. R. Muruanantham",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of Mechanical? | ANSWER: Mr. D. Rushi Kumar",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of Civil? | ANSWER: Mr. K.V.R Satya Sai",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the HOD of MBA? | ANSWER: Dr. K. Gyaneswari",
                "metadata": {"type": "faq", "category": "departments", "priority": "high"}
            },
            {
                "text": "Who is the founder of TKRCET? | ANSWER: Sri. Teegala Krishna Reddy (Chairman of TKR Educational Society)",
                "metadata": {"type": "faq", "category": "administration", "priority": "high"}
            },
            {
                "text": "Who is the Secretary of TKRCET? | ANSWER: Dr. T. Harinath Reddy",
                "metadata": {"type": "faq", "category": "administration", "priority": "high"}
            }
        ]
        
        # Add FAQ entries to the beginning for higher priority
        self.chunks = faq_entries + self.chunks
        self.stats['faqs_added'] = len(faq_entries)
        print(f"✓ Added {len(faq_entries)} FAQ entries")
    
    def save_cleaned_data(self):
        """Save the cleaned database"""
        print("\nSaving cleaned database...")
        self.stats['final_count'] = len(self.chunks)
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(self.chunks)} chunks")
    
    def print_statistics(self):
        """Print cleanup statistics"""
        print("\n" + "="*70)
        print("CLEANUP STATISTICS")
        print("="*70)
        print(f"Original chunk count:        {self.stats['original_count']}")
        print(f"Navigation menus removed:    {self.stats['removed_nav_menus']}")
        print(f"Data conflicts resolved:     {self.stats['conflicts_resolved']}")
        print(f"FAQ entries added:           {self.stats['faqs_added']}")
        print(f"Final chunk count:           {self.stats['final_count']}")
        print(f"Net change:                  {self.stats['final_count'] - self.stats['original_count']:+d}")
        print(f"Size reduction:              {((self.stats['original_count'] - self.stats['final_count']) / self.stats['original_count'] * 100):.2f}%")
        print("="*70)
    
    def delete_cache_files(self):
        """Delete FAISS and BM25 cache to force rebuild"""
        print("\nDeleting cache files to force rebuild...")
        
        cache_files = [
            'app/database/vectordb/faiss_index.bin',
            'app/database/vectordb/bm25_index.pkl'
        ]
        
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"✓ Deleted {cache_file}")
            else:
                print(f"⚠ {cache_file} not found (already deleted or doesn't exist)")
    
    def run(self):
        """Run the complete cleanup process"""
        print("\n" + "="*70)
        print("DATABASE CLEANUP AND FAQ ENHANCEMENT")
        print("="*70)
        
        self.load_data()
        self.create_backup()
        self.remove_navigation_menus()
        self.resolve_conflicts()
        self.add_faq_entries()
        self.save_cleaned_data()
        self.delete_cache_files()
        self.print_statistics()
        
        print("\n✅ Cleanup completed successfully!")
        print(f"📁 Backup saved to: {self.backup_path}")
        print("🔄 Cache files deleted - indices will rebuild on next run")


if __name__ == '__main__':
    cleanup = DatabaseCleanup()
    cleanup.run()
