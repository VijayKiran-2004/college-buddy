import uvicorn, threading, os, socket, time, asyncio, html, re
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from rag.chain import rag_answer, enhance_response_for_students
from rag.enhanced_matcher import get_answer_with_link
from scraper.loader import ingest_from_cache
from scraper.doc_loader import ingest_word_document
from typing import Dict, Optional, Tuple, Union
import json
from response_cache import response_cache
from analytics_logger import analytics
from feedback_collector import feedback_collector
from background_analytics import analyze_query_background
from typo_corrector import correct_typos, get_correction_message

CACHE_FILE = 'scraped_data.json'
DB_DIR = './chroma'
CACHE_MAX_AGE_SECONDS = 24 * 60 * 60  # 24 hours

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

def detect_category(question: str) -> str:
    """Detect the category of a question for analytics."""
    question_lower = question.lower()
    
    categories = {
        'placement': ['placement', 'job', 'career', 'recruitment', 'package', 'salary', 'company', 'hire'],
        'admission': ['admission', 'admissions', 'apply', 'eligibility', 'cutoff', 'seat', 'intake'],
        'contact': ['contact', 'phone', 'email', 'address', 'location', 'reach'],
        'hostel': ['hostel', 'accommodation', 'room', 'mess', 'food', 'boarding'],
        'library': ['library', 'book', 'reading', 'journal', 'resource'],
        'fee': ['fee', 'fees', 'cost', 'tuition', 'payment', 'scholarship', 'concession'],
        'faculty': ['faculty', 'teacher', 'professor', 'hod', 'staff', 'instructor'],
        'exam': ['exam', 'examination', 'test', 'result', 'marks', 'grade'],
        'event': ['event', 'fest', 'festival', 'activity', 'cultural', 'technical'],
        'course': ['course', 'program', 'degree', 'branch', 'stream', 'specialization'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in question_lower for keyword in keywords):
            return category
    
    return 'general'

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

@app.get("/analytics")
@limiter.limit("10/minute")
def get_analytics(request: Request):
    """Get analytics dashboard data."""
    summary = analytics.get_summary()
    return JSONResponse(content=summary)

@app.get("/analytics/background")
@limiter.limit("10/minute")
def get_background_analytics(request: Request):
    """Get LLM-powered background analytics (no delay to users)."""
    from background_analytics import get_quick_stats
    try:
        stats = get_quick_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.post("/feedback")
@limiter.limit("30/minute")
async def submit_feedback(request: Request):
    """Submit user feedback for a response."""
    try:
        data = await request.json()
        question = data.get("question", "")
        response = data.get("response", "")
        is_helpful = data.get("is_helpful", True)
        comment = data.get("comment", "")
        
        feedback_collector.add_feedback(question, response, is_helpful, comment)
        
        return JSONResponse(content={"message": "Thank you for your feedback!"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error saving feedback: {str(e)}"}
        )

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a Word document containing college data.
    """
    if not file.filename or not file.filename.endswith('.docx'):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .docx files are supported"}
        )
    
    try:
        # Save the uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        ingest_word_document(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        # Reingest data to update the knowledge base
        ingest_from_cache(CACHE_FILE)
        
        return JSONResponse(
            content={"message": "Document successfully processed and added to the knowledge base"}
        )
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing document: {str(e)}"}
        )

@app.websocket("/chat")
@limiter.limit("30/minute")
async def websocket_endpoint(ws: WebSocket, request: Request):
    await ws.accept()
    print("Client connected to websocket")
    history = []
    greetings = ["hi", "hello", "hey", "hii", "heyy", "how are you", "how r u", "how are you doing"]
    try:
        while True:
            data = await ws.receive_json()
            question = data.get("message", "")
            
            # Sanitize input
            question = sanitize_input(question)
            
            if not question:
                await ws.send_json({
                    "type": "error",
                    "message": "I didn't receive a question. Please try again."
                })
                continue
            
            # Correct typos in the question
            corrected_question, was_corrected = correct_typos(question)
            correction_msg = get_correction_message(question, corrected_question) if was_corrected else ""
            
            # Use corrected question for processing
            question = corrected_question
            
            # Normalize question for greeting check
            normalized_question = question.lower().strip(" ?!.")
            
            if normalized_question in greetings:
                greeting_response = "Hello! I'm College-Buddy, here to help you with information about the college. You can ask me about admissions, courses, fees, and more."
                # Enhance greeting for student-friendly tone
                greeting_response = enhance_response_for_students(greeting_response, question)
                await ws.send_json({
                    "type": "response",
                    "message": greeting_response,
                    "sources": []
                })
                continue

            try:
                start_time = time.time()
                lang = 'english'
                
                # Check cache first
                cached_response = response_cache.get(question)
                if cached_response:
                    print(f"[CACHE HIT] Returning cached response for: {question[:50]}...")
                    category = detect_category(question)
                    response_time = time.time() - start_time
                    analytics.log_query(question, category, response_time, success=True)
                    
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
                    answer = "Oops! Something went wrong on my end. Could you please repeat your question?"
                    sources = []
                    success = False
                except Exception as e:
                    print(f"Error generating answer: {e}")
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
                    # Enhance even error messages for friendly tone
                    answer = enhance_response_for_students(answer, question)
                
                # Log analytics
                response_time = time.time() - start_time
                category = detect_category(question)
                analytics.log_query(question, category, response_time, success)
                
                # Cache the response
                response_cache.set(question, {"answer": answer, "sources": sources})
                
                # Append the interaction to history
                history.append({"role": "user", "parts": [question]})
                history.append({"role": "model", "parts": [answer]})
                
                # Add correction message to answer if typo was corrected
                if correction_msg:
                    answer = f"{correction_msg}\n\n{answer}"
                
                # Send response to client IMMEDIATELY
                await ws.send_json({
                    "type": "response",
                    "message": answer,
                    "sources": sources
                })
                
                # BACKGROUND TASK: Analyze with LLM (user doesn't wait!)
                try:
                    asyncio.create_task(
                        asyncio.to_thread(analyze_query_background, question, answer)
                    )
                except Exception as bg_error:
                    # Background task failed - user already has answer, so no problem
                    print(f"[Background] Analytics failed: {bg_error}")
                
            except Exception as e:
                import traceback
                print(f"[ERROR] An error occurred while processing the question: {str(e)}")
                traceback.print_exc()
                
                # Log failed query
                category = detect_category(question)
                analytics.log_query(question, category, 0, success=False)
                
                await ws.send_json({
                    "type": "error",
                    "message": "Oops! Something went wrong on my end. Could you please repeat your question?",
                    "sources": []
                })
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred in the websocket: {e}")

def find_free_port(start_port=8000):
    """Find the next free port, starting from start_port."""
    port = start_port
    max_port = start_port + 100  # Try up to 100 ports
    
    while port < max_port:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise OSError("No free ports found")

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8001))
        print(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Failed to start server: {e}")