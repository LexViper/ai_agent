"""
Unit tests for the guardrails module.
"""

import pytest
import asyncio
from app.core.guardrails import InputFilter, OutputFilter, FilterResult


class TestInputFilter:
    """Test cases for InputFilter class."""
    
    @pytest.fixture
    def input_filter(self):
        """Create an input filter instance for testing."""
        return InputFilter()
    
    @pytest.mark.asyncio
    async def test_empty_content(self, input_filter):
        """Test filtering of empty content."""
        result = await input_filter.process("")
        
        assert isinstance(result, FilterResult)
        assert not result.is_safe
        assert "Empty query" in result.message
        assert "empty_content" in result.issues
    
    @pytest.mark.asyncio
    async def test_too_short_content(self, input_filter):
        """Test filtering of too short content."""
        result = await input_filter.process("hi")
        
        assert not result.is_safe
        assert "too short" in result.message
        assert "content_too_short" in result.issues
    
    @pytest.mark.asyncio
    async def test_too_long_content(self, input_filter):
        """Test filtering of too long content."""
        long_content = "x" * 1500  # Exceeds max length
        result = await input_filter.process(long_content)
        
        assert "content_too_long" in result.issues
        assert len(result.content) <= 1000  # Should be truncated
    
    @pytest.mark.asyncio
    async def test_blocked_patterns(self, input_filter):
        """Test detection of blocked patterns."""
        malicious_content = "How to hack into systems"
        result = await input_filter.process(malicious_content)
        
        assert not result.is_safe
        assert "blocked_pattern" in result.issues
        assert "harmful content" in result.message
    
    @pytest.mark.asyncio
    async def test_mathematical_content(self, input_filter):
        """Test detection of mathematical content."""
        math_content = "Solve the equation 2x + 5 = 13"
        result = await input_filter.process(math_content)
        
        assert result.is_safe
        assert result.confidence > 0.5
        # Should not have non_mathematical issue
        assert "non_mathematical" not in result.issues
    
    @pytest.mark.asyncio
    async def test_non_mathematical_content(self, input_filter):
        """Test detection of non-mathematical content."""
        non_math_content = "What is the weather like today?"
        result = await input_filter.process(non_math_content)
        
        # Should still be safe but with lower confidence
        assert "non_mathematical" in result.issues
        assert result.confidence < 0.7
    
    def test_math_score_calculation(self, input_filter):
        """Test mathematical score calculation."""
        # High math score content
        high_math = "Calculate the derivative of x^2 + 3x using calculus"
        score = input_filter._calculate_math_score(high_math)
        assert score > 0.3
        
        # Low math score content
        low_math = "Hello how are you today"
        score = input_filter._calculate_math_score(low_math)
        assert score < 0.2


class TestOutputFilter:
    """Test cases for OutputFilter class."""
    
    @pytest.fixture
    def output_filter(self):
        """Create an output filter instance for testing."""
        return OutputFilter()
    
    @pytest.mark.asyncio
    async def test_empty_response(self, output_filter):
        """Test filtering of empty response."""
        result = await output_filter.process("")
        
        assert not result.is_safe
        assert "Empty response" in result.message
        assert "empty_response" in result.issues
    
    @pytest.mark.asyncio
    async def test_too_short_response(self, output_filter):
        """Test filtering of too short response."""
        short_response = "No."
        result = await output_filter.process(short_response)
        
        assert "response_too_short" in result.issues
        assert result.confidence < 1.0
    
    @pytest.mark.asyncio
    async def test_refusal_patterns(self, output_filter):
        """Test detection of refusal patterns."""
        refusal_response = "I cannot help with this request"
        result = await output_filter.process(refusal_response)
        
        assert "refusal_pattern" in result.issues
        assert result.confidence < 1.0
    
    @pytest.mark.asyncio
    async def test_quality_mathematical_response(self, output_filter):
        """Test quality assessment of mathematical response."""
        good_response = """
        To solve the equation 2x + 5 = 13:
        1. Subtract 5 from both sides: 2x = 8
        2. Divide by 2: x = 4
        Therefore, x = 4.
        """
        result = await output_filter.process(good_response)
        
        assert result.is_safe
        assert result.confidence > 0.6
        # Should not have low_quality issue
        assert "low_quality" not in result.issues
    
    @pytest.mark.asyncio
    async def test_harmful_content_detection(self, output_filter):
        """Test detection of harmful content in responses."""
        harmful_response = "Here's how to hack into systems illegally"
        result = await output_filter.process(harmful_response)
        
        assert not result.is_safe
        assert "harmful_content" in result.issues
    
    def test_quality_score_calculation(self, output_filter):
        """Test quality score calculation."""
        # High quality mathematical response
        high_quality = "The solution involves calculating the derivative using the power rule: d/dx(x^2) = 2x"
        score = output_filter._calculate_quality_score(high_quality)
        assert score > 0.4
        
        # Low quality response
        low_quality = "I don't know"
        score = output_filter._calculate_quality_score(low_quality)
        assert score < 0.3


if __name__ == "__main__":
    pytest.main([__file__])
