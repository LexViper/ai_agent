"""
Math AI Agent - FastAPI Backend
Entry point for the Math AI Agent system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables FIRST
load_dotenv()

from app.core.database import init_database
from app.api.routes import router
from loguru import logger

# Create FastAPI instance
app = FastAPI(
    title="Math AI Agent API",
    description="Backend API for Math AI Agent system with knowledge base integration and human feedback",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database and knowledge base on startup."""
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize and populate knowledge base
        from app.core.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        await kb.populate_initial_knowledge()
        logger.info("Knowledge base initialized and populated")
        
        logger.info("Math AI Agent startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Math AI Agent API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "math-ai-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)