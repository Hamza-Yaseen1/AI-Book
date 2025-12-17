import React, { useState, useRef, useEffect } from 'react';
import ChatbotComponent from '../HomepageFeatures/ChatbotComponent';
import './ChatWindow.css';

const ChatWindow = ({ isOpen, onClose, isMobile }) => {
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setShowOverlay(true);
    } else {
      const timer = setTimeout(() => setShowOverlay(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  if (isMobile) {
    return (
      <>
        {showOverlay && <div className="chat-overlay" onClick={onClose} />}
        <div className={`chat-window chat-window--mobile ${showOverlay ? 'chat-window--open' : ''}`}>
          <div className="chat-header">
            <h3>Physical AI Assistant</h3>
            <button
              className="chat-close-btn"
              onClick={onClose}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className="chat-content">
            <ChatbotComponent onClose={onClose} />
          </div>
        </div>
      </>
    );
  }

  return (
    <div className={`chat-window ${showOverlay ? 'chat-window--open' : ''}`}>
      <div className="chat-header">
        <h3>Physical AI Assistant</h3>
        <button
          className="chat-close-btn"
          onClick={onClose}
          aria-label="Close chat"
        >
          ×
        </button>
      </div>
      <div className="chat-content">
        <ChatbotComponent onClose={onClose} />
      </div>
    </div>
  );
};

export default ChatWindow;