"""
Simple HTTP server to serve the frontend files for testing the integration.
"""
import http.server
import socketserver
import os
from pathlib import Path

# Get the directory where this script is located
CURRENT_DIR = Path(__file__).parent

class FrontendHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler to serve frontend files."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(CURRENT_DIR), **kwargs)

    def end_headers(self):
        # Add CORS headers to allow requests to the backend
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def run_server(port=3000):
    """Run the frontend server."""
    print(f"Starting frontend server on http://localhost:{port}")
    print(f"Serving files from: {CURRENT_DIR}")
    print("Make sure the backend server is running on http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")

    with socketserver.TCPServer(("", port), FrontendHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()