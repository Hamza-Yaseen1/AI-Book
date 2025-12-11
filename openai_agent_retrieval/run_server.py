"""
Script to run the OpenAI Agent with Qdrant Retrieval API server.
This provides an alternative way to start the server with custom options.
"""
import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config import HOST, PORT, DEBUG

def run_server():
    """Run the FastAPI server using uvicorn."""
    print(f"Starting OpenAI Agent with Qdrant Retrieval API server...")
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Debug mode: {DEBUG}")
    print(f"Access the API documentation at: http://{HOST}:{PORT}/docs")
    print("-" * 60)

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug",
        workers=1  # Adjust based on your needs
    )

if __name__ == "__main__":
    run_server()