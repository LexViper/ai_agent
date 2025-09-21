import React, { useState } from 'react';
import styled from 'styled-components';

const FeedbackContainer = styled.div`
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
`;

const FeedbackTitle = styled.h3`
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
`;

const ButtonRow = styled.div`
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
`;

const FeedbackButton = styled.button`
  padding: 0.6rem 1rem;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  
  &:hover {
    border-color: #667eea;
    background: #f8f9ff;
    transform: translateY(-1px);
  }
  
  &.positive {
    border-color: #4caf50;
    color: #4caf50;
    
    &:hover {
      background: #e8f5e8;
      border-color: #4caf50;
    }
  }
  
  &.negative {
    border-color: #f44336;
    color: #f44336;
    
    &:hover {
      background: #ffebee;
      border-color: #f44336;
    }
  }
  
  &.correction {
    border-color: #ff9800;
    color: #ff9800;
    
    &:hover {
      background: #fff3e0;
      border-color: #ff9800;
    }
  }
  
  &.clarification {
    border-color: #2196f3;
    color: #2196f3;
    
    &:hover {
      background: #e3f2fd;
      border-color: #2196f3;
    }
  }
`;

const FeedbackModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalTitle = styled.h3`
  margin: 0 0 1rem 0;
  color: #333;
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 100px;
  padding: 0.8rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 1rem;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const ModalButtons = styled.div`
  display: flex;
  gap: 0.8rem;
  justify-content: flex-end;
`;

const ModalButton = styled.button`
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &.primary {
    background: #667eea;
    color: white;
    
    &:hover {
      background: #5a6fd8;
    }
  }
  
  &.secondary {
    background: #e0e0e0;
    color: #666;
    
    &:hover {
      background: #d0d0d0;
    }
  }
`;

const ThankYouMessage = styled.div`
  background: #e8f5e8;
  border: 1px solid #c8e6c8;
  border-radius: 8px;
  padding: 1rem;
  color: #2e7d32;
  text-align: center;
  margin-top: 1rem;
  animation: fadeIn 0.3s ease-out;
`;

const FeedbackButtons = ({ onFeedback, queryId }) => {
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [feedbackText, setFeedbackText] = useState('');
  const [correctedAnswer, setCorrectedAnswer] = useState('');
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  const handleFeedbackClick = (type) => {
    if (type === 'positive') {
      // For positive feedback, submit immediately
      handleSubmitFeedback('positive', '', '');
    } else {
      // For other types, show modal for additional input
      setModalType(type);
      setShowModal(true);
      setFeedbackText('');
      setCorrectedAnswer('');
    }
  };

  const handleSubmitFeedback = async (type, text, correction) => {
    try {
      await onFeedback(type, text, correction);
      setFeedbackGiven(true);
      setShowModal(false);
      
      // Hide the thank you message after 3 seconds
      setTimeout(() => {
        setFeedbackGiven(false);
      }, 3000);
    } catch (error) {
      alert('Failed to submit feedback. Please try again.');
    }
  };

  const handleModalSubmit = () => {
    if (modalType === 'correction' && !correctedAnswer.trim()) {
      alert('Please provide a corrected answer.');
      return;
    }
    
    handleSubmitFeedback(modalType, feedbackText, correctedAnswer);
  };

  const getModalContent = () => {
    switch (modalType) {
      case 'negative':
        return {
          title: 'Help us improve',
          placeholder: 'What was wrong with this answer? (optional)',
          showCorrection: false
        };
      case 'correction':
        return {
          title: 'Provide a correction',
          placeholder: 'Additional comments (optional)',
          showCorrection: true
        };
      case 'clarification':
        return {
          title: 'Request clarification',
          placeholder: 'What would you like clarified?',
          showCorrection: false
        };
      default:
        return { title: '', placeholder: '', showCorrection: false };
    }
  };

  const modalContent = getModalContent();

  if (feedbackGiven) {
    return (
      <FeedbackContainer>
        <ThankYouMessage>
          ✨ Thank you for your feedback! It helps us improve.
        </ThankYouMessage>
      </FeedbackContainer>
    );
  }

  return (
    <>
      <FeedbackContainer>
        <FeedbackTitle>How was this answer?</FeedbackTitle>
        <ButtonRow>
          <FeedbackButton 
            className="positive"
            onClick={() => handleFeedbackClick('positive')}
          >
            👍 Helpful
          </FeedbackButton>
          
          <FeedbackButton 
            className="negative"
            onClick={() => handleFeedbackClick('negative')}
          >
            👎 Not helpful
          </FeedbackButton>
          
          <FeedbackButton 
            className="correction"
            onClick={() => handleFeedbackClick('correction')}
          >
            ✏️ Correct this
          </FeedbackButton>
          
          <FeedbackButton 
            className="clarification"
            onClick={() => handleFeedbackClick('clarification')}
          >
            ❓ Need clarification
          </FeedbackButton>
        </ButtonRow>
        
        <div style={{ fontSize: '0.8rem', color: '#666', textAlign: 'center' }}>
          Your feedback helps improve the AI's responses
        </div>
      </FeedbackContainer>

      {showModal && (
        <FeedbackModal onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <ModalContent>
            <ModalTitle>{modalContent.title}</ModalTitle>
            
            {modalContent.showCorrection && (
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#333' }}>
                  Corrected Answer:
                </label>
                <TextArea
                  value={correctedAnswer}
                  onChange={(e) => setCorrectedAnswer(e.target.value)}
                  placeholder="Please provide the correct answer..."
                  style={{ minHeight: '80px' }}
                />
              </div>
            )}
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#333' }}>
                Additional Comments:
              </label>
              <TextArea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder={modalContent.placeholder}
              />
            </div>
            
            <ModalButtons>
              <ModalButton 
                className="secondary"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </ModalButton>
              <ModalButton 
                className="primary"
                onClick={handleModalSubmit}
              >
                Submit Feedback
              </ModalButton>
            </ModalButtons>
          </ModalContent>
        </FeedbackModal>
      )}
    </>
  );
};

export default FeedbackButtons;