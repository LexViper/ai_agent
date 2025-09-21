import React, { useState } from 'react';
import styled from 'styled-components';

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #999;
  }
`;

const ContextInput = styled.input`
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #999;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 0.8rem;
  align-items: center;
  
  @media (max-width: 480px) {
    flex-direction: column;
    gap: 0.6rem;
    
    button {
      width: 100%;
    }
  }
`;

const SubmitButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }
`;

const ClearButton = styled.button`
  background: transparent;
  color: #666;
  border: 2px solid #e0e0e0;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #ccc;
    background: #f5f5f5;
  }
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
`;

const CharCount = styled.div`
  font-size: 0.8rem;
  color: ${props => props.isNearLimit ? '#ff6b6b' : '#999'};
  text-align: right;
  margin-top: 0.3rem;
`;

const InputBox = ({ onSubmit, isLoading }) => {
  const [question, setQuestion] = useState('');
  const [context, setContext] = useState('');
  const maxLength = 1000;
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!question.trim()) {
      alert('Please enter a math question.');
      return;
    }
    
    if (question.length > maxLength) {
      alert(`Question is too long. Please limit to ${maxLength} characters.`);
      return;
    }
    
    onSubmit(question.trim(), context.trim() || null);
  };
  
  const handleClear = () => {
    setQuestion('');
    setContext('');
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit(e);
    }
  };
  
  const isNearLimit = question.length > maxLength * 0.8;
  
  return (
    <form onSubmit={handleSubmit}>
      <InputContainer>
        <TextArea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Enter your math question here... (e.g., 'Solve 2x + 5 = 13' or 'What is the derivative of x^2?')"
          disabled={isLoading}
          maxLength={maxLength}
        />
        <CharCount isNearLimit={isNearLimit}>
          {question.length}/{maxLength}
        </CharCount>
        
        <ContextInput
          type="text"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Optional context (e.g., 'This is for calculus homework' or 'I'm in grade 10')"
          disabled={isLoading}
        />
        
        <ButtonContainer>
          <SubmitButton type="submit" disabled={isLoading || !question.trim()}>
            {isLoading ? (
              <>
                <LoadingSpinner />
                Solving...
              </>
            ) : (
              <>
                🧮 Solve Problem
              </>
            )}
          </SubmitButton>
          
          <ClearButton type="button" onClick={handleClear} disabled={isLoading}>
            Clear
          </ClearButton>
        </ButtonContainer>
        
        <div style={{ fontSize: '0.8rem', color: '#666', textAlign: 'center' }}>
          Press Ctrl/Cmd + Enter to submit quickly
        </div>
      </InputContainer>
    </form>
  );
};

export default InputBox;