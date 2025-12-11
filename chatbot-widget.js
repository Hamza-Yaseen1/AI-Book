// Floating Chatbot Widget
(function() {
    // Configuration
    const API_BASE_URL = window.location.origin.includes('hf.space')
        ? `${window.location.origin}`
        : 'http://localhost:8000';

    // Create the chatbot widget
    function createChatbotWidget() {
        // Create the chatbot container
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'chatbot-container';
        chatbotContainer.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        `;

        // Create the chatbot icon button
        const chatbotIcon = document.createElement('div');
        chatbotIcon.id = 'chatbot-icon';
        chatbotIcon.style.cssText = `
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        `;

        // Create the chat icon inside the button
        const chatIcon = document.createElement('div');
        chatIcon.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H16L13 20C12.843 19.9999 12.6871 19.9637 12.543 19.8937C12.3989 19.8236 12.2698 19.721 12.1647 19.592C12.0596 19.463 11.9807 19.3104 11.9336 19.145C11.8865 18.9795 11.8723 18.8049 11.892 18.633L12.5 15H7C6.46957 15 5.96086 14.7893 5.58579 14.4142C5.21071 14.0391 5 13.5304 5 13V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V13C19 13.5304 18.7893 14.0391 18.4142 14.4142C18.0391 14.7893 17.5304 15 17 15H16Z"
                      stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 9H15" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M9 13H13" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
        `;
        chatIcon.style.cssText = `
            color: white;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        chatbotIcon.appendChild(chatIcon);

        // Create the chat window (initially hidden)
        const chatWindow = document.createElement('div');
        chatWindow.id = 'chatbot-window';
        chatWindow.style.cssText = `
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 400px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            display: none;
            flex-direction: column;
            overflow: hidden;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
        `;

        // Create the chat header
        const chatHeader = document.createElement('div');
        chatHeader.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;

        const headerTitle = document.createElement('h3');
        headerTitle.textContent = 'AI Assistant';
        headerTitle.style.cssText = `
            margin: 0;
            font-size: 16px;
        `;

        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        chatHeader.appendChild(headerTitle);
        chatHeader.appendChild(closeBtn);

        // Create iframe to load the chat interface
        const chatIframe = document.createElement('iframe');
        chatIframe.src = 'frontend/chat-iframe.html'; // Point to the iframe-optimized chat interface
        chatIframe.style.cssText = `
            flex: 1;
            border: none;
            width: 100%;
        `;

        chatWindow.appendChild(chatHeader);
        chatWindow.appendChild(chatIframe);

        // Add event listeners
        chatbotIcon.addEventListener('click', function() {
            chatWindow.style.display = 'flex';
            setTimeout(() => {
                chatWindow.style.opacity = '1';
                chatWindow.style.transform = 'translateY(0)';
            }, 10);
        });

        closeBtn.addEventListener('click', function() {
            chatWindow.style.opacity = '0';
            chatWindow.style.transform = 'translateY(20px)';
            setTimeout(() => {
                chatWindow.style.display = 'none';
            }, 300);
        });

        // Close chat window when clicking outside
        document.addEventListener('click', function(event) {
            if (!chatbotContainer.contains(event.target) &&
                chatWindow.style.display === 'flex' &&
                chatWindow.style.opacity === '1') {
                chatWindow.style.opacity = '0';
                chatWindow.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    chatWindow.style.display = 'none';
                }, 300);
            }
        });

        // Add elements to container
        chatbotContainer.appendChild(chatWindow);
        chatbotContainer.appendChild(chatbotIcon);

        // Add container to body
        document.body.appendChild(chatbotContainer);

        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(102, 126, 234, 0); }
                100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
            }

            #chatbot-icon:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
            }

            #chatbot-icon.pulse {
                animation: pulse 2s infinite;
            }
        `;
        document.head.appendChild(style);

        // Add a small delay to show the pulse animation
        setTimeout(() => {
            chatbotIcon.classList.add('pulse');
        }, 1000);
    }

    // Initialize the chatbot widget when the page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createChatbotWidget);
    } else {
        createChatbotWidget();
    }
})();