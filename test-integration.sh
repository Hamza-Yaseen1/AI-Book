# Test the chatbot integration

# 1. Check that all required files exist
echo "Checking required files..."
if [ -f "chatbot-widget.js" ]; then
    echo "✓ chatbot-widget.js exists"
else
    echo "✗ chatbot-widget.js missing"
fi

if [ -f "frontend/chat-iframe.html" ]; then
    echo "✓ frontend/chat-iframe.html exists"
else
    echo "✗ frontend/chat-iframe.html missing"
fi

if [ -f "api/proxy.js" ]; then
    echo "✓ api/proxy.js exists"
else
    echo "✗ api/proxy.js missing"
fi

if [ -f "demo.html" ]; then
    echo "✓ demo.html exists"
else
    echo "✗ demo.html missing"
fi

echo ""
echo "Integration files are ready!"
echo "To test the chatbot widget:"
echo "1. Make sure your backend is running on http://localhost:8000"
echo "2. Open demo.html in a browser"
echo "3. Look for the chatbot icon in the bottom-right corner"
echo "4. Click it to open the chat interface"