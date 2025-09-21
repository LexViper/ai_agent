# Math AI Agent - Backend 🚀

FastAPI-based backend server for the Math AI Agent system, providing intelligent mathematical problem-solving capabilities with knowledge base integration, web search, and human feedback learning.

## 🏗️ Architecture Overview

The backend follows a modular, async-first architecture:

```
app/
├── main.py              # FastAPI application & startup configuration
├── api/
│   └── routes.py        # REST API endpoints for queries & feedback
└── core/                # Business logic modules
    ├── knowledge_base.py    # Vector search & semantic knowledge retrieval
    ├── web_search.py        # MCP-compatible external search integration
    ├── guardrails.py        # Input/output safety & content moderation
    ├── feedback.py          # Human feedback processing & learning
    └── database.py          # Database operations & schema management
```

## ⚡ Quick Start

### 1. Environment Setup

```bash
# Create virtual environment (recommended)
python -m venv math-ai-env
source math-ai-env/bin/activate  # On Windows: math-ai-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./math_ai_agent.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./math_ai_agent.db

# AI Model API Keys (choose your preferred providers)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Logging & Debug
LOG_LEVEL=INFO
DEBUG=False

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### 3. Run the Server

```bash
# Development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Verify Installation

- **API Health**: http://localhost:8000/health
- **Interactive Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📚 API Endpoints

### Core Endpoints

#### POST `/api/v1/query`
Submit a mathematical query for AI-powered solving.

**Request:**
```json
{
  "question": "Solve the quadratic equation x^2 - 5x + 6 = 0",
  "context": "This is for calculus homework",
  "user_id": "optional_user_identifier"
}
```

**Response:**
```json
{
  "answer": "To solve x^2 - 5x + 6 = 0:\n1. Factor: (x-2)(x-3) = 0\n2. Solutions: x = 2 or x = 3",
  "confidence": 0.95,
  "sources": ["Knowledge Base", "Algebraic Rules"],
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "reasoning_steps": [
    "Identified quadratic equation format",
    "Applied factoring method",
    "Solved for x values"
  ]
}
```

#### POST `/api/v1/feedback`
Submit feedback to improve the AI system.

**Request:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "feedback_type": "positive|negative|correction|clarification",
  "feedback_text": "The explanation was very clear!",
  "corrected_answer": "Optional corrected answer for 'correction' type",
  "user_id": "optional_user_identifier"
}
```

#### GET `/api/v1/query/{query_id}/feedback`
Retrieve feedback history for a specific query.

### Health & Monitoring

#### GET `/health`
System health check endpoint.

#### GET `/api/v1/health`
API-specific health check with component status.

## 🧠 Core Modules

### Knowledge Base (`knowledge_base.py`)

Vector-based semantic search for mathematical knowledge:

```python
from app.core.knowledge_base import KnowledgeBase

kb = KnowledgeBase()
result = await kb.query("What is the derivative of x^2?")
```

**Features:**
- ChromaDB integration for vector storage
- Sentence transformers for embeddings
- Semantic similarity search
- Knowledge base management and statistics

### Web Search (`web_search.py`)

MCP-compatible external knowledge acquisition:

```python
from app.core.web_search import WebSearchAgent

search = WebSearchAgent()
result = await search.search_and_synthesize("calculus chain rule")
```

**Features:**
- Multiple search engine support (DuckDuckGo, Wolfram Alpha)
- Concurrent search execution
- Result synthesis and confidence scoring
- Math-specific query enhancement

### Guardrails (`guardrails.py`)

Safety and content moderation system:

```python
from app.core.guardrails import InputFilter, OutputFilter

input_filter = InputFilter()
result = await input_filter.process("Solve 2x + 5 = 13")
```

**Features:**
- Input validation and sanitization
- Output safety filtering
- Mathematical content appropriateness checks
- Confidence-based quality scoring

### Feedback System (`feedback.py`)

Human feedback processing and learning:

```python
from app.core.feedback import FeedbackManager

feedback = FeedbackManager()
await feedback.process_feedback(
    query_id="uuid",
    feedback_type="positive",
    feedback_text="Great explanation!"
)
```

**Features:**
- Feedback type classification
- Query logging and retrieval
- Learning from human corrections
- Feedback analytics and reporting

### Database Management (`database.py`)

Async database operations with SQLAlchemy:

```python
from app.core.database import get_database

db = await get_database()
stats = await db.get_database_stats()
```

**Features:**
- SQLite/PostgreSQL support
- Async database operations
- Query logging and feedback storage
- Database statistics and health monitoring

## 🗄️ Database Schema

### Query Logs Table
```sql
query_logs (
    id INTEGER PRIMARY KEY,
    query_id VARCHAR(36) UNIQUE NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    sources TEXT,  -- JSON array
    reasoning_steps TEXT,  -- JSON array
    user_id VARCHAR(50),
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Feedback Table
```sql
feedback (
    id INTEGER PRIMARY KEY,
    feedback_id VARCHAR(36) UNIQUE NOT NULL,
    query_id VARCHAR(36) NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,
    feedback_text TEXT,
    corrected_answer TEXT,
    user_id VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE,
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Knowledge Base Table
```sql
knowledge_base (
    id INTEGER PRIMARY KEY,
    content_id VARCHAR(36) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(200) NOT NULL,
    metadata TEXT,  -- JSON object
    embedding_vector TEXT,  -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./math_ai_agent.db` | Database connection string |
| `ASYNC_DATABASE_URL` | `sqlite+aiosqlite:///./math_ai_agent.db` | Async database URL |
| `OPENAI_API_KEY` | None | OpenAI API key for GPT models |
| `ANTHROPIC_API_KEY` | None | Anthropic API key for Claude |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DEBUG` | `False` | Enable debug mode |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins |

### Model Configuration

The system supports multiple AI providers. Configure in your environment:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mathaiagent
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: mathaiagent
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Configuration

```bash
# Production environment variables
DATABASE_URL=postgresql://user:password@localhost:5432/mathaiagent
LOG_LEVEL=WARNING
DEBUG=False
WORKERS=4

# Run with Gunicorn for production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 Monitoring & Logging

### Logging Configuration

The system uses `loguru` for structured logging:

```python
import loguru

# Log levels: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
logger.info("Query processed successfully", query_id=query_id, confidence=0.95)
```

### Health Monitoring

Monitor system health via endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed API health
curl http://localhost:8000/api/v1/health

# Database statistics
curl http://localhost:8000/api/v1/stats
```

### Metrics Collection

The system is ready for metrics integration:

- Response times per endpoint
- Query success/failure rates  
- Database query performance
- Feedback submission rates
- AI model response times

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── test_api/
│   ├── test_routes.py       # API endpoint tests
│   └── test_health.py       # Health check tests
├── test_core/
│   ├── test_knowledge_base.py   # Knowledge base tests
│   ├── test_web_search.py       # Web search tests
│   ├── test_guardrails.py       # Safety filter tests
│   ├── test_feedback.py         # Feedback system tests
│   └── test_database.py         # Database operation tests
└── conftest.py              # Test configuration
```

## 🔒 Security Considerations

### Input Validation
- All inputs are validated and sanitized
- SQL injection prevention via SQLAlchemy
- XSS protection on API responses

### Authentication (Ready for Implementation)
The system is structured to easily add authentication:

```python
# Add to routes.py
from fastapi import Depends
from app.auth import get_current_user

@router.post("/query")
async def solve_math_problem(
    query: MathQuery,
    user: User = Depends(get_current_user)
):
    # Implementation here
```

### Rate Limiting (Ready for Implementation)
```python
# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.add_middleware(SlowAPIMiddleware)
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check database URL
echo $DATABASE_URL

# Test database connection
python -c "from app.core.database import get_database; import asyncio; asyncio.run(get_database())"
```

**Import Errors:**
```bash
# Ensure you're in the backend directory
cd backend

# Check Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

**AI API Errors:**
```bash
# Verify API keys
python -c "import os; print('OPENAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Debug Mode

Enable comprehensive debugging:

```bash
DEBUG=True LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

## 📈 Performance Optimization

### Database Optimization
- Use connection pooling for production
- Add database indexes for frequent queries
- Implement query result caching

### AI Model Optimization
- Implement response caching for common queries
- Use async calls for multiple AI providers
- Add request batching for efficiency

### Memory Management
- Monitor ChromaDB memory usage
- Implement vector embedding caching
- Use background tasks for heavy operations

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
black app/
flake8 app/
mypy app/
```

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain async/await patterns
- Add logging for important operations

## 📚 Dependencies

### Core Dependencies
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding models
- **Loguru**: Structured logging
- **Pydantic**: Data validation and settings

### AI Integration
- **OpenAI**: GPT model integration
- **Anthropic**: Claude model integration
- **HTTPX**: Async HTTP client

### Development
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework
- **Black**: Code formatting
- **MyPy**: Type checking

---

