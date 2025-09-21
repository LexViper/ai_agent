"""
Unit tests for the web search module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from app.core.web_search import WebSearchAgent, SearchResult


class TestWebSearchAgent:
    """Test cases for WebSearchAgent class."""
    
    @pytest.fixture
    def web_search_agent(self):
        """Create a web search agent instance for testing."""
        with patch('app.core.web_search.httpx.AsyncClient'):
            agent = WebSearchAgent()
            return agent
    
    @pytest.mark.asyncio
    async def test_search_and_synthesize_success(self, web_search_agent):
        """Test successful search and synthesis."""
        # Mock search methods to return successful results
        web_search_agent._search_duckduckgo = Mock(return_value={
            "success": True,
            "results": [{"title": "Test", "content": "Test content", "url": "test.com"}],
            "sources": ["DuckDuckGo"]
        })
        web_search_agent._search_wolfram_alpha = Mock(return_value={
            "success": True,
            "results": [{"title": "Wolfram", "content": "Wolfram content", "url": "wolfram.com"}],
            "sources": ["Wolfram Alpha"]
        })
        
        result = await web_search_agent.search_and_synthesize("solve 2x + 5 = 13")
        
        assert isinstance(result, SearchResult)
        assert result.confidence > 0.1
        assert len(result.sources) > 0
        assert "Web Search Results" in result.answer
    
    @pytest.mark.asyncio
    async def test_search_and_synthesize_no_results(self, web_search_agent):
        """Test search when no results are found."""
        # Mock search methods to return no results
        web_search_agent._search_duckduckgo = Mock(return_value={"success": False})
        web_search_agent._search_wolfram_alpha = Mock(return_value={"success": False})
        
        result = await web_search_agent.search_and_synthesize("test query")
        
        assert isinstance(result, SearchResult)
        assert result.confidence == 0.1
        assert "No relevant information found" in result.answer
    
    def test_enhance_math_query(self, web_search_agent):
        """Test math query enhancement."""
        # Query without math keywords
        enhanced = web_search_agent._enhance_math_query("solve problem", "algebra")
        assert "algebra" in enhanced
        assert "solve problem" in enhanced
        
        # Query with existing math keywords
        enhanced = web_search_agent._enhance_math_query("calculate derivative")
        assert "calculate derivative" in enhanced
    
    def test_generate_math_search_results(self, web_search_agent):
        """Test generation of math-specific search results."""
        # Test equation solving
        results = web_search_agent._generate_math_search_results("solve 2x + 5 = 13")
        assert len(results) > 0
        assert any("equation" in result["title"].lower() for result in results)
        
        # Test derivative
        results = web_search_agent._generate_math_search_results("derivative of x^2")
        assert len(results) > 0
        assert any("derivative" in result["title"].lower() for result in results)
        
        # Test integration
        results = web_search_agent._generate_math_search_results("integrate sin(x)")
        assert len(results) > 0
        assert any("integration" in result["title"].lower() for result in results)
    
    def test_generate_wolfram_results(self, web_search_agent):
        """Test generation of Wolfram Alpha style results."""
        # Test equation solving
        results = web_search_agent._generate_wolfram_results("solve x^2 = 4")
        assert len(results) > 0
        assert "Solution" in results[0]["title"]
        
        # Test derivative
        results = web_search_agent._generate_wolfram_results("derivative of x^3")
        assert len(results) > 0
        assert "Derivative" in results[0]["title"]
        
        # Test geometric calculation
        results = web_search_agent._generate_wolfram_results("area of circle radius 5")
        assert len(results) > 0
        assert "Geometric" in results[0]["title"]
    
    @pytest.mark.asyncio
    async def test_synthesize_from_search_results(self, web_search_agent):
        """Test synthesis from search results."""
        results = [
            {"title": "Math Solution", "content": "Step by step solution", "url": "example.com"},
            {"title": "Another Result", "content": "More information", "url": "test.com"}
        ]
        
        synthesis = await web_search_agent._synthesize_from_search_results(
            "test query", results, "test context"
        )
        
        assert "Web Search Results" in synthesis
        assert "test query" in synthesis
        assert "test context" in synthesis
        assert "Step by step solution" in synthesis
    
    def test_calculate_confidence(self, web_search_agent):
        """Test confidence calculation."""
        # No results
        confidence = web_search_agent._calculate_confidence([], "")
        assert confidence == 0.1
        
        # Multiple results with substantial answer
        results = [{"content": "result1"}, {"content": "result2"}, {"content": "result3"}]
        long_answer = "This is a long and detailed mathematical answer " * 10
        confidence = web_search_agent._calculate_confidence(results, long_answer)
        assert confidence > 0.5


if __name__ == "__main__":
    pytest.main([__file__])
