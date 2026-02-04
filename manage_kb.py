"""
KB Expansion Manager - CLI Tool
Manage knowledge base expansion suggestions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.kb_expander import KnowledgeBaseExpander


def main():
    """Main CLI interface"""
    expander = KnowledgeBaseExpander()
    
    print("\n" + "="*70)
    print("KNOWLEDGE BASE EXPANSION MANAGER")
    print("="*70)
    
    while True:
        print("\n📚 Options:")
        print("  1. View knowledge gaps")
        print("  2. View pending suggestions")
        print("  3. Auto-approve high-confidence suggestions")
        print("  4. Generate report")
        print("  5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            # View gaps
            print("\n🔍 Identifying knowledge gaps...")
            gaps = expander.identify_knowledge_gaps()
            
            if gaps:
                print(f"\nFound {len(gaps)} frequently asked questions not in KB:")
                for i, gap in enumerate(gaps, 1):
                    print(f"  {i}. {gap}")
            else:
                print("\n✓ No significant gaps found!")
        
        elif choice == '2':
            # View suggestions
            pending = expander.get_pending_suggestions()
            
            if pending:
                print(f"\n📝 {len(pending)} pending suggestions:")
                for i, sugg in enumerate(pending):
                    print(f"\n  [{i}] Query: {sugg['query']}")
                    print(f"      Category: {sugg['category']}")
                    print(f"      Confidence: {sugg['confidence']:.2f}")
                    print(f"      Facts: {len(sugg['facts'])} items")
                
                # Option to approve/reject
                action = input("\nApprove/Reject? (a <index> / r <index> / skip): ").strip()
                if action.startswith('a '):
                    idx = int(action.split()[1])
                    if expander.approve_suggestion(idx):
                        print(f"✓ Approved suggestion {idx}")
                elif action.startswith('r '):
                    idx = int(action.split()[1])
                    if expander.reject_suggestion(idx):
                        print(f"✗ Rejected suggestion {idx}")
            else:
                print("\n✓ No pending suggestions!")
        
        elif choice == '3':
            # Auto-approve
            print("\n🤖 Auto-approving high-confidence suggestions...")
            count = expander.auto_expand(min_confidence=0.85)
            print(f"✓ Auto-approved {count} suggestions")
        
        elif choice == '4':
            # Generate report
            print(expander.generate_report())
        
        elif choice == '5':
            print("\nGoodbye! 👋\n")
            break
        
        else:
            print("\n❌ Invalid option")


if __name__ == "__main__":
    main()
