"""
Test response times for College Buddy
Verifies all optimizations are working
"""
import asyncio
import websockets
import json
import time
from datetime import datetime

TEST_QUERIES = [
    "Tell me about CSE department",
    "What companies visit for placements?",
    "What is the admission process?",
    "What are the fees?",
    "Is TKRCET autonomous?",
    "What facilities does the college have?",
    "Tell me about the ECE department",
    "Who is the HOD of CSE?",
]

async def test_query(query, ws):
    """Test a single query and measure response time"""
    start_time = time.time()
    
    # Send query
    await ws.send(json.dumps({"message": query}))
    
    # Receive response
    response = await ws.recv()
    data = json.loads(response)
    
    end_time = time.time()
    response_time = end_time - start_time
    
    return {
        "query": query,
        "response_time": response_time,
        "success": data.get('type') == 'response',
        "answer_length": len(data.get('message', '')),
        "has_info": "I don't have" not in data.get('message', '') and "no information" not in data.get('message', '').lower()
    }

async def run_tests():
    """Run all tests and display results"""
    uri = "ws://localhost:8001/chat"
    
    print("\n" + "="*80)
    print("🧪 COLLEGE BUDDY - RESPONSE TIME TEST")
    print("="*80)
    print(f"Testing {len(TEST_QUERIES)} queries...")
    print(f"Target: <2 seconds per query")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")
    
    results = []
    
    try:
        async with websockets.connect(uri) as ws:
            for i, query in enumerate(TEST_QUERIES, 1):
                print(f"[{i}/{len(TEST_QUERIES)}] Testing: {query[:50]}...")
                
                try:
                    result = await asyncio.wait_for(test_query(query, ws), timeout=10.0)
                    results.append(result)
                    
                    # Display result
                    status = "✅" if result['success'] and result['has_info'] else "❌"
                    time_str = f"{result['response_time']:.2f}s"
                    time_color = "🟢" if result['response_time'] < 2.0 else "🟡" if result['response_time'] < 3.0 else "🔴"
                    
                    print(f"  {status} {time_color} {time_str} | Answer: {result['answer_length']} chars | Info: {'Yes' if result['has_info'] else 'No'}")
                    
                    # Small delay between queries
                    await asyncio.sleep(0.5)
                    
                except asyncio.TimeoutError:
                    print(f"  ❌ ⏱️ TIMEOUT (>10s)")
                    results.append({
                        "query": query,
                        "response_time": 10.0,
                        "success": False,
                        "answer_length": 0,
                        "has_info": False
                    })
                except Exception as e:
                    print(f"  ❌ ERROR: {e}")
                    results.append({
                        "query": query,
                        "response_time": 0,
                        "success": False,
                        "answer_length": 0,
                        "has_info": False
                    })
    
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("Make sure the backend is running on port 8001!")
        return
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'] and r['has_info'])
    avg_time = sum(r['response_time'] for r in results) / total if total > 0 else 0
    fast_queries = sum(1 for r in results if r['response_time'] < 2.0)
    
    print(f"Total Queries: {total}")
    print(f"Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"Fast (<2s): {fast_queries}/{total} ({fast_queries/total*100:.1f}%)")
    print(f"Average Time: {avg_time:.2f}s")
    print(f"Fastest: {min(r['response_time'] for r in results):.2f}s")
    print(f"Slowest: {max(r['response_time'] for r in results):.2f}s")
    
    # Performance verdict
    print("\n" + "="*80)
    if avg_time < 2.0 and successful/total >= 0.8:
        print("🎉 EXCELLENT! All optimizations are working!")
    elif avg_time < 3.0 and successful/total >= 0.7:
        print("✅ GOOD! Performance is acceptable.")
    else:
        print("⚠️ NEEDS IMPROVEMENT! Response times or accuracy are low.")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
