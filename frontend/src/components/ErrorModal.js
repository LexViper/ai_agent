import React from 'react';
import './ErrorModal.css';

const ErrorModal = ({ isOpen, onClose, title, message, suggestions = [] }) => {
  if (!isOpen) return null;

  return (
    <div className="error-modal-overlay" onClick={onClose}>
      <div className="error-modal" onClick={(e) => e.stopPropagation()}>
        <div className="error-modal-header">
          <h3>{title || "Invalid Question"}</h3>
          <button className="error-modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="error-modal-body">
          <div className="error-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="#f59e0b" strokeWidth="2" fill="#fef3c7"/>
              <path d="M12 8v4m0 4h.01" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          
          <p className="error-message">{message}</p>
          
          {suggestions.length > 0 && (
            <div className="error-suggestions">
              <h4>Try asking questions like:</h4>
              <ul>
                {suggestions.map((suggestion, index) => (
                  <li key={index} className="suggestion-item">
                    <code>"{suggestion}"</code>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <div className="error-modal-footer">
          <button className="error-modal-button" onClick={onClose}>
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorModal;
