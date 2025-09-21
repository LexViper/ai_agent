"""
Database Module
Handles database setup, connections, and schema management for feedback logging.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, Float, Boolean, DateTime, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import select, insert, update, delete
from databases import Database
from loguru import logger
from datetime import datetime

# Database URL - will use SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./math_ai_agent.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./math_ai_agent.db")

# SQLAlchemy setup
Base = declarative_base()
metadata = MetaData()

# Define tables
query_logs_table = Table(
    "query_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("query_id", String(36), unique=True, nullable=False),
    Column("question", Text, nullable=False),
    Column("answer", Text, nullable=False),
    Column("confidence", Float, default=0.0),
    Column("sources", Text),  # JSON string
    Column("reasoning_steps", Text),  # JSON string
    Column("user_id", String(50), nullable=True),
    Column("timestamp", DateTime, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

feedback_table = Table(
    "feedback",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("feedback_id", String(36), unique=True, nullable=False),
    Column("query_id", String(36), nullable=False),
    Column("feedback_type", String(20), nullable=False),
    Column("feedback_text", Text, nullable=True),
    Column("corrected_answer", Text, nullable=True),
    Column("user_id", String(50), nullable=True),
    Column("processed", Boolean, default=False),
    Column("timestamp", DateTime, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

knowledge_base_table = Table(
    "knowledge_base",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("content_id", String(36), unique=True, nullable=False),
    Column("content", Text, nullable=False),
    Column("source", String(200), nullable=False),
    Column("metadata", Text),  # JSON string
    Column("embedding_vector", Text),  # JSON string for vector storage
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.database: Optional[Database] = None
        self.engine = None
        self.async_engine = None
        self.async_session = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize database connection and create tables."""
        try:
            # Create database connection
            self.database = Database(ASYNC_DATABASE_URL)
            
            # Create async engine for SQLAlchemy
            self.async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
            
            # Create async session factory
            AsyncSessionLocal = sessionmaker(
                bind=self.async_engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            self.async_session = AsyncSessionLocal
            
            # Connect to database
            await self.database.connect()
            
            # Create tables
            await self.create_tables()
            
            self.initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables if they don't exist."""
        try:
            # Create synchronous engine for table creation
            sync_engine = create_engine(DATABASE_URL)
            
            # Create all tables
            metadata.create_all(sync_engine)
            
            logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    async def close(self):
        """Close database connections."""
        try:
            if self.database:
                await self.database.disconnect()
            
            if self.async_engine:
                await self.async_engine.dispose()
            
            self.initialized = False
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    async def store_query_log(self, query_data: Dict[str, Any]) -> bool:
        """Store a query log entry."""
        try:
            if not self.initialized:
                await self.initialize()
            
            import json
            
            # Prepare data for insertion
            insert_data = {
                "query_id": query_data["query_id"],
                "question": query_data["question"],
                "answer": query_data["answer"],
                "confidence": query_data.get("confidence", 0.0),
                "sources": json.dumps(query_data.get("sources", [])),
                "reasoning_steps": json.dumps(query_data.get("reasoning_steps", [])),
                "user_id": query_data.get("user_id"),
                "timestamp": query_data.get("timestamp", datetime.utcnow()),
            }
            
            # Insert into database
            query = insert(query_logs_table).values(insert_data)
            await self.database.execute(query)
            
            logger.info(f"Stored query log: {query_data['query_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing query log: {e}")
            return False
    
    async def store_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Store a feedback entry."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Prepare data for insertion
            insert_data = {
                "feedback_id": feedback_data["feedback_id"],
                "query_id": feedback_data["query_id"],
                "feedback_type": feedback_data["feedback_type"],
                "feedback_text": feedback_data.get("feedback_text"),
                "corrected_answer": feedback_data.get("corrected_answer"),
                "user_id": feedback_data.get("user_id"),
                "processed": feedback_data.get("processed", False),
                "timestamp": feedback_data.get("timestamp", datetime.utcnow()),
            }
            
            # Insert into database
            query = insert(feedback_table).values(insert_data)
            await self.database.execute(query)
            
            logger.info(f"Stored feedback: {feedback_data['feedback_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
            return False
    
    async def get_query_log(self, query_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a query log by ID."""
        try:
            if not self.initialized:
                await self.initialize()
            
            query = select(query_logs_table).where(query_logs_table.c.query_id == query_id)
            result = await self.database.fetch_one(query)
            
            if result:
                import json
                return {
                    "query_id": result["query_id"],
                    "question": result["question"],
                    "answer": result["answer"],
                    "confidence": result["confidence"],
                    "sources": json.loads(result["sources"]) if result["sources"] else [],
                    "reasoning_steps": json.loads(result["reasoning_steps"]) if result["reasoning_steps"] else [],
                    "user_id": result["user_id"],
                    "timestamp": result["timestamp"],
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving query log {query_id}: {e}")
            return None
    
    async def get_feedback_for_query(self, query_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a specific query."""
        try:
            if not self.initialized:
                await self.initialize()
            
            query = select(feedback_table).where(feedback_table.c.query_id == query_id)
            results = await self.database.fetch_all(query)
            
            feedback_list = []
            for result in results:
                feedback_list.append({
                    "feedback_id": result["feedback_id"],
                    "query_id": result["query_id"],
                    "feedback_type": result["feedback_type"],
                    "feedback_text": result["feedback_text"],
                    "corrected_answer": result["corrected_answer"],
                    "user_id": result["user_id"],
                    "processed": result["processed"],
                    "timestamp": result["timestamp"].isoformat() if result["timestamp"] else None,
                })
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Error retrieving feedback for query {query_id}: {e}")
            return []
    
    async def store_knowledge_base_entry(self, content_data: Dict[str, Any]) -> bool:
        """Store a knowledge base entry."""
        try:
            if not self.initialized:
                await self.initialize()
            
            import json
            
            # Prepare data for insertion
            insert_data = {
                "content_id": content_data["content_id"],
                "content": content_data["content"],
                "source": content_data["source"],
                "metadata": json.dumps(content_data.get("metadata", {})),
                "embedding_vector": json.dumps(content_data.get("embedding_vector", [])),
            }
            
            # Insert into database
            query = insert(knowledge_base_table).values(insert_data)
            await self.database.execute(query)
            
            logger.info(f"Stored knowledge base entry: {content_data['content_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing knowledge base entry: {e}")
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Count records in each table
            query_logs_count = await self.database.fetch_val(
                select([query_logs_table.c.id]).count()
            )
            
            feedback_count = await self.database.fetch_val(
                select([feedback_table.c.id]).count()
            )
            
            knowledge_base_count = await self.database.fetch_val(
                select([knowledge_base_table.c.id]).count()
            )
            
            return {
                "query_logs": query_logs_count or 0,
                "feedback_entries": feedback_count or 0,
                "knowledge_base_entries": knowledge_base_count or 0,
                "database_url": DATABASE_URL,
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}

# Global database manager instance
db_manager = DatabaseManager()

async def init_database():
    """Initialize the database."""
    await db_manager.initialize()

async def get_database() -> Optional[Database]:
    """Get the database connection."""
    if not db_manager.initialized:
        await db_manager.initialize()
    return db_manager.database

async def close_database():
    """Close the database connection."""
    await db_manager.close()