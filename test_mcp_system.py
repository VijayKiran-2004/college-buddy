#!/usr/bin/env python3
"""
Test suite for Pure MCP System
Tests static facts, caching, web scraping, and performance
"""

import sys
import time
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.agent_mcp import SimplifiedMCPAgent


def test_static_facts():
    """Test static fact queries (should be instant)"""
    print("\n" + "=" * 70)
    print("TEST 1: Static Facts (Target: <0.5s)")
    print("=" * 70)
    
    agent = SimplifiedMCPAgent()
    
    tests = [
        ("who is the principal?", "Dr. D. V. Ravi Shankar"),
        ("where is college located?", "Meerpet"),
        ("college timings?", "9:40 AM"),
        ("who is the HOD of CSE?", "Dr. A. Suresh Rao"),
    ]
    
    passed = 0
    for query, expected in tests:
        start = time.time()
        response = agent(query)
        duration = time.time() - start
        
        success = expected.lower() in response.lower() and duration < 0.5
        status = "✓ PASS" if success else "✗ FAIL"
        
        print(f"{status} - {query}")
        print(f"  Time: {duration:.3f}s")
        print(f"  Response: {response[:100]}...")
        
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)


def test_caching():
    """Test that caching works (second query should be faster)"""
    print("\n" + "=" * 70)
    print("TEST 2: Caching (Second query should be <0.1s)")
    print("=" * 70)
    
    agent = SimplifiedMCPAgent()
    query = "who is the principal?"
    
    # First query
    start = time.time()
    response1 = agent(query)
    time1 = time.time() - start
    
    # Second query (should be cached)
    start = time.time()
    response2 = agent(query)
    time2 = time.time() - start
    
    success = time2 < 0.1 and response1 == response2
    status = "✓ PASS" if success else "✗ FAIL"
    
    print(f"{status}")
    print(f"  First query: {time1:.3f}s")
    print(f"  Second query: {time2:.3f}s (cached)")
    if time2 > 0:
        print(f"  Speedup: {time1/time2:.1f}x")
    else:
        print(f"  Speedup: Instant (too fast to measure)")
    
    return success


def test_scope_validation():
    """Test that off-topic queries are rejected"""
    print("\n" + "=" * 70)
    print("TEST 3: Scope Validation (Should reject non-college queries)")
    print("=" * 70)
    
    agent = SimplifiedMCPAgent()
    
    invalid_queries = [
        "(a+b)^2",
        "solve 2+2",
        "what is photosynthesis?",
    ]
    
    passed = 0
    for query in invalid_queries:
        response = agent(query)
        success = "I'm sorry, I can only answer questions about TKRCET college" in response
        status = "✓ PASS" if success else "✗ FAIL"
        
        print(f"{status} - {query}")
        print(f"  Response: {response[:80]}...")
        
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(invalid_queries)}")
    return passed == len(invalid_queries)


def test_greetings():
    """Test greeting detection"""
    print("\n" + "=" * 70)
    print("TEST 4: Greetings")
    print("=" * 70)
    
    agent = SimplifiedMCPAgent()
    
    greetings = ["hi", "hello", "how r u?"]
    
    passed = 0
    for greeting in greetings:
        response = agent(greeting)
        success = "TKRCET College Assistant" in response
        status = "✓ PASS" if success else "✗ FAIL"
        
        print(f"{status} - {greeting}")
        
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(greetings)}")
    return passed == len(greetings)


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PURE MCP SYSTEM - TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Static Facts", test_static_facts()))
    results.append(("Caching", test_caching()))
    results.append(("Scope Validation", test_scope_validation()))
    results.append(("Greetings", test_greetings()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
