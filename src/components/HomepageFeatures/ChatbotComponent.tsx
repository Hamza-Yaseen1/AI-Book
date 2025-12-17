import React, { useState, useRef, useEffect, JSX } from 'react';
import clsx from 'clsx';

type Message = {
    id: string;
    text: string;
    sender: 'user' | 'bot';
};

interface ChatbotComponentProps {
    onClose?: () => void;
}

export default function ChatbotComponent({ onClose }: ChatbotComponentProps): JSX.Element {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        // Send initial greeting when component mounts
        setMessages([
            {
                id: '1',
                text: "Hello 👋 I'm Hamza's Physical AI assistant. How can I help you today?",
                sender: 'bot'
            }
        ]);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Global Selection Listener
    useEffect(() => {
        const handleSelection = async () => {
            const selection = window.getSelection();
            if (selection && selection.toString().trim().length > 0) {
                const selectedText = selection.toString().trim();

                // Add selection query to chat
                const newMessage: Message = {
                    id: Date.now().toString(),
                    text: `Explain selection: "${selectedText.substring(0, 50)}..."`,
                    sender: 'user'
                };
                setMessages(prev => [...prev, newMessage]);
                setIsLoading(true);

                try {
                    const response = await fetch('https://hamza-11-chatbot.hf.space/api/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            question: "Explain this text in context of the course.",
                            selection: selectedText
                        })
                    });

                    if (!response.ok) throw new Error('Backend error');

                    const data = await response.json();

                    setMessages(prev => [...prev, {
                        id: (Date.now() + 1).toString(),
                        text: data.answer,
                        sender: 'bot'
                    }]);
                } catch (error) {
                    setMessages(prev => [...prev, {
                        id: (Date.now() + 1).toString(),
                        text: "Sorry, I couldn't process that selection. Ensure the backend is running.",
                        sender: 'bot'
                    }]);
                } finally {
                    setIsLoading(false);
                }
            }
        };

        const onMouseUp = () => {
            // slight delay to ensure selection is populated
            setTimeout(handleSelection, 100);
        };

        document.addEventListener('mouseup', onMouseUp);
        return () => document.removeEventListener('mouseup', onMouseUp);
    }, []);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const newUserMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            sender: 'user',
        };

        setMessages((prev) => [...prev, newUserMessage]);
        setInputValue('');

        // Check for greeting messages
        const lowerInput = inputValue.toLowerCase().trim();
        if (lowerInput === 'hi' || lowerInput === 'hello' || lowerInput === 'hey') {
            const greetingResponse: Message = {
                id: (Date.now() + 1).toString(),
                text: "Hello! I'm Hamza's Physical AI assistant. How can I assist you with the Physical AI course today?",
                sender: 'bot',
            };
            setMessages((prev) => [...prev, greetingResponse]);
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('https://hamza-11-chatbot.hf.space/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: newUserMessage.text })
            });

            if (!response.ok) throw new Error('Backend error');

            const data = await response.json();

            setMessages((prev) => [...prev, {
                id: (Date.now() + 1).toString(),
                text: data.answer,
                sender: 'bot',
            }]);
        } catch (error) {
            setMessages((prev) => [...prev, {
                id: (Date.now() + 1).toString(),
                text: "Error connecting to backend. Please try again later.",
                sender: 'bot',
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="chatbot-internal">
            <div className="chat-messages">
                {messages.map((msg) => (
                    <div key={msg.id} className={clsx('chat-message', msg.sender)}>
                        {msg.text}
                    </div>
                ))}
                {isLoading && <div className="chat-message bot">Thinking...</div>}
                <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-area">
                <input
                    type="text"
                    className="chat-input"
                    placeholder="Type a message..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                />
                <button className="chat-send" onClick={handleSendMessage} disabled={isLoading}>
                    ➤
                </button>
            </div>
        </div>
    );
}