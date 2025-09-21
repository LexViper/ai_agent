import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';

const DisplayContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
`;

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
`;

const LoadingText = styled.div`
  color: #666;
  font-size: 1rem;
  margin-bottom: 0.5rem;
`;

const LoadingSubtext = styled.div`
  color: #999;
  font-size: 0.8rem;
`;

const ErrorContainer = styled.div`
  background: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 1.5rem;
  color: #c62828;
  text-align: center;
`;

const ErrorTitle = styled.h3`
  margin: 0 0 0.5rem 0;
  color: #d32f2f;
`;

const ResultContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const QueryDisplay = styled.div`
  background: #f8f9fa;
  border-left: 4px solid #667eea;
  padding: 1rem;
  border-radius: 0 8px 8px 0;
  margin-bottom: 1rem;
`;

const QueryLabel = styled.div`
  font-size: 0.8rem;
  color: #666;
  font-weight: 600;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const QueryText = styled.div`
  color: #333;
  font-size: 1rem;
  font-style: italic;
`;

const AnswerSection = styled.div`
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
`;

const AnswerHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.8rem 1.2rem;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

// NEW: Google Search Indicator Styles
const SearchIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
`;

const GoogleIcon = styled.span`
  font-size: 0.8rem;
`;

const ConfidenceScore = styled.div`
  background: rgba(255, 255, 255, 0.2);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const AnswerContent = styled.div`
  padding: 1.5rem;
  
  p {
    margin-bottom: 1rem;
    line-height: 1.6;
  }
  
  code {
    background: #f5f5f5;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9rem;
  }
  
  pre {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid #e9ecef;
  }
  
  blockquote {
    border-left: 4px solid #667eea;
    margin: 1rem 0;
    padding-left: 1rem;
    color: #666;
    background: #f8f9ff;
    padding: 1rem;
    border-radius: 0 6px 6px 0;
  }
  
  ul, ol {
    margin: 1rem 0;
    padding-left: 1.5rem;
  }
  
  li {
    margin-bottom: 0.5rem;
  }
`;

const MetadataSection = styled.div`
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  
  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
`;

const MetadataCard = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e9ecef;
`;

const MetadataTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const SourcesList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const SourceItem = styled.li`
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.5rem;
  margin-bottom: 0.3rem;
  font-size: 0.8rem;
  color: #666;
`;

const ReasoningSteps = styled.ol`
  margin: 0;
  padding-left: 1.2rem;
`;

const ReasoningStep = styled.li`
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.5rem;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
  color: #666;
`;

const AnswerDisplay = ({ result, isLoading, error, query }) => {
  if (isLoading) {
    return (
      <DisplayContainer>
        <LoadingContainer>
          <LoadingSpinner />
          <LoadingText>Solving your math problem...</LoadingText>
          <LoadingSubtext>This may take a few seconds</LoadingSubtext>
        </LoadingContainer>
      </DisplayContainer>
    );
  }

  if (error) {
    return (
      <DisplayContainer>
        <ErrorContainer>
          <ErrorTitle>⚠️ Error</ErrorTitle>
          <p>{error}</p>
          <div style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
            Please try rephrasing your question or check your internet connection.
          </div>
        </ErrorContainer>
      </DisplayContainer>
    );
  }

  if (!result) {
    return <DisplayContainer />;
  }

  const confidencePercentage = Math.round(result.confidence * 100);
  const confidenceColor = result.confidence >= 0.7 ? '#4caf50' : 
                         result.confidence >= 0.4 ? '#ff9800' : '#f44336';

  return (
    <DisplayContainer>
      <ResultContainer>
        {query && (
          <QueryDisplay>
            <QueryLabel>Your Question</QueryLabel>
            <QueryText>{query}</QueryText>
          </QueryDisplay>
        )}

        <AnswerSection>
          <AnswerHeader>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span>🤖 AI Solution</span>
              {/* NEW: Google Search Indicator */}
              {result.used_google_search && (
                <SearchIndicator>
                  <GoogleIcon>🔍</GoogleIcon>
                  <span>Enhanced with Google ({result.google_search_count} results)</span>
                </SearchIndicator>
              )}
            </div>
            <ConfidenceScore style={{ color: confidenceColor }}>
              {confidencePercentage}% confident
            </ConfidenceScore>
          </AnswerHeader>
          
          <AnswerContent>
            <ReactMarkdown>{result.answer}</ReactMarkdown>
          </AnswerContent>
        </AnswerSection>

        <MetadataSection>
          {result.sources && result.sources.length > 0 && (
            <MetadataCard>
              <MetadataTitle>📚 References</MetadataTitle>
              <SourcesList>
                {result.sources.slice(0, 3).map((source, index) => {
                  // Check if source contains a URL pattern
                  const urlMatch = source.match(/https?:\/\/[^\s)]+/);
                  const isClickableRef = source.includes('**[') && source.includes('](') && source.includes(')**');
                  
                  if (isClickableRef) {
                    // Parse markdown-style links
                    const linkMatch = source.match(/\*\*\[(.*?)\]\((.*?)\)\*\*\s*-\s*(.*)/);
                    if (linkMatch) {
                      const [, title, url, description] = linkMatch;
                      return (
                        <SourceItem key={index}>
                          <strong>
                            <a href={url} target="_blank" rel="noopener noreferrer" style={{color: '#667eea', textDecoration: 'none'}}>
                              {title}
                            </a>
                          </strong>
                          <br />
                          <small style={{color: '#666'}}>{description}</small>
                        </SourceItem>
                      );
                    }
                    // Fallback for malformed clickable refs
                    return <SourceItem key={index}>{source}</SourceItem>;
                  } else if (urlMatch) {
                    // Handle sources with embedded URLs
                    const url = urlMatch[0];
                    const title = source.replace(url, '').trim();
                    return (
                      <SourceItem key={index}>
                        <a href={url} target="_blank" rel="noopener noreferrer" style={{color: '#667eea', textDecoration: 'none'}}>
                          {title || `Reference ${index + 1}`}
                        </a>
                      </SourceItem>
                    );
                  } else {
                    // Regular source text
                    return <SourceItem key={index}>{source}</SourceItem>;
                  }
                })}
              </SourcesList>
            </MetadataCard>
          )}

          {result.reasoning_steps && result.reasoning_steps.length > 0 && (
            <MetadataCard>
              <MetadataTitle>🧠 Reasoning Steps</MetadataTitle>
              <ReasoningSteps>
                {result.reasoning_steps.map((step, index) => (
                  <ReasoningStep key={index}>{step}</ReasoningStep>
                ))}
              </ReasoningSteps>
            </MetadataCard>
          )}

          {/* NEW: Search Sources Information */}
          {(result.kb_confidence !== undefined || result.used_google_search) && (
            <MetadataCard>
              <MetadataTitle>🔍 Search Sources</MetadataTitle>
              <div style={{ fontSize: '0.85rem', color: '#666' }}>
                {result.kb_confidence !== undefined && (
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>Knowledge Base:</strong> {Math.round(result.kb_confidence * 100)}% confidence
                  </div>
                )}
                {result.used_google_search ? (
                  <div>
                    <strong>Google Search:</strong> ✅ Enhanced with {result.google_search_count} web results
                  </div>
                ) : (
                  <div>
                    <strong>Google Search:</strong> Not used (KB confidence sufficient)
                  </div>
                )}
              </div>
            </MetadataCard>
          )}
        </MetadataSection>
      </ResultContainer>
    </DisplayContainer>
  );
};

export default AnswerDisplay;