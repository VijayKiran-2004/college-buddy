"""
Start the College Buddy backend server with proper WebSocket configuration.
This ensures WebSocket connections stay alive during long AI responses.
"""
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    
    print("=" * 80)
    print("🚀 Starting College Buddy Backend Server")
    print("=" * 80)
    print(f"📍 Port: {port}")
    print(f"🌐 Host: 0.0.0.0")
    print(f"💓 WebSocket Ping Interval: 20s")
    print(f"⏱️  WebSocket Ping Timeout: 60s")
    print(f"⏳ Keep-Alive Timeout: 120s")
    print("=" * 80)
    print("\n✅ Server starting... Press CTRL+C to quit\n")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            ws_ping_interval=20,     # Send ping every 20 seconds to keep connection alive
            ws_ping_timeout=60,      # Wait up to 60 seconds for pong response
            timeout_keep_alive=120,  # Keep HTTP connections alive for 2 minutes
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
