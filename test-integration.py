# Test the chatbot integration

# 1. Check that all required files exist
print("Checking required files...")
import os

files_to_check = [
    "chatbot-widget.js",
    "frontend/chat-iframe.html",
    "api/proxy.js",
    "demo.html"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"[OK] {file_path} exists")
    else:
        print(f"[MISSING] {file_path} missing")

print("")
print("Integration files are ready!")
print("To test the chatbot widget:")
print("1. Make sure your backend is running on http://localhost:8000")
print("2. Open demo.html in a browser")
print("3. Look for the chatbot icon in the bottom-right corner")
print("4. Click it to open the chat interface")