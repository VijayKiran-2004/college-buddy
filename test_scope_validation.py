#!/usr/bin/env python3
"""
Test script to verify chatbot scope validation
Tests that off-topic queries are properly rejected
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ultra_rag import UltraRAGSystem

def test_chatbot_scope():
    """Test chatbot with various queries to verify scope validation"""
    
    print("\n" + "=" * 70)
    print("CHATBOT SCOPE VALIDATION TEST")
    print("=" * 70 + "\n")
    
    # Initialize RAG system
    print("Initializing UltraRAG System...\n")
    rag = UltraRAGSystem()
    
    # Test queries - mix of valid and invalid
    test_cases = [
        # Valid college queries
        ("how r u?", "GREETING", True),
        ("where is college located?", "COLLEGE INFO", True),
        ("who is the principal?", "PERSONNEL", True),
        ("what are the college timings?", "TIMINGS", True),
        
        # Invalid queries (should be rejected)
        ("(a+b)^2", "MATH FORMULA", False),
        ("(a+b)^2=?", "MATH EQUATION", False),
        ("what is the formula for photosynthesis?", "SCIENCE", False),
        ("solve 2+2", "MATH", False),
        ("what is the capital of France?", "GENERAL KNOWLEDGE", False),
    ]
    
    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70 + "\n")
    
    passed = 0
    failed = 0
    
    for query, category, should_answer in test_cases:
        print(f"Query: {query}")
        print(f"Category: {category}")
        print(f"Expected: {'ANSWER' if should_answer else 'REJECT'}")
        
        response = rag(query)
        
        # Check if response is a rejection
        is_rejection = "I'm sorry, I can only answer questions about TKRCET college" in response
        
        # Determine if test passed
        if should_answer:
            # Should answer - pass if NOT a rejection
            test_passed = not is_rejection
        else:
            # Should reject - pass if IS a rejection
            test_passed = is_rejection
        
        if test_passed:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            failed += 1
        
        print(f"Response: {response[:150]}...")
        print("-" * 70 + "\n")
    
    # Print summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    test_chatbot_scope()
