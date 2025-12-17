import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def init_model():
    """Initializes the Gemini model using the API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is missing from .env")
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-flash-latest')

async def stream_chat_response(model, new_message_text, chat_history_objects):
    """
    Streams the response from Gemini.
    Handles both 'Message' objects (database) and raw dicts.
    """
    
    formatted_history = []
    
    for msg in chat_history_objects:
        role = "user"
        content = ""

        # --- SMART DETECTION LOGIC ---
        
        # 1. Is it our Database Message object? (Has .text attribute)
        if hasattr(msg, 'text'):
            role = msg.role
            content = msg.text
            
        # 2. Is it a Dictionary? (Has .get method)
        elif isinstance(msg, dict):
            role = msg.get('role', 'user')
            # Try getting 'parts' first, then 'text'
            content = msg.get('parts', '') or msg.get('text', '')
            
        # 3. Fallback: Check attributes directly just in case
        else:
            role = getattr(msg, 'role', 'user')
            content = getattr(msg, 'parts', None) or getattr(msg, 'text', "")

        # --- FORMATTING FOR GEMINI ---
        
        # Map 'model' -> 'model', everything else -> 'user'
        gemini_role = "model" if role == "model" else "user"
        
        # Ensure content is a string
        if isinstance(content, list):
            content = " ".join([str(c) for c in content])
            
        if content:
            formatted_history.append({
                "role": gemini_role,
                "parts": [str(content)]
            })

    # Start the chat session
    chat_session = model.start_chat(history=formatted_history)

    # Send message
    response_stream = chat_session.send_message(new_message_text, stream=True)

    for chunk in response_stream:
        if chunk.text:
            yield chunk.text