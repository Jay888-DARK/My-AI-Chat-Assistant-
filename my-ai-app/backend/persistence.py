import json
import os
from typing import List, Dict
from models import Session, Message

# --- Configuration ---
SESSIONS_FILE = "sessions.json"
HISTORY_DIR = "history"  # Folder to store chat logs

# Ensure history directory exists automatically
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def load_all_sessions() -> Dict[str, Session]:
    """Loads all session metadata from sessions.json"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r") as f:
            data = json.load(f)
            # Convert raw dicts back to Session objects
            sessions = {}
            for k, v in data.items():
                sessions[k] = Session(**v)
            return sessions
    except Exception as e:
        print(f"[ERROR] Failed to load sessions: {e}")
        return {}

def save_session(session: Session):
    """Saves a single session to the sessions.json index"""
    # 1. Load existing data so we don't overwrite others
    all_sessions = load_all_sessions()
    
    # 2. Update/Add the specific session
    all_sessions[session.id] = session
    
    # 3. Save back to disk
    data_to_save = {k: v.dict() for k, v in all_sessions.items()}
    
    with open(SESSIONS_FILE, "w") as f:
        json.dump(data_to_save, f, default=str, indent=2)

def load_session_history(session_id: str) -> List[Message]:
    """
    Loads messages for a specific session. 
    Returns an empty list [] if the file doesn't exist yet (FIX FOR 404 ERROR).
    """
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    
    # --- CRITICAL FIX ---
    if not os.path.exists(file_path):
        return []  # Return empty list instead of crashing!
    # --------------------

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return [Message(**m) for m in data]
    except Exception as e:
        print(f"[ERROR] Failed to load history for {session_id}: {e}")
        return []

def append_message_to_session(message: Message):
    """Adds a message to the session's history file"""
    # 1. Load current history
    history = load_session_history(message.session_id)
    
    # 2. Append new message
    history.append(message)
    
    # 3. Save back to specific history file
    file_path = os.path.join(HISTORY_DIR, f"{message.session_id}.json")
    with open(file_path, "w") as f:
        json.dump([m.dict() for m in history], f, default=str, indent=2)

def update_session_title(session_id: str, new_title: str):
    """Updates just the title of a session"""
    all_sessions = load_all_sessions()
    if session_id in all_sessions:
        session = all_sessions[session_id]
        session.title = new_title
        save_session(session)