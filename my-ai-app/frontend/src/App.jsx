// src/App.jsx
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Send, Plus, MessageSquare, Bot, User } from 'lucide-react';
import './App.css';

// --- CONFIGURATION ---
// Option 1: Local Development (Default)
const API_BASE = "https://my-ai-chat-assistant.onrender.com";

// Option 2: Public Access (Uncomment this line below when using ngrok for your friend)
// const API_BASE = "https://your-ngrok-url-here.ngrok-free.app/api"; 

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // 1. Load Sessions on Startup
  useEffect(() => {
    fetchSessions();
  }, []);

  // 2. Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 3. Auto-load messages if currentSessionId changes (e.g. after creating new)
  useEffect(() => {
    if (currentSessionId) {
      loadMessages(currentSessionId);
    }
  }, [currentSessionId]);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API_BASE}/sessions`);
      setSessions(res.data);
      // Automatically select the first session if none selected
      if (res.data.length > 0 && !currentSessionId) {
        setCurrentSessionId(res.data[0].id);
      }
    } catch (error) {
      console.error("Failed to load sessions", error);
    }
  };

  const createNewSession = async () => {
    try {
      const res = await axios.post(`${API_BASE}/sessions`);
      setSessions([res.data, ...sessions]);
      setCurrentSessionId(res.data.id);
      setMessages([]); // Clear screen for new chat
    } catch (error) {
      console.error("Error creating session", error);
    }
  };

  const loadMessages = async (id) => {
    try {
      const res = await axios.get(`${API_BASE}/sessions/${id}/messages`);
      setMessages(res.data);
    } catch (error) {
      console.error("Error loading messages", error);
    }
  };

  // Helper to handle sidebar clicks specifically
  const handleSessionClick = (id) => {
    setCurrentSessionId(id);
    // The useEffect hook above will trigger loadMessages automatically
  };

  // --- THE STREAMING LOGIC ---
  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Safety Check: If no session selected, force select one or create one
    if (!currentSessionId) {
        alert("Please select a chat or create a new one!");
        return;
    }

    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Create a placeholder for the AI response
    setMessages(prev => [...prev, { role: 'model', text: '...' }]);

    try {
      // Use native fetch for streaming
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: userMessage.text,
          history: [] 
        })
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponseText = "";

      // Remove the "..." placeholder before we start filling real text
      setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1].text = ""; 
          return newMsgs;
      });

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); 
            if (data === 'Stream finished') break;
            
            aiResponseText += data;
            
            // Update the UI with the chunk
            setMessages(prev => {
              const newMsgs = [...prev];
              newMsgs[newMsgs.length - 1].text = aiResponseText;
              return newMsgs;
            });
          }
        }
      }
      
      // Refresh session list (to update title if it changed)
      fetchSessions();

    } catch (error) {
      console.error("Streaming error", error);
      setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1].text = "Error: Could not connect to Gemini.";
          return newMsgs;
      });
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <button className="new-chat-btn" onClick={createNewSession}>
          <Plus size={20} /> New Chat
        </button>
        <div className="session-list">
          {sessions.map(session => (
            <div 
              key={session.id} 
              className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
              onClick={() => handleSessionClick(session.id)} // Click loads the chat!
            >
              <span className="icon"><MessageSquare size={16} /></span>
              <span className="title">{session.title || "Untitled Chat"}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat */}
      <div className="chat-area">
        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className={`avatar ${msg.role === 'user' ? 'user' : 'ai'}`}>
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="message-content">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-wrapper">
            <input 
              type="text" 
              placeholder="Message Gemini..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={isTyping}
            />
            <button className="send-btn" onClick={handleSend} disabled={isTyping}>
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;