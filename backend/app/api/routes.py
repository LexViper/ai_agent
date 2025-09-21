"""
API Routes for Math AI Agent
Handles math queries, knowledge base integration, and user feedback.
"""

import uuid
from fastapi import APIRouter, HTTPException
from app.models.schemas import MathQuery, MathResponse, FeedbackRequest
from app.core.knowledge_base import KnowledgeBase
from app.core.web_search import WebSearchAgent
from app.core.guardrails import InputFilter, OutputFilter
from app.core.feedback import FeedbackManager
# Google Search Integration - NEW: Add Google search fallback capability
from app.core.google_search import google_search_service, GoogleSearchResponse
from loguru import logger

# Initialize core components
knowledge_base = KnowledgeBase()
web_search = WebSearchAgent()
input_filter = InputFilter()
output_filter = OutputFilter()
feedback_manager = FeedbackManager()

# Create router
router = APIRouter()

@router.post("/query", response_model=MathResponse)
async def solve_math_problem(query: MathQuery):
    """
    Process a math query using knowledge base and web search.
    """
    try:
        # Apply input filtering and guardrails
        filtered_query = await input_filter.process(query.question)
        
        if not filtered_query.is_safe:
            # Provide specific error messages for different issues
            if "non_mathematical" in filtered_query.issues:
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "error": "Non-mathematical question",
                        "message": filtered_query.message,
                        "suggestion": "Try asking questions like 'Solve 2x + 5 = 13' or 'What is the derivative of x^2?'"
                    }
                )
            else:
                raise HTTPException(status_code=400, detail=filtered_query.message)
        
        # STEP 1: Search knowledge base for existing answers (UNCHANGED)
        kb_result = await knowledge_base.query(filtered_query.content, query.context)
        kb_confidence = getattr(kb_result, 'confidence', 0.0) if kb_result else 0.0
        
        # STEP 2: Google Search Fallback - NEW: Add Google search if KB confidence is low
        google_search_data = None
        additional_context = ""
        
        if kb_confidence < 0.7:  # Only use Google search if KB confidence is low
            logger.info(f"KB confidence {kb_confidence} < 0.7, attempting Google search fallback")
            try:
                google_search_data = await google_search_service.search_math_query(
                    filtered_query.content, 
                    query.context
                )
                if google_search_data and google_search_data.results:
                    additional_context = google_search_service.format_results_for_gemini(google_search_data)
                    logger.info(f"Google search provided {len(google_search_data.results)} additional results")
                else:
                    logger.info("Google search returned no results")
            except Exception as e:
                logger.warning(f"Google search fallback failed: {e}")
        else:
            logger.info(f"KB confidence {kb_confidence} >= 0.7, skipping Google search")
        
        # STEP 3: Generate solution using Gemini API with enhanced context (ENHANCED, NOT CHANGED)
        from app.core.llm_service import llm_service
        
        try:
            # Combine original context with Google search results for Gemini
            enhanced_context = query.context or ""
            if additional_context:
                enhanced_context += additional_context
            
            # Get step-by-step solution from Gemini/LLM service
            llm_answer = await llm_service.generate_step_by_step_solution(
                filtered_query.content, 
                enhanced_context if enhanced_context else None
            )
            
            # STEP 4: Generate references from multiple sources (ENHANCED)
            # Start with existing web search references (UNCHANGED)
            references = web_search._generate_dynamic_references(filtered_query.content, [])
            
            # Add Google search references if available (NEW)
            if google_search_data and google_search_data.results:
                google_refs = google_search_service.extract_references(google_search_data)
                # Merge references, prioritizing Google results for first 2 slots
                combined_refs = google_refs[:2] + references[:1]  # 2 Google + 1 existing
                references = [{"title": ref["title"], "url": ref["url"]} for ref in combined_refs]
            else:
                # Keep existing reference format (UNCHANGED)
                references = references
            
            # STEP 5: Construct response with Google search indicators (ENHANCED)
            reasoning_steps = [
                "Processed mathematical question through AI system",
                f"Searched knowledge base (confidence: {kb_confidence:.2f})",
            ]
            
            # Add Google search step if used (NEW)
            if google_search_data and google_search_data.results:
                reasoning_steps.append(f"Enhanced with Google search ({len(google_search_data.results)} results)")
            
            reasoning_steps.extend([
                "Generated comprehensive step-by-step solution", 
                "Provided verification and detailed explanation",
                "Added relevant mathematical resources and references"
            ])
            
            # Always use LLM answer for math questions (Gemini preferred, fallback included)
            result = type('Result', (), {
                'answer': llm_answer,
                'confidence': 0.90 if "Gemini AI" in llm_answer else 0.75,  # Higher confidence for Gemini
                'sources': [ref['title'] if isinstance(ref, dict) else ref for ref in references[:3]],  # Exactly 3 references
                'query_id': str(uuid.uuid4()),
                'reasoning_steps': reasoning_steps,
                # NEW: Add Google search metadata for frontend
                'used_google_search': google_search_data is not None and len(google_search_data.results) > 0 if google_search_data else False,
                'google_search_count': len(google_search_data.results) if google_search_data and google_search_data.results else 0,
                'kb_confidence': kb_confidence
            })()
                
        except Exception as e:
            logger.error(f"Error in LLM solution generation: {e}")
            # Fallback to web search with enhanced math solving
            result = await web_search.search_and_synthesize(
                filtered_query.content, 
                context=query.context
            )
        
        # Apply output filtering
        filtered_output = await output_filter.process(result.answer)
        
        if not filtered_output.is_safe:
            raise HTTPException(status_code=500, detail="Generated response failed safety checks")
        
        # Create response with Google search metadata
        response = MathResponse(
            answer=filtered_output.content,
            confidence=result.confidence,
            sources=result.sources,
            query_id=result.query_id,
            reasoning_steps=result.reasoning_steps,
            # Add Google search metadata
            used_google_search=getattr(result, 'used_google_search', False),
            google_search_count=getattr(result, 'google_search_count', 0),
            kb_confidence=getattr(result, 'kb_confidence', 0.0)
        )
        
        # Log the query and response for potential feedback
        await feedback_manager.log_query(
            query_id=response.query_id,
            question=query.question,
            answer=response.answer,
            user_id=query.user_id
        )
        
        return response
        
    except HTTPException as he:
        # Re-raise HTTPExceptions (like non-math query errors) as-is
        raise he
    except Exception as e:
        logger.error(f"Error processing query '{query.question}': {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        error_message = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
        raise HTTPException(status_code=500, detail=f"Error processing query: {error_message}")

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback for improving the system.
    """
    try:
        result = await feedback_manager.process_feedback(
            query_id=feedback.query_id,
            feedback_type=feedback.feedback_type,
            feedback_text=feedback.feedback_text,
            corrected_answer=feedback.corrected_answer,
            user_id=feedback.user_id
        )
        
        return {"message": "Feedback received successfully", "feedback_id": result.feedback_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

@router.get("/query/{query_id}/feedback")
async def get_query_feedback(query_id: str):
    """
    Retrieve feedback for a specific query.
    """
    try:
        feedback_list = await feedback_manager.get_feedback_for_query(query_id)
        return {"query_id": query_id, "feedback": feedback_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback: {str(e)}")

@router.get("/health")
async def api_health():
    """API-specific health check."""
    return {"status": "healthy", "component": "api-routes"}