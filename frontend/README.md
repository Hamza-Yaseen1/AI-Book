# RAG Chatbot Frontend

This is the frontend for the RAG (Retrieval-Augmented Generation) chatbot that connects to the FastAPI backend.

## Features

- Modern chat interface for interacting with the RAG chatbot
- Real-time communication with the backend API
- Display of sources for retrieved information
- Responsive design for desktop and mobile
- Loading indicators during processing
- Error handling for connection issues

## Setup Instructions

### Prerequisites

- Backend server running (see `../openai_agent_retrieval/README.md`)
- Python 3.8+ for serving the frontend

### Starting the Backend Server

First, make sure your backend server is running:

```bash
cd ../openai_agent_retrieval
python main.py
```

This should start the backend server on `http://localhost:8000`.

### Serving the Frontend

#### Option 1: Using the Python server (recommended for development)

```bash
cd frontend
python server.py
```

This will start the frontend server on `http://localhost:3000`.

#### Option 2: Using a local web server

You can use any static file server. For example, with Node.js:

```bash
npx http-server
```

Or with Python 3:

```bash
python -m http.server 3000
```

### Accessing the Application

Open your browser and navigate to `http://localhost:3000` (or whatever port your frontend server is running on).

## Configuration

The frontend is configured to connect to the backend at `http://localhost:8000` by default. If your backend is running on a different port or address, update the `API_BASE_URL` constant in `script.js`.

## Usage

1. Type your question in the input field at the bottom
2. Press Enter or click the Send button
3. The chatbot will process your query and retrieve relevant information
4. Responses will appear in the chat window with source information

## Troubleshooting

### Connection Issues

- Ensure the backend server is running on the expected URL
- Check browser console for CORS or network errors
- Verify that the API endpoint is accessible by visiting `http://localhost:8000/health`

### Browser Compatibility

The frontend uses modern JavaScript features and should work in all modern browsers (Chrome, Firefox, Safari, Edge).

## Files

- `index.html` - Main HTML structure
- `styles.css` - Styling for the chat interface
- `script.js` - Frontend logic and API communication
- `server.py` - Simple server to serve frontend files