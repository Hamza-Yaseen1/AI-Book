import React from 'react';
import './ChatButton.css';

const ChatButton = ({ onClick, isOpen }) => {
  if (isOpen) return null;

  return (
    <button
      className="chat-button"
      onClick={onClick}
      aria-label="Open chat"
      title="AI Assistant"
    >
      <svg
        className="chat-button-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    </button>
  );
};

export default ChatButton;