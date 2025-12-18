AI Chat Assistant (Gemini 2.0)

A full-stack AI Chatbot built with React and FastAPI, powered by Google's latest Gemini 2.0 Flash model. This application features real-time streaming responses, persistent chat history, and a modern dark-mode UI.

✨ Features

Real-time Streaming: Responses appear word-by-word (Server-Sent Events) just like ChatGPT.

Persistent Sessions: Sidebar history allows you to switch between multiple conversations.

Modern UI: Clean, responsive dark mode interface built with React & CSS Flexbox.

Fast Backend: Asynchronous Python backend using FastAPI.

Secure: Handles CORS and environment variables securely.

🛠️ Tech Stack

Frontend

React.js (Vite)

CSS3 (Custom styling, Flexbox)

Axios & Fetch API (For API communication)

Backend

Python (3.10+)

FastAPI (Web framework)

Uvicorn (ASGI Server)

Google Generative AI (Gemini 2.0 Flash)

Deployment

Frontend: Netlify

Backend: Render

⚙️ Installation & Setup

Follow these steps to run the project locally on your machine.

Clone the Repository git clone https://github.com/[YOUR-USERNAME]/[YOUR-REPO-NAME].git cd [YOUR-REPO-NAME]

Backend Setup Navigate to the backend folder and install Python dependencies.

cd backend Create a virtual environment (optional but recommended) python -m venv venv Activate it: Windows: venv\Scripts\activate Mac/Linux: source venv/bin/activate

Install requirements pip install -r requirements.txt

Configure API Key:

Create a .env file inside the backend folder.

Add your Google Gemini API key: GEMINI_API_KEY=your_actual_api_key_here

Run the Server: uvicorn main:app --reload (The backend will start at http://127.0.0.1:8000)

Frontend Setup Open a new terminal, navigate to the frontend folder, and install dependencies.

cd frontend npm install

Run the Frontend: npm run dev (The app will start at http://localhost:5173)

📂 Project Structure

backend/ main.py (FastAPI server & logic) gemini_client.py (AI Model configuration) sessions.json (Local chat history storage) requirements.txt (Python dependencies) .env (API Secrets - Not uploaded to GitHub) frontend/ src/ App.jsx (Main React component) App.css (Styling) main.jsx (Entry point) package.json (Node dependencies) vite.config.js (Vite configuration) README.md

🤝 Contributing Feel free to fork this repository and submit pull requests. Any improvements to the UI or backend logic are welcome!

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

👤 Author Jay Bhatt Computer Science & Engineering Student Ahmedabad University

LinkedIn: https://www.linkedin.com/in/jay-bhatt-8a9013289/ GitHub: https://github.com/Jay888-DARK
