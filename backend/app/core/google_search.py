"""
Google Custom Search API Integration for Math AI Agent

This module provides Google web search fallback functionality without modifying
existing knowledge base or Gemini API logic. It integrates as an additional
step in the query processing pipeline.

Author: Math AI Agent Team
Purpose: Add Google search fallback for enhanced answer quality
"""

import os
import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class GoogleSearchResult:
    """Structure for individual Google search results."""
    title: str
    snippet: str
    link: str
    display_link: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API responses."""
        return {
            "title": self.title,
            "snippet": self.snippet,
            "link": self.link,
            "display_link": self.display_link
        }


@dataclass
class GoogleSearchResponse:
    """Structure for complete Google search response."""
    query: str
    results: List[GoogleSearchResult]
    total_results: int
    search_time: float
    used_google_search: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "query": self.query,
            "results": [result.to_dict() for result in self.results],
            "total_results": self.total_results,
            "search_time": self.search_time,
            "used_google_search": self.used_google_search
        }


class GoogleSearchService:
    """
    Google Custom Search API service for math-related web search.
    
    This service provides fallback search functionality when the knowledge base
    returns low confidence results. It does NOT replace existing KB or Gemini logic.
    """
    
    def __init__(self):
        """Initialize Google Search service with API credentials."""
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Configuration
        self.max_results = 5  # Limit results for math queries
        self.timeout = 10     # Request timeout in seconds
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API credentials not configured - search fallback disabled")
            self.enabled = False
        else:
            logger.info("Google Search API initialized successfully")
            self.enabled = True
    
    async def search_math_query(self, query: str, context: Optional[str] = None) -> Optional[GoogleSearchResponse]:
        """
        Search Google for math-related content.
        
        Args:
            query: The mathematical question to search for
            context: Optional context to improve search results
            
        Returns:
            GoogleSearchResponse with search results or None if disabled/failed
        """
        if not self.enabled:
            logger.debug("Google Search disabled - skipping search")
            return None
        
        try:
            # Enhance query for better math results
            enhanced_query = self._enhance_math_query(query, context)
            
            # Perform the search
            search_results = await self._perform_search(enhanced_query)
            
            if search_results:
                logger.info(f"Google Search returned {len(search_results.results)} results for: {query}")
                return search_results
            else:
                logger.warning(f"Google Search returned no results for: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Google Search failed for query '{query}': {e}")
            return None
    
    def _enhance_math_query(self, query: str, context: Optional[str] = None) -> str:
        """
        Enhance the search query to get better math-related results.
        
        Args:
            query: Original math question
            context: Optional context
            
        Returns:
            Enhanced search query
        """
        # Add math-specific terms to improve results
        math_terms = ["mathematics", "math", "solve", "calculate", "formula"]
        
        # Check if query already contains math terms
        query_lower = query.lower()
        has_math_terms = any(term in query_lower for term in math_terms)
        
        if not has_math_terms:
            # Add "mathematics" to improve relevance
            enhanced_query = f"{query} mathematics"
        else:
            enhanced_query = query
        
        # Add context if provided
        if context:
            enhanced_query += f" {context}"
        
        # Limit query length
        if len(enhanced_query) > 200:
            enhanced_query = enhanced_query[:200]
        
        logger.debug(f"Enhanced query: '{query}' -> '{enhanced_query}'")
        return enhanced_query
    
    async def _perform_search(self, query: str) -> Optional[GoogleSearchResponse]:
        """
        Perform the actual Google Custom Search API call.
        
        Args:
            query: Enhanced search query
            
        Returns:
            GoogleSearchResponse or None if failed
        """
        import time
        start_time = time.time()
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": self.max_results,
            "safe": "active",  # Safe search for educational content
            "fields": "items(title,snippet,link,displayLink),searchInformation(totalResults)"
        }
        
        try:
            # Configure SSL context to handle certificate issues in development
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl_context=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    self.base_url, 
                    params=params, 
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        search_time = time.time() - start_time
                        
                        return self._parse_search_response(query, data, search_time)
                    else:
                        error_text = await response.text()
                        logger.error(f"Google Search API error {response.status}: {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Google Search timeout after {self.timeout}s for query: {query}")
            return None
        except Exception as e:
            logger.error(f"Google Search request failed: {e}")
            return None
    
    def _parse_search_response(self, query: str, data: Dict, search_time: float) -> GoogleSearchResponse:
        """
        Parse Google Custom Search API response.
        
        Args:
            query: Original search query
            data: API response data
            search_time: Time taken for search
            
        Returns:
            Parsed GoogleSearchResponse
        """
        results = []
        
        # Extract search results
        items = data.get("items", [])
        for item in items:
            result = GoogleSearchResult(
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                link=item.get("link", ""),
                display_link=item.get("displayLink", "")
            )
            results.append(result)
        
        # Extract total results count
        search_info = data.get("searchInformation", {})
        total_results = int(search_info.get("totalResults", 0))
        
        return GoogleSearchResponse(
            query=query,
            results=results,
            total_results=total_results,
            search_time=search_time,
            used_google_search=True
        )
    
    def format_results_for_gemini(self, search_response: GoogleSearchResponse) -> str:
        """
        Format Google search results for inclusion in Gemini API prompts.
        
        Args:
            search_response: Google search results
            
        Returns:
            Formatted string for Gemini prompt
        """
        if not search_response or not search_response.results:
            return ""
        
        formatted = "\n**Additional Web Search Results:**\n"
        
        for i, result in enumerate(search_response.results[:3], 1):  # Limit to top 3
            formatted += f"\n{i}. **{result.title}**\n"
            formatted += f"   {result.snippet}\n"
            formatted += f"   Source: {result.display_link}\n"
        
        return formatted
    
    def extract_references(self, search_response: GoogleSearchResponse) -> List[Dict[str, str]]:
        """
        Extract references from Google search results for frontend display.
        
        Args:
            search_response: Google search results
            
        Returns:
            List of reference dictionaries
        """
        if not search_response or not search_response.results:
            return []
        
        references = []
        for result in search_response.results[:3]:  # Top 3 results
            references.append({
                "title": result.title,
                "url": result.link,
                "source": "Google Search",
                "snippet": result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
            })
        
        return references


# Global Google Search service instance
google_search_service = GoogleSearchService()


async def search_google_fallback(query: str, context: Optional[str] = None) -> Optional[GoogleSearchResponse]:
    """
    Convenience function for Google search fallback.
    
    Args:
        query: Mathematical question
        context: Optional context
        
    Returns:
        Google search results or None
    """
    return await google_search_service.search_math_query(query, context)


def is_google_search_enabled() -> bool:
    """Check if Google Search is properly configured and enabled."""
    return google_search_service.enabled


def get_google_search_status() -> Dict[str, Any]:
    """Get Google Search service status for debugging."""
    return {
        "enabled": google_search_service.enabled,
        "has_api_key": bool(google_search_service.api_key),
        "has_search_engine_id": bool(google_search_service.search_engine_id),
        "max_results": google_search_service.max_results,
        "timeout": google_search_service.timeout
    }
