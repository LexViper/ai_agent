import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Home from './pages/Home';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
`;

const Header = styled.header`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Title = styled.h1`
  color: white;
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
`;

const Subtitle = styled.p`
  color: rgba(255, 255, 255, 0.8);
  margin: 0.5rem 0 0 0;
  text-align: center;
  font-size: 0.9rem;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Header>
          <Title>🧮 Math AI Agent</Title>
          <Subtitle>Your intelligent mathematical problem-solving assistant</Subtitle>
        </Header>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </AppContainer>
    </Router>
  );
}

export default App;