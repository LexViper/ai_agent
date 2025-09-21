

# Ai_agent 🧮

An AI-powered mathematical problem-solving system built with a **FastAPI backend** and **React frontend**. The ai_agent provides step-by-step math solutions, Google Gemini API integration, knowledge base support, web search, and robust safety guardrails.

## Features

- Google Gemini API for detailed math solutions  
- Step-by-step explanations for algebra, calculus, geometry, and more  
- Smart guardrails to reject non-mathematical queries  
- Responsive React UI with user-friendly error handling  
- Dynamic references with each answer  
- Real-time async processing and fast responses  
- Human feedback integration for continuous improvement  
- Database integration for storing queries and feedback  
- API documentation via Swagger/OpenAPI  

## Quick Start

### Prerequisites

- Python 3.8+ (recommend 3.10)  
- Node.js 16+ (recommend 18)  
- pip and npm (package managers)  
- (Optional) API Keys for Google Gemini and web search  

### Installation

```bash
# Clone the ai_agent repo
git clone https://github.com/LexViper/ai_agent.git
cd ai_agent

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In a separate terminal:

```bash
# Setup frontend
cd frontend
npm install
npm start
```

### Access

- Frontend UI: http://localhost:3000  
- Backend API docs: http://localhost:8000/docs  

## Usage Examples

- Basic math: `2 + 2`  
- Algebra: `Solve 3x + 7 = 10`  
- Calculus: `Derivative of x^2`  
- Geometry: `Area of circle radius 5`  
- Non-math queries show friendly error popup  

## API Example

```bash
curl -X POST "http://localhost:8000/api/v1/query" -H "Content-Type: application/json" -d '{
  "question": "Solve 2x + 4 = 2",
  "user_id": "test_user"
}'
```

## Configuration

Backend `.env` example:

```bash
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./math_ai_agent.db
CORS_ORIGINS=["http://localhost:3000"]
SECRET_KEY=your_secret_key_here
```

Frontend `.env` example:

```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Contributing

1. Fork the repo  
2. Create a branch `git checkout -b feature-name`  
3. Commit your changes `git commit -m 'Add feature'`  
4. Push and open a pull request  


