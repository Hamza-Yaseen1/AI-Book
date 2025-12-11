// Configuration
// On Hugging Face Spaces, the backend will be on the same origin
const API_BASE_URL = window.location.origin.includes('hf.space') 
    ? `${window.location.origin}` 
    : 'http://localhost:8000';

console.log('API Base URL:', API_BASE_URL);

// DOM Elements
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-btn');
const loadingIndicator = document.getElementById('loading-indicator');

// State
let isProcessing = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupAutoResize();
});

// Set up event listeners
function setupEventListeners() {
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

// Auto-resize textarea
function setupAutoResize() {
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    });
}

// Handle sending a message
async function handleSendMessage() {
    const message = userInput.value.trim();

    if (!message || isProcessing) {
        return;
    }

    // Clear input and reset height
    userInput.value = '';
    userInput.style.height = 'auto';

    // Add user message to chat
    addMessage(message, 'user');

    try {
        await sendMessageToAPI(message);
    } catch (error) {
        console.error('Error sending message:', error);
        addErrorMessage('Sorry, there was an error processing your request. Please try again.');
    }
}

// Add a message to the chat
function addMessage(content, sender, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    let messageContent = `<div class="message-content">${formatMessageContent(content)}</div>`;

    if (sources && sources.length > 0) {
        messageContent += `
            <div class="sources-list">
                <h4>Sources:</h4>
                <ul>
                    ${sources.slice(0, 3).map(source =>
                        `<li><a href="${source.url}" target="_blank">${truncateString(source.text, 100)}</a></li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }

    messageDiv.innerHTML = messageContent;

    // Add timestamp
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const header = document.createElement('div');
    header.className = 'message-header';
    header.innerHTML = `<span>${sender === 'user' ? 'You' : 'Chatbot'}</span><span>${timestamp}</span>`;

    messageDiv.insertBefore(header, messageDiv.firstChild);

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add an error message to the chat
function addErrorMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error';

    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${content}</p>
        </div>
    `;

    // Add timestamp
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const header = document.createElement('div');
    header.className = 'message-header';
    header.innerHTML = `<span>Error</span><span>${timestamp}</span>`;

    messageDiv.insertBefore(header, messageDiv.firstChild);

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Send message to API and handle response
async function sendMessageToAPI(message) {
    setIsProcessing(true);

    try {
        showLoadingIndicator();

        console.log('Sending request to:', `${API_BASE_URL}/query`);
        
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: message,
                max_results: 5,
                include_sources: true
            })
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('API error response:', errorData);
            throw new Error(`API request failed with status ${response.status}: ${errorData.detail || 'Unknown error'}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        // Add bot response to chat
        if (data.response) {
            addMessage(data.response, 'bot', data.sources || []);
        } else {
            throw new Error('Invalid response format: missing response field');
        }

    } catch (error) {
        console.error('API Error:', error);
        addErrorMessage('Sorry, there was an error communicating with the server. ' + error.message + '. Please check that the backend is running and try again.');
    } finally {
        hideLoadingIndicator();
        setIsProcessing(false);
    }
}

// Show loading indicator
function showLoadingIndicator() {
    loadingIndicator.style.display = 'flex';
    scrollToBottom();
}

// Hide loading indicator
function hideLoadingIndicator() {
    loadingIndicator.style.display = 'none';
}

// Set processing state
function setIsProcessing(state) {
    isProcessing = state;
    sendButton.disabled = state;
}

// Scroll to bottom of messages
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Format message content (handle line breaks, etc.)
function formatMessageContent(content) {
    // Replace newlines with HTML line breaks
    return content.replace(/\n/g, '<br>');
}

// Truncate string with ellipsis
function truncateString(str, maxLength) {
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

// Health check to verify backend connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        console.error('Backend connection check failed:', error);
        return false;
    }
}

// Check backend connection on load
window.addEventListener('load', async () => {
    const isConnected = await checkBackendConnection();
    if (!isConnected) {
        addErrorMessage('Warning: Unable to connect to the backend server. Please make sure the FastAPI server is running on ' + API_BASE_URL);
    }
});