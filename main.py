import uvicorn, os, time, asyncio, html, re
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from rag.chain import rag_answer
from scraper.loader import ingest_from_cache
from typing import Dict
import json
from core.cache import response_cache

CACHE_FILE = 'data/scraped/scraped_data.json'

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# Input sanitization
MAX_MESSAGE_LENGTH = 500

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape special characters
    text = html.escape(text)
    
    # Limit length
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[:MAX_MESSAGE_LENGTH]
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] Starting data ingestion from cache...")
    try:
        ingest_from_cache(CACHE_FILE)
        print("[startup] Data ingestion complete.")
    except Exception as e:
        print(f"[startup] Error during data ingestion: {e}")
    
    yield


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter
app.state.limiter = limiter

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
@limiter.limit("100/minute")
def home(request: Request):
    return FileResponse("static/index.html")

@app.get("/demo")
@limiter.limit("100/minute")
def demo(request: Request):
    return FileResponse("static/demo-page.html")

@app.websocket("/chat")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("Client connected to websocket")
    history = []
    greetings = ["hi", "hello", "hey", "hii", "heyy", "how are you", "how r u", "how are you doing"]
    try:
        while True:
            data = await ws.receive_json()
            
            # Handle heartbeat ping
            if data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
                continue
            
            question = data.get("message", "")
            
            # Sanitize input
            question = sanitize_input(question)
            
            if not question:
                await ws.send_json({
                    "type": "error",
                    "message": "I didn't receive a question. Please try again."
                })
                continue
            
            # Normalize question for greeting check
            normalized_question = question.lower().strip(" ?!.")
            
            if normalized_question in greetings:
                greeting_response = "Hello! I'm College-Buddy, here to help you with information about the college. You can ask me about admissions, courses, fees, and more."
                try:
                    await ws.send_json({
                        "type": "response",
                        "message": greeting_response,
                        "sources": []
                    })
                except Exception as send_error:
                    print(f"[WARNING] Failed to send greeting - client disconnected: {send_error}")
                continue

            try:
                start_time = time.time()
                lang = 'english'
                
                # Check cache first
                cached_response = response_cache.get(question)
                if cached_response:
                    print(f"[CACHE HIT] Returning cached response for: {question[:50]}...")
                    response_time = time.time() - start_time
                    
                    # Handle both dict and string cached responses
                    if isinstance(cached_response, dict):
                        answer = cached_response.get("answer", "")
                        sources = cached_response.get("sources", [])
                    else:
                        answer = cached_response
                        sources = []
                    
                    await ws.send_json({
                        "type": "response",
                        "message": answer,
                        "sources": sources
                    })
                    continue
                
                # Get the answer with a timeout
                try:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(rag_answer, question=question, lang=lang, history=history),
                        timeout=30.0
                    )
                    
                    # Extract answer and sources if result is a dict
                    if isinstance(result, dict):
                        answer = result.get("answer", str(result))
                        sources = result.get("sources", [])
                    else:
                        answer = result
                        sources = []
                    
                    success = True
                except asyncio.TimeoutError:
                    print(f"⏱️ Timeout waiting for answer")
                    answer = "Oops! Something went wrong on my end. Could you please repeat your question?"
                    sources = []
                    success = False
                except Exception as e:
                    print(f"❌ Error generating answer: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    answer = "Oops! Something went wrong on my end. Could you please repeat your question?"
                    sources = []
                    success = False
                
                # Handle answer encoding
                if isinstance(answer, (bytes, bytearray)):
                    answer = answer.decode('utf-8')
                elif not isinstance(answer, str):
                    answer = str(answer)
                
                # Check if answer is a "no answer" case
                if not answer or "I don't have that information" in answer or len(answer) < 20:
                    answer = "I'm not sure about that. Could you try rephrasing your question or contact the college office at https://tkrcet.ac.in/contact-us/"
                
                # Cache the response
                response_cache.set(question, {"answer": answer, "sources": sources})
                
                # Append the interaction to history
                history.append({"role": "user", "parts": [question]})
                history.append({"role": "model", "parts": [answer]})
                
                # Send response to client (check if connection is still open)
                try:
                    await ws.send_json({
                        "type": "response",
                        "message": answer,
                        "sources": sources
                    })
                except Exception as send_error:
                    print(f"[WARNING] Failed to send response - client likely disconnected: {send_error}")
                    # Connection closed, but that's okay - just log and continue
                
            except Exception as e:
                import traceback
                print(f"[ERROR] An error occurred while processing the question: {str(e)}")
                traceback.print_exc()
                
                try:
                    await ws.send_json({
                        "type": "error",
                        "message": "Oops! Something went wrong on my end. Could you please repeat your question?",
                        "sources": []
                    })
                except Exception as send_error:
                    print(f"[WARNING] Failed to send error message - client disconnected: {send_error}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred in the websocket: {e}")

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8001))
        print(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Failed to start server: {e}")