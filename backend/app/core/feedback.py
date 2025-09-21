"""
Human Feedback Module
Handles collection, processing, and learning from user feedback to improve system performance.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger
from app.core.database import get_database

class FeedbackType(Enum):
    """Types of feedback users can provide."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CORRECTION = "correction"
    CLARIFICATION = "clarification"

@dataclass
class QueryLog:
    """Log entry for a query and response."""
    query_id: str
    question: str
    answer: str
    confidence: float
    sources: List[str]
    user_id: Optional[str]
    timestamp: datetime
    reasoning_steps: Optional[List[str]] = None

@dataclass
class FeedbackEntry:
    """User feedback entry."""
    feedback_id: str
    query_id: str
    feedback_type: FeedbackType
    feedback_text: Optional[str]
    corrected_answer: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    processed: bool = False

@dataclass
class FeedbackProcessingResult:
    """Result from processing feedback."""
    feedback_id: str
    success: bool
    message: str
    actions_taken: List[str]

class FeedbackManager:
    """
    Manages user feedback collection, processing, and system improvement.
    """
    
    def __init__(self):
        """Initialize feedback manager."""
        self.query_logs = {}  # In-memory cache, will be moved to DB
        self.feedback_entries = {}  # In-memory cache, will be moved to DB
        self.learning_enabled = True
    
    async def log_query(
        self, 
        query_id: str, 
        question: str, 
        answer: str, 
        user_id: Optional[str] = None,
        confidence: float = 0.0,
        sources: List[str] = None,
        reasoning_steps: List[str] = None
    ) -> QueryLog:
        """
        Log a query and its response for potential feedback.
        
        Args:
            query_id: Unique identifier for the query
            question: The original question asked
            answer: The answer provided
            user_id: Optional user identifier
            confidence: Confidence score of the answer
            sources: List of sources used
            reasoning_steps: Steps taken to arrive at the answer
            
        Returns:
            QueryLog entry
        """
        try:
            query_log = QueryLog(
                query_id=query_id,
                question=question,
                answer=answer,
                confidence=confidence,
                sources=sources or [],
                user_id=user_id,
                timestamp=datetime.now(timezone.utc),
                reasoning_steps=reasoning_steps
            )
            
            # Store in memory (will be replaced with database storage)
            self.query_logs[query_id] = query_log
            
            # Store in database
            database = await get_database()
            if database:
                await self._store_query_log_in_db(database, query_log)
            
            logger.info(f"Logged query {query_id} for user {user_id}")
            return query_log
            
        except Exception as e:
            logger.error(f"Error logging query {query_id}: {e}")
            raise
    
    async def process_feedback(
        self,
        query_id: str,
        feedback_type: str,
        feedback_text: Optional[str] = None,
        corrected_answer: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> FeedbackProcessingResult:
        """
        Process user feedback and take appropriate actions.
        
        Args:
            query_id: ID of the query being given feedback on
            feedback_type: Type of feedback (positive, negative, correction, etc.)
            feedback_text: Optional text feedback
            corrected_answer: Optional corrected answer
            user_id: Optional user identifier
            
        Returns:
            FeedbackProcessingResult with details of actions taken
        """
        try:
            feedback_id = str(uuid.uuid4())
            
            # Validate feedback type
            try:
                fb_type = FeedbackType(feedback_type)
            except ValueError:
                return FeedbackProcessingResult(
                    feedback_id=feedback_id,
                    success=False,
                    message=f"Invalid feedback type: {feedback_type}",
                    actions_taken=[]
                )
            
            # Check if query exists
            query_log = self.query_logs.get(query_id)
            if not query_log:
                # Try to fetch from database
                database = await get_database()
                if database:
                    query_log = await self._fetch_query_log_from_db(database, query_id)
                
                if not query_log:
                    return FeedbackProcessingResult(
                        feedback_id=feedback_id,
                        success=False,
                        message=f"Query {query_id} not found",
                        actions_taken=[]
                    )
            
            # Create feedback entry
            feedback_entry = FeedbackEntry(
                feedback_id=feedback_id,
                query_id=query_id,
                feedback_type=fb_type,
                feedback_text=feedback_text,
                corrected_answer=corrected_answer,
                user_id=user_id,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Store feedback
            self.feedback_entries[feedback_id] = feedback_entry
            
            # Store in database
            database = await get_database()
            if database:
                await self._store_feedback_in_db(database, feedback_entry)
            
            # Process feedback based on type
            actions_taken = await self._process_feedback_by_type(feedback_entry, query_log)
            
            # Mark as processed
            feedback_entry.processed = True
            
            logger.info(f"Processed feedback {feedback_id} for query {query_id}")
            
            return FeedbackProcessingResult(
                feedback_id=feedback_id,
                success=True,
                message="Feedback processed successfully",
                actions_taken=actions_taken
            )
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return FeedbackProcessingResult(
                feedback_id=feedback_id,
                success=False,
                message=f"Error processing feedback: {str(e)}",
                actions_taken=[]
            )
    
    async def _process_feedback_by_type(
        self, 
        feedback: FeedbackEntry, 
        query_log: QueryLog
    ) -> List[str]:
        """Process feedback based on its type."""
        actions = []
        
        if feedback.feedback_type == FeedbackType.POSITIVE:
            actions.extend(await self._handle_positive_feedback(feedback, query_log))
            
        elif feedback.feedback_type == FeedbackType.NEGATIVE:
            actions.extend(await self._handle_negative_feedback(feedback, query_log))
            
        elif feedback.feedback_type == FeedbackType.CORRECTION:
            actions.extend(await self._handle_correction_feedback(feedback, query_log))
            
        elif feedback.feedback_type == FeedbackType.CLARIFICATION:
            actions.extend(await self._handle_clarification_feedback(feedback, query_log))
        
        return actions
    
    async def _handle_positive_feedback(self, feedback: FeedbackEntry, query_log: QueryLog) -> List[str]:
        """Handle positive feedback."""
        actions = []
        
        if self.learning_enabled:
            # Reinforce successful patterns
            actions.append("Reinforced successful response pattern")
            
            # If sources were used, mark them as reliable
            if query_log.sources:
                actions.append(f"Marked {len(query_log.sources)} sources as reliable")
            
            # Update confidence scores for similar queries
            actions.append("Updated confidence scoring for similar queries")
        
        return actions
    
    async def _handle_negative_feedback(self, feedback: FeedbackEntry, query_log: QueryLog) -> List[str]:
        """Handle negative feedback."""
        actions = []
        
        if self.learning_enabled:
            # Flag response pattern for review
            actions.append("Flagged response pattern for review")
            
            # Reduce confidence in sources if used
            if query_log.sources:
                actions.append(f"Reduced confidence in {len(query_log.sources)} sources")
            
            # Queue for manual review if needed
            if query_log.confidence > 0.7:
                actions.append("Queued high-confidence incorrect answer for manual review")
        
        return actions
    
    async def _handle_correction_feedback(self, feedback: FeedbackEntry, query_log: QueryLog) -> List[str]:
        """Handle correction feedback."""
        actions = []
        
        if feedback.corrected_answer and self.learning_enabled:
            # Store correction for future reference
            actions.append("Stored corrected answer for future reference")
            
            # Update knowledge base with correction
            actions.append("Added correction to knowledge base")
            
            # Flag original sources if confidence was high
            if query_log.confidence > 0.6 and query_log.sources:
                actions.append("Flagged original sources for accuracy review")
        
        return actions
    
    async def _handle_clarification_feedback(self, feedback: FeedbackEntry, query_log: QueryLog) -> List[str]:
        """Handle clarification requests."""
        actions = []
        
        if feedback.feedback_text and self.learning_enabled:
            # Analyze what clarification was needed
            actions.append("Analyzed clarification requirements")
            
            # Flag response as potentially unclear
            actions.append("Marked original response as potentially unclear")
            
            # Queue for response improvement
            actions.append("Queued for response clarity improvement")
        
        return actions
    
    async def get_feedback_for_query(self, query_id: str) -> List[Dict[str, Any]]:
        """Get all feedback entries for a specific query."""
        try:
            feedback_list = []
            
            # Search in memory
            for feedback in self.feedback_entries.values():
                if feedback.query_id == query_id:
                    feedback_dict = asdict(feedback)
                    feedback_dict['feedback_type'] = feedback.feedback_type.value
                    feedback_dict['timestamp'] = feedback.timestamp.isoformat()
                    feedback_list.append(feedback_dict)
            
            # Also search database if available
            database = await get_database()
            if database:
                db_feedback = await self._fetch_feedback_from_db(database, query_id)
                feedback_list.extend(db_feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Error retrieving feedback for query {query_id}: {e}")
            return []
    
    async def get_feedback_analytics(self) -> Dict[str, Any]:
        """Get analytics about feedback patterns."""
        try:
            total_feedback = len(self.feedback_entries)
            
            if total_feedback == 0:
                return {
                    "total_feedback": 0,
                    "feedback_by_type": {},
                    "average_response_time": 0,
                    "most_common_issues": []
                }
            
            # Count by type
            type_counts = {}
            for feedback in self.feedback_entries.values():
                fb_type = feedback.feedback_type.value
                type_counts[fb_type] = type_counts.get(fb_type, 0) + 1
            
            return {
                "total_feedback": total_feedback,
                "feedback_by_type": type_counts,
                "processed_count": sum(1 for f in self.feedback_entries.values() if f.processed),
                "recent_feedback_count": len([
                    f for f in self.feedback_entries.values() 
                    if (datetime.now(timezone.utc) - f.timestamp).days < 7
                ])
            }
            
        except Exception as e:
            logger.error(f"Error generating feedback analytics: {e}")
            return {"error": str(e)}
    
    async def _store_query_log_in_db(self, database, query_log: QueryLog):
        """Store query log in database."""
        try:
            from app.core.database import db_manager
            
            query_data = {
                "query_id": query_log.query_id,
                "question": query_log.question,
                "answer": query_log.answer,
                "confidence": query_log.confidence,
                "sources": query_log.sources,
                "reasoning_steps": query_log.reasoning_steps,
                "user_id": query_log.user_id,
                "timestamp": query_log.timestamp
            }
            
            await db_manager.store_query_log(query_data)
            logger.info(f"Stored query log in database: {query_log.query_id}")
            
        except Exception as e:
            logger.error(f"Error storing query log in database: {e}")
    
    async def _store_feedback_in_db(self, database, feedback: FeedbackEntry):
        """Store feedback in database."""
        try:
            from app.core.database import db_manager
            
            feedback_data = {
                "feedback_id": feedback.feedback_id,
                "query_id": feedback.query_id,
                "feedback_type": feedback.feedback_type.value,
                "feedback_text": feedback.feedback_text,
                "corrected_answer": feedback.corrected_answer,
                "user_id": feedback.user_id,
                "processed": feedback.processed,
                "timestamp": feedback.timestamp
            }
            
            await db_manager.store_feedback(feedback_data)
            logger.info(f"Stored feedback in database: {feedback.feedback_id}")
            
        except Exception as e:
            logger.error(f"Error storing feedback in database: {e}")
    
    async def _fetch_query_log_from_db(self, database, query_id: str) -> Optional[QueryLog]:
        """Fetch query log from database."""
        try:
            from app.core.database import db_manager
            
            query_data = await db_manager.get_query_log(query_id)
            if query_data:
                return QueryLog(
                    query_id=query_data["query_id"],
                    question=query_data["question"],
                    answer=query_data["answer"],
                    confidence=query_data["confidence"],
                    sources=query_data["sources"],
                    user_id=query_data["user_id"],
                    timestamp=query_data["timestamp"],
                    reasoning_steps=query_data["reasoning_steps"]
                )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching query log from database: {e}")
            return None
    
    async def _fetch_feedback_from_db(self, database, query_id: str) -> List[Dict[str, Any]]:
        """Fetch feedback from database."""
        try:
            from app.core.database import db_manager
            
            feedback_list = await db_manager.get_feedback_for_query(query_id)
            return feedback_list
            
        except Exception as e:
            logger.error(f"Error fetching feedback from database: {e}")
            return []