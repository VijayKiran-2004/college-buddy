"""
WebSocket Connection Diagnostic Tool
Tests if WebSocket stays alive during long-running queries
"""
import asyncio
import websockets
import json
import time

async def test_long_query():
    uri = "ws://localhost:8001/chat"
    
    print("="*80)
    print("🔍 WebSocket Connection Diagnostic Tool")
    print("="*80)
    print(f"📍 Connecting to: {uri}")
    print()
    
    try:
        async with websockets.connect(
            uri,
            ping_interval=20,
            ping_timeout=60,
            close_timeout=10
        ) as websocket:
            print("✅ Connected successfully!")
            print()
            
            # Test 1: Simple query
            print("Test 1: Sending greeting...")
            await websocket.send(json.dumps({"message": "hi"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            data = json.loads(response)
            print(f"✅ Response received: {data['message'][:50]}...")
            print()
            
            # Test 2: Long query that triggers Gemini
            print("Test 2: Sending query that requires Gemini (this may take 10-20 seconds)...")
            start_time = time.time()
            
            await websocket.send(json.dumps({"message": "what are you doing?"}))
            print(f"   📤 Query sent at {time.time() - start_time:.2f}s")
            print("   ⏳ Waiting for response...")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=60)
                elapsed = time.time() - start_time
                data = json.loads(response)
                
                print(f"✅ Response received after {elapsed:.2f}s")
                print(f"   Message length: {len(data.get('message', ''))} characters")
                print(f"   Type: {data.get('type')}")
                print()
                print("="*80)
                print("✅ ALL TESTS PASSED - WebSocket connection stayed alive!")
                print("="*80)
                
            except asyncio.TimeoutError:
                print("❌ TIMEOUT - No response received within 60 seconds")
                print("   Connection likely closed during processing")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed unexpectedly!")
        print(f"   Code: {e.code}")
        print(f"   Reason: {e.reason}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print()
    asyncio.run(test_long_query())
