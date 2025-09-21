# Math AI Agent - Frontend 🎨

Modern React frontend for the Math AI Agent system, providing an intuitive interface for mathematical problem-solving with real-time AI responses and user feedback capabilities.

## 🎯 Overview

The frontend is built with React 18 and modern web technologies to deliver a responsive, accessible, and visually appealing user experience for mathematical problem-solving.

### Key Features

- **🧮 Intelligent Math Input**: Smart input interface with validation and math-specific enhancements
- **📊 Real-time AI Responses**: Live display of AI-powered mathematical solutions
- **💬 Interactive Feedback**: User feedback system to improve AI performance
- **📱 Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **⚡ Fast Performance**: Optimized React components with minimal re-renders
- **🎨 Modern UI**: Glass-morphism design with smooth animations

## 🏗️ Architecture

```
src/
├── components/           # Reusable React components
│   ├── InputBox.js      # Math query input with validation
│   ├── AnswerDisplay.js # AI response display with formatting
│   └── FeedbackButtons.js # User feedback interface
├── pages/               # Page components
│   └── Home.js         # Main application interface
├── utils/              # Utility functions
│   └── api.js         # API communication layer
├── App.js              # Root application component
├── App.css            # Global styles and animations
├── index.js           # React DOM rendering entry point
└── index.css          # Base CSS styles
```

## ⚡ Quick Start

### Prerequisites

- **Node.js 14+** (recommended: Node.js 18 LTS)
- **npm 7+** or **yarn 1.22+**

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or with yarn
yarn install
```

### Development Server

```bash
# Start development server
npm start
# or with yarn
yarn start

# The application will open at http://localhost:3000
```

### Build for Production

```bash
# Create production build
npm run build
# or with yarn
yarn build

# Serve production build locally (for testing)
npx serve -s build
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development

# Debug Settings
REACT_APP_DEBUG=false

# Optional: Analytics & Monitoring
REACT_APP_ANALYTICS_ID=your_analytics_id
```

### Environment-Specific Configuration

#### Development (`.env.development`)
```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_DEBUG=true
REACT_APP_LOG_LEVEL=debug
```

#### Production (`.env.production`)
```bash
REACT_APP_API_URL=https://your-api-domain.com/api/v1
REACT_APP_DEBUG=false
REACT_APP_LOG_LEVEL=error
```

## 📱 Components Overview

### InputBox Component

Smart math input interface with real-time validation and user experience enhancements.

**Features:**
- Character count with visual feedback
- Mathematical query validation
- Keyboard shortcuts (Ctrl/Cmd + Enter to submit)
- Context input for additional problem details
- Loading states during API calls

**Usage:**
```jsx
import InputBox from './components/InputBox';

<InputBox 
  onSubmit={handleQuerySubmit} 
  isLoading={isLoading} 
/>
```

### AnswerDisplay Component

Comprehensive display component for AI responses with rich formatting and metadata.

**Features:**
- Markdown rendering for mathematical expressions
- Confidence score visualization
- Source attribution display
- Reasoning steps breakdown
- Loading animations and error handling

**Usage:**
```jsx
import AnswerDisplay from './components/AnswerDisplay';

<AnswerDisplay 
  result={queryResult}
  isLoading={isLoading}
  error={error}
  query={originalQuery}
/>
```

### FeedbackButtons Component

Interactive feedback system for continuous AI improvement.

**Features:**
- Multiple feedback types (positive, negative, correction, clarification)
- Modal interfaces for detailed feedback
- Immediate feedback for positive responses
- Correction interface with text input

**Usage:**
```jsx
import FeedbackButtons from './components/FeedbackButtons';

<FeedbackButtons 
  onFeedback={handleFeedback}
  queryId={queryResult.query_id}
/>
```

## 🎨 Styling & Design System

### Design Philosophy

The interface uses a modern glass-morphism design with:
- **Gradient backgrounds** for visual depth
- **Backdrop blur effects** for layered UI elements
- **Smooth animations** for enhanced user experience
- **Responsive grid layouts** for all screen sizes

### Color Palette

```css
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --glass-bg: rgba(255, 255, 255, 0.95);
  --glass-border: rgba(255, 255, 255, 0.18);
  --shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  --text-primary: #333;
  --text-secondary: #666;
  --success-color: #4caf50;
  --warning-color: #ff9800;
  --error-color: #f44336;
}
```

### Component Styling

Using **styled-components** for component-scoped styling:

```jsx
import styled from 'styled-components';

const StyledContainer = styled.div`
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: var(--shadow);
`;
```

### Responsive Design

All components are mobile-first responsive:

```css
/* Mobile first */
.container {
  display: flex;
  flex-direction: column;
}

/* Tablet and desktop */
@media (min-width: 768px) {
  .container {
    flex-direction: row;
    gap: 2rem;
  }
}
```

## 🔌 API Integration

### API Client Configuration

The frontend uses Axios for API communications with comprehensive error handling:

```javascript
// src/utils/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request/Response interceptors for logging and error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Comprehensive error handling
    if (error.response?.status === 400) {
      throw new Error('Please check your input and try again');
    }
    // ... additional error handling
  }
);
```

### API Methods

#### Submit Math Query
```javascript
import { submitQuery } from '../utils/api';

const result = await submitQuery(
  "Solve x^2 + 5x + 6 = 0",
  "Quadratic equations homework",
  "optional_user_id"
);
```

#### Submit User Feedback
```javascript
import { submitFeedback } from '../utils/api';

await submitFeedback({
  query_id: "uuid-here",
  feedback_type: "positive",
  feedback_text: "Great explanation!",
  user_id: "optional_user_id"
});
```

#### Health Checks
```javascript
import { checkApiHealth } from '../utils/api';

const health = await checkApiHealth();
console.log('API Status:', health.status);
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm test
# or with yarn
yarn test

# Run tests with coverage
npm test -- --coverage
# or with yarn
yarn test --coverage

# Run tests in watch mode
npm test -- --watch
```

### Testing Structure

```
src/
├── __tests__/           # Test files
│   ├── components/
│   │   ├── InputBox.test.js
│   │   ├── AnswerDisplay.test.js
│   │   └── FeedbackButtons.test.js
│   ├── pages/
│   │   └── Home.test.js
│   └── utils/
│       └── api.test.js
├── setupTests.js        # Test setup configuration
└── testUtils.js         # Testing utilities
```

### Example Test

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import InputBox from '../components/InputBox';

test('submits query when form is submitted', () => {
  const handleSubmit = jest.fn();
  render(<InputBox onSubmit={handleSubmit} />);
  
  const input = screen.getByPlaceholderText(/enter your math question/i);
  const submitBtn = screen.getByText(/solve problem/i);
  
  fireEvent.change(input, { target: { value: 'solve 2x + 5 = 13' } });
  fireEvent.click(submitBtn);
  
  expect(handleSubmit).toHaveBeenCalledWith('solve 2x + 5 = 13', null);
});
```

## ⚡ Performance Optimization

### React Optimization

- **Memo Components**: Prevent unnecessary re-renders
```jsx
import React, { memo } from 'react';

const AnswerDisplay = memo(({ result, isLoading, error }) => {
  // Component implementation
});
```

- **Lazy Loading**: Code splitting for better performance
```jsx
import { lazy, Suspense } from 'react';

const FeedbackButtons = lazy(() => import('./components/FeedbackButtons'));

// Usage with Suspense
<Suspense fallback={<Loading />}>
  <FeedbackButtons />
</Suspense>
```

### Bundle Optimization

- **Tree Shaking**: Eliminate unused code
- **Code Splitting**: Split code by routes/features
- **Asset Optimization**: Optimize images and fonts

### Performance Monitoring

```javascript
// Web Vitals monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

## 📱 Mobile Optimization

### Responsive Design Patterns

- **Fluid Typography**: Scalable text across devices
- **Touch-Friendly Interfaces**: 44px minimum touch targets
- **Optimized Animations**: Reduced motion for better performance

### Mobile-Specific Features

```jsx
// Touch gesture support
import { useSwipeable } from 'react-swipeable';

const handlers = useSwipeable({
  onSwipedLeft: () => handleNextQuery(),
  onSwipedRight: () => handlePreviousQuery(),
});

<div {...handlers}>
  {/* Swipeable content */}
</div>
```

## 🚀 Deployment

### Static Hosting (Recommended)

#### Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
npm run build
netlify deploy --prod --dir=build
```

#### Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Docker Deployment

```dockerfile
# Multi-stage build
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Configuration for Deployment

```bash
# Production build with custom API URL
REACT_APP_API_URL=https://api.yourdomain.com/api/v1 npm run build

# Build with analytics
REACT_APP_ANALYTICS_ID=GA_TRACKING_ID npm run build
```

## 🔒 Security Best Practices

### Content Security Policy

```html
<!-- Add to public/index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline' fonts.googleapis.com;
               font-src 'self' fonts.gstatic.com;">
```

### Input Sanitization

```javascript
import DOMPurify from 'dompurify';

// Sanitize user input before display
const sanitizedInput = DOMPurify.sanitize(userInput);
```

### API Security

```javascript
// Secure API calls with request validation
const validateRequest = (data) => {
  if (!data.question || data.question.length > 1000) {
    throw new Error('Invalid question format');
  }
};
```

## 🐛 Troubleshooting

### Common Issues

#### CORS Errors
```javascript
// Check API configuration
console.log('API URL:', process.env.REACT_APP_API_URL);

// Verify backend CORS settings allow frontend origin
```

#### Build Failures
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for conflicting dependencies
npm ls
```

#### Performance Issues
```javascript
// Enable React Developer Tools Profiler
// Check for unnecessary re-renders and optimize with memo/useMemo

import { useMemo } from 'react';

const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(props);
}, [dependencies]);
```

### Debug Mode

Enable detailed logging in development:

```javascript
// Add to .env.development
REACT_APP_DEBUG=true

// Use in components
if (process.env.REACT_APP_DEBUG) {
  console.log('Debug info:', data);
}
```

## 📈 Analytics & Monitoring

### User Analytics

```javascript
// Google Analytics 4 integration
import { gtag } from 'ga-gtag';

// Track user interactions
const trackQuerySubmission = (query) => {
  gtag('event', 'query_submitted', {
    event_category: 'engagement',
    event_label: 'math_query',
    value: 1
  });
};
```

### Error Monitoring

```javascript
// Error boundary for crash reporting
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Send to error reporting service
    console.error('Application error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <FallbackComponent />;
    }
    return this.props.children;
  }
}
```

## 🎨 Customization Guide

### Theming

Customize the application appearance:

```javascript
// Create theme object
const theme = {
  colors: {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#4caf50',
    warning: '#ff9800',
    error: '#f44336'
  },
  fonts: {
    body: '-apple-system, BlinkMacSystemFont, sans-serif',
    monospace: 'Monaco, Consolas, monospace'
  }
};

// Use with styled-components ThemeProvider
import { ThemeProvider } from 'styled-components';

<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>
```

### Component Extensions

Extend existing components:

```jsx
// Extended InputBox with custom validation
const AdvancedInputBox = ({ onSubmit, customValidation, ...props }) => {
  const handleSubmit = (question, context) => {
    if (customValidation && !customValidation(question)) {
      return;
    }
    onSubmit(question, context);
  };

  return <InputBox onSubmit={handleSubmit} {...props} />;
};
```

## 📚 Dependencies

### Core Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.1",
  "axios": "^1.6.2",
  "styled-components": "^6.1.1",
  "react-markdown": "^9.0.1"
}
```

### Development Dependencies

```json
{
  "@testing-library/react": "^13.4.0",
  "@testing-library/jest-dom": "^5.17.0",
  "@testing-library/user-event": "^14.5.2",
  "react-scripts": "5.0.1"
}
```

## 🤝 Contributing

### Development Workflow

1. **Setup Development Environment**
   ```bash
   npm install
   npm start
   ```

2. **Follow Code Standards**
   - Use functional components with hooks
   - Implement proper prop validation
   - Write meaningful component tests
   - Follow responsive design principles

3. **Code Style Guidelines**
   ```javascript
   // Use destructuring for props
   const MyComponent = ({ title, onAction, isLoading }) => {
     // Component logic
   };
   
   // Use meaningful variable names
   const isSubmitButtonDisabled = isLoading || !question.trim();
   
   // Add comprehensive prop types (if using PropTypes)
   MyComponent.propTypes = {
     title: PropTypes.string.isRequired,
     onAction: PropTypes.func.isRequired,
     isLoading: PropTypes.bool
   };
   ```

### Testing Guidelines

- Write tests for all components
- Test user interactions and edge cases
- Mock API calls in tests
- Maintain high test coverage (>80%)

---
