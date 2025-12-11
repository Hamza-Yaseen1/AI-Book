"""
Main entry point for Hugging Face Spaces deployment.
Runs FastAPI backend and serves frontend on the same application.
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the agent API
sys.path.insert(0, str(Path(__file__).parent / "openai_agent_retrieval"))
from openai_agent_retrieval.main import app as api_app

# Create main app
app = FastAPI(title="Physical AI Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API routes
app.mount("/api", api_app)

# Serve static frontend files
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    """Serve the main index.html"""
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend static files"""
    file_path = frontend_dir / full_path
    
    # If it's a file, serve it
    if file_path.is_file():
        return FileResponse(str(file_path))
    
    # If it's a directory or doesn't exist, serve index.html
    return FileResponse(str(frontend_dir / "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Physical AI Chatbot on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
