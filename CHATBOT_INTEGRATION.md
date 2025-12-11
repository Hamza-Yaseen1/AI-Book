# Physical-AI Book with Chatbot Integration

This project includes a floating chatbot widget that can be integrated into any webpage. The chatbot allows users to interact with your RAG (Retrieval-Augmented Generation) AI assistant.

## Integration Instructions

### Method 1: Simple Integration
To add the chatbot to any webpage:

1. Upload `chatbot-widget.js` to your server
2. Add the following script tag to your HTML before the closing `</body>` tag:

```html
<script src="path/to/chatbot-widget.js"></script>
```

### Method 2: For Vercel Deployment
If deploying on Vercel with the backend:

1. Place the `api/proxy.js` file in your Vercel project's `api` directory
2. Set the `BACKEND_URL` environment variable to point to your backend server
3. Add the chatbot widget script as described in Method 1

## How It Works

- A floating chatbot icon appears in the bottom-right corner of the page
- Clicking the icon opens the chat interface in a popup window
- The chat interface connects to your backend API
- Users can ask questions and get AI-powered responses based on your knowledge base

## Backend Configuration

The widget automatically detects the environment:
- On Hugging Face Spaces: Uses the same origin
- On Vercel: Uses the proxy API route at `/api/proxy`
- Locally: Defaults to `http://localhost:8000`

## Files Included

- `chatbot-widget.js`: The floating chatbot widget
- `frontend/chat-iframe.html`: Optimized chat interface for iframe embedding
- `api/proxy.js`: Vercel API route for proxying backend requests
- `demo.html`: Example implementation

## Environment Variables (for Vercel deployment)

Set the following environment variable:
- `BACKEND_URL`: URL of your backend server (e.g., `https://your-backend-app.fly.dev`)

## Testing

1. Start your backend server (usually on port 8000)
2. Open `demo.html` in a browser to test the integration
3. The chatbot icon should appear in the bottom-right corner
4. Click it to open the chat interface and start asking questions

## Customization

You can customize the chatbot widget by modifying:
- Colors in the CSS within `chatbot-widget.js`
- Position by changing the `bottom` and `right` values in the widget styles
- Size by adjusting the width and height of the chat window