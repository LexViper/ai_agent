# Math AI Agent - Deployment Guide

## Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 14+ with npm/yarn
- Git

### Local Development Setup

1. **Clone and Setup Backend:**
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
```

2. **Setup Frontend:**
```bash
cd frontend
cp .env.example .env
npm install
```

3. **Start the Application:**

Backend (Terminal 1):
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (Terminal 2):
```bash
cd frontend
npm start
```

4. **Access the Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Configuration

### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite:///./math_ai_agent.db

# Optional AI API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Production Deployment

### Backend (Docker)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Build)
```bash
cd frontend
npm run build
# Deploy build/ folder to your static hosting service
```

## Features Implemented

✅ **Backend:**
- FastAPI with async/await patterns
- Vector-based knowledge base with ChromaDB
- Web search integration (simulated)
- Input/output filtering and guardrails
- Human feedback collection and processing
- SQLite database with async operations
- Comprehensive error handling and logging

✅ **Frontend:**
- React 18 with styled-components
- Responsive design with mobile support
- Real-time query processing
- Interactive feedback system
- Smooth animations and loading states
- Glass-morphism UI design

✅ **Testing:**
- Unit tests for core backend modules
- Test coverage for guardrails and knowledge base
- Pytest configuration with async support

## API Endpoints

### Core Endpoints
- `POST /api/v1/query` - Submit math questions
- `POST /api/v1/feedback` - Submit user feedback
- `GET /api/v1/query/{id}/feedback` - Get feedback for query
- `GET /health` - Health check

### Example Usage
```javascript
// Submit a math query
const response = await fetch('/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Solve 2x + 5 = 13",
    context: "Algebra homework"
  })
});
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │
│                 │    │                 │
│ • InputBox      │◄──►│ • Routes        │
│ • AnswerDisplay │    │ • Knowledge Base│
│ • Feedback      │    │ • Web Search    │
└─────────────────┘    │ • Guardrails    │
                       │ • Feedback      │
                       └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Database      │
                       │ • Query Logs    │
                       │ • Feedback      │
                       │ • Knowledge     │
                       └─────────────────┘
```

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Ensure frontend URL is in backend CORS_ORIGINS
   - Check that both services are running

2. **Database Errors:**
   - Verify DATABASE_URL in .env
   - Check file permissions for SQLite

3. **Import Errors:**
   - Ensure all dependencies are installed
   - Check Python path and virtual environment

### Debug Mode
```bash
# Backend debug
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Frontend debug
REACT_APP_DEBUG=true npm start
```

## Performance Optimization

- **Backend:** Async operations, connection pooling, response caching
- **Frontend:** Code splitting, lazy loading, memoization
- **Database:** Indexed queries, optimized schema

## Security Features

- Input validation and sanitization
- Output filtering for safety
- Rate limiting (configurable)
- CORS protection
- Content moderation

## Future Enhancements

- Real LLM integration (OpenAI/Anthropic)
- Actual web search APIs (Serper/Tavily)
- Advanced mathematical visualization
- Multi-language support
- Collaborative problem solving
- Mobile app development
