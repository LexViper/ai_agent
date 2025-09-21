import React, { useState } from 'react';
import styled from 'styled-components';
import InputBox from '../components/InputBox';
import AnswerDisplay from '../components/AnswerDisplay';
import FeedbackButtons from '../components/FeedbackButtons';
import ErrorModal from '../components/ErrorModal';
import { submitQuery, submitFeedback } from '../utils/api';

const HomeContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 120px);
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  
  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
  }
  
  @media (max-width: 480px) {
    gap: 1.5rem;
    padding: 0 0.5rem;
  }
`;

const QuerySection = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  animation: slideInFromLeft 0.6s ease-out;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    animation: fadeIn 0.6s ease-out;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
    border-radius: 12px;
  }
`;

const ResultSection = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  min-height: 400px;
  display: flex;
  flex-direction: column;
  animation: slideInFromRight 0.6s ease-out;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    min-height: 300px;
    animation: fadeIn 0.6s ease-out 0.2s both;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
    border-radius: 12px;
    min-height: 250px;
  }
`;

const SectionTitle = styled.h2`
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.4rem;
  font-weight: 600;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  color: #666;
  padding: 2rem;
  
  h3 {
    color: #333;
    margin-bottom: 1rem;
  }
  
  p {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }
`;

const ExampleQueries = styled.div`
  margin-top: 1.5rem;
  
  h4 {
    color: #333;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  li {
    background: rgba(103, 126, 234, 0.1);
    padding: 0.5rem 0.8rem;
    margin: 0.3rem 0;
    border-radius: 8px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba(103, 126, 234, 0.2);
      transform: translateX(4px);
    }
  }
`;

function Home() {
  const [currentQuery, setCurrentQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorModalData, setErrorModalData] = useState({});

  const handleQuerySubmit = async (question, context) => {
    setIsLoading(true);
    setError(null);
    setCurrentQuery(question);
    
    try {
      const result = await submitQuery(question, context);
      setQueryResult(result);
    } catch (err) {
      // Check if this is a non-mathematical question error
      if (err.status === 400 && err.data?.error === 'Non-mathematical question') {
        setErrorModalData({
          title: "Math Questions Only",
          message: "Please enter a valid math question. Only mathematical questions are allowed.",
          suggestions: [
            "Solve 3x + 7 = 10",
            "What is the derivative of x^2?",
            "Calculate 15 + 25",
            "Find the area of a circle with radius 8",
            "What is 25% of 80?"
          ]
        });
        setShowErrorModal(true);
        setError(null);
        setQueryResult(null);
      } else {
        setError(err.message || 'An error occurred while processing your query.');
        setQueryResult(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (feedbackType, feedbackText, correctedAnswer) => {
    if (!queryResult?.query_id) {
      alert('No query to provide feedback for.');
      return;
    }

    try {
      await submitFeedback({
        query_id: queryResult.query_id,
        feedback_type: feedbackType,
        feedback_text: feedbackText,
        corrected_answer: correctedAnswer,
      });
      
      // Show success message (could be enhanced with a toast notification)
      alert('Thank you for your feedback!');
    } catch (err) {
      alert('Error submitting feedback. Please try again.');
    }
  };

  const handleExampleClick = (example) => {
    handleQuerySubmit(example, null);
  };

  const handleCloseErrorModal = () => {
    setShowErrorModal(false);
    setErrorModalData({});
  };

  const exampleQueries = [
    "Solve: 2x + 5 = 13",
    "What is the derivative of x^2 + 3x?",
    "Find the area of a circle with radius 5",
    "Explain the Pythagorean theorem",
    "Calculate the integral of sin(x)",
  ];

  return (
    <HomeContainer>
      <ErrorModal
        isOpen={showErrorModal}
        onClose={handleCloseErrorModal}
        title={errorModalData.title}
        message={errorModalData.message}
        suggestions={errorModalData.suggestions}
      />
      <MainContent>
        <QuerySection>
          <SectionTitle>Ask Your Math Question</SectionTitle>
          <InputBox onSubmit={handleQuerySubmit} isLoading={isLoading} />
          
          <ExampleQueries>
            <h4>Try these examples:</h4>
            <ul>
              {exampleQueries.map((example, index) => (
                <li 
                  key={index} 
                  onClick={() => handleExampleClick(example)}
                >
                  {example}
                </li>
              ))}
            </ul>
          </ExampleQueries>
        </QuerySection>

        <ResultSection>
          <SectionTitle>Answer & Solution</SectionTitle>
          
          {!queryResult && !isLoading && !error && (
            <WelcomeMessage>
              <h3>Welcome to Math AI Agent! 🧮</h3>
              <p>Ask me any mathematical question and I'll help you solve it.</p>
              <p>I can help with:</p>
              <p>• Algebra and equations</p>
              <p>• Calculus and derivatives</p>
              <p>• Geometry and trigonometry</p>
              <p>• Statistics and probability</p>
              <p>• And much more!</p>
            </WelcomeMessage>
          )}
          
          <AnswerDisplay 
            result={queryResult}
            isLoading={isLoading}
            error={error}
            query={currentQuery}
          />
          
          {queryResult && !isLoading && (
            <FeedbackButtons 
              onFeedback={handleFeedback}
              queryId={queryResult.query_id}
            />
          )}
        </ResultSection>
      </MainContent>
    </HomeContainer>
  );
}

export default Home;