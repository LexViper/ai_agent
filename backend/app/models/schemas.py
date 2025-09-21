"""
Pydantic models for API request/response schemas.
"""

from typing import List, Optional
from pydantic import BaseModel

class MathQuery(BaseModel):
    """Model for incoming math queries."""
    question: str
    context: Optional[str] = None
    user_id: Optional[str] = None

class MathResponse(BaseModel):
    """Model for math query responses."""
    answer: str
    confidence: float
    sources: List[str]
    query_id: str
    reasoning_steps: Optional[List[str]] = None
    # NEW: Google Search Integration fields
    used_google_search: Optional[bool] = False
    google_search_count: Optional[int] = 0
    kb_confidence: Optional[float] = 0.0

class FeedbackRequest(BaseModel):
    """Model for user feedback."""
    query_id: str
    feedback_type: str  # "positive", "negative", "correction"
    feedback_text: Optional[str] = None
    corrected_answer: Optional[str] = None
    user_id: Optional[str] = None
