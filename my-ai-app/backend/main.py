import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import pydantic

# Load environment variables
load_dotenv()

# --- Project Imports (Absolute Imports) ---
from models import Session, Message, Content
from persistence import (
    load_all_sessions, 
    save_session, 
    load_session_history, 
    append_message_to_session,
    update_session_title
)
from gemini_client import stream_chat_response, init_model

# --- Global State ---
class GlobalState:
    sessions: Dict[str, Session] = {}
    gemini_client = None

STATE = GlobalState()

# --- Lifespan Manager (Startup & Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 1. Startup: Initialize Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found in .env. Chat will not work.")
    
    try:
        STATE.gemini_client = init_model()
        print("Gemini Client Initialized Successfully.")
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")

    # 2. Startup: Load Sessions
    STATE.sessions = load_all_sessions()
    
    # Create default session if empty
    if not STATE.sessions:
        default_session = Session(id="default", title="New Chat")
        STATE.sessions[default_session.id] = default_session
        save_session(default_session)
        print("Created default session.")

    print(f"Server started. Loaded {len(STATE.sessions)} sessions.")
    
    yield # Application runs here
    
    # 3. Shutdown
    print("Application shutting down...")

# --- FastAPI App Definition ---
app = FastAPI(
    title="Gemini Full-Stack Chat API",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. In prod, specify your frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ChatRequest(pydantic.BaseModel):
    session_id: str
    message: str
    history: List[Content] = [] # Optional, defaults to empty list

# =========================================================================
# === API Endpoints ===
# =========================================================================

@app.post("/api/sessions", response_model=Session)
def create_new_session():
    """Creates a new, empty chat session."""
    new_session = Session(title="New Chat")
    STATE.sessions[new_session.id] = new_session
    save_session(new_session)
    return new_session

@app.get("/api/sessions", response_model=List[Session])
def get_all_sessions():
    """Returns all sessions sorted by newest first."""
    return sorted(
        STATE.sessions.values(), 
        key=lambda s: s.created_at, 
        reverse=True
    )

@app.get("/api/sessions/{session_id}/messages", response_model=List[Message])
def get_session_messages(session_id: str):
    """Returns message history for a session."""
    if session_id not in STATE.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return load_session_history(session_id)

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    """Endpoint for real-time streaming of Gemini's response."""
    
    # 1. Validation
    if request.session_id not in STATE.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not STATE.gemini_client:
        raise HTTPException(status_code=503, detail="Gemini client not available")

    # 2. Save User Message
    user_msg = Message(
        session_id=request.session_id,
        role="user",
        text=request.message
    )
    append_message_to_session(user_msg)

    # 3. Update Title (If it's a new chat)
    current_session = STATE.sessions[request.session_id]
    if current_session.title == "New Chat":
        # Take first 5 words of user message
        new_title = " ".join(request.message.split()[:5])
        current_session.title = new_title
        update_session_title(request.session_id, new_title)

    # 4. Stream Generator
    async def event_generator():
        full_response_text = ""
        
        try:
            # --- CRITICAL FIX HERE ---
            # We load history from DB instead of trusting the request
            current_history = load_session_history(request.session_id)

            # Assumes stream_chat_response is an async generator
            async for chunk in stream_chat_response(
                STATE.gemini_client,
                request.message,
                current_history # <--- Sending the DB history object
            ):
                if await http_request.is_disconnected():
                    print("Client disconnected.")
                    break
                
                full_response_text += chunk
                yield {"data": chunk}

            # End of stream marker
            yield {"event": "end", "data": "Stream finished"}

        except Exception as e:
            print(f"Streaming Error: {e}")
            yield {"event": "error", "data": str(e)}
        
        finally:
            # 5. Save AI Response (Only if we got text)
            if full_response_text.strip():
                ai_msg = Message(
                    session_id=request.session_id,
                    role="model",
                    text=full_response_text
                )
                append_message_to_session(ai_msg)

    return EventSourceResponse(event_generator())