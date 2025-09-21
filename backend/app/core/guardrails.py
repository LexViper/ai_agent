"""
Guardrails Module
Implements input and output filtering for safety, content moderation, and quality control.
"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class FilterResult:
    """Result from content filtering."""
    is_safe: bool
    content: str
    message: str
    issues: List[str]
    confidence: float

class InputFilter:
    """
    Filters and validates user input for safety and appropriateness.
    Ensures queries are mathematical and don't contain harmful content.
    """
    
    def __init__(self):
        """Initialize input filter with validation rules."""
        self.blocked_patterns = [
            r'\b(hack|exploit|attack|malicious)\b',
            r'\b(personal|private|confidential)\s+information\b',
            r'\b(generate|create)\s+(virus|malware|harmful)\b',
        ]
        
        # Enhanced math detection patterns - more comprehensive
        self.math_indicators = [
            # Mathematical operations and keywords
            r'\b(solve|calculate|compute|find|derive|integrate|differentiate|evaluate|simplify|determine)\b',
            r'\b(equation|formula|function|theorem|proof|graph|plot|matrix|vector|expression)\b',
            r'\b(algebra|calculus|geometry|trigonometry|statistics|probability|arithmetic|mathematics)\b',
            
            # Mathematical symbols and operators
            r'[+\-*/=<>{}[\]()^%]',
            r'[×÷±≤≥≠≈∈∉⊂⊃∪∩∫∑∏√π∞]',  # Unicode math symbols
            
            # Numbers and arithmetic patterns
            r'\b\d+\b',  # Contains numbers
            r'\d+\s*[+\-*/^×÷%]\s*\d+',  # Arithmetic expressions
            r'^\s*\d+\s*[+\-*/×÷]\s*\d+\s*$',  # Simple arithmetic like "2+2"
            r'^\s*\d+\s*[+\-*/×÷]\s*\d+\s*[+\-*/×÷]\s*\d+',  # Multi-operation arithmetic
            
            # Mathematical functions
            r'\b(sin|cos|tan|log|ln|exp|sqrt|abs|floor|ceil|round)\b',
            r'\b(sum|integral|derivative|limit|factorial|permutation|combination)\b',
            
            # Advanced mathematical terms
            r'\b(differential|partial|equation|transform|laplace|fourier|matrix|vector|tensor)\b',
            r'\b(eigenvalue|eigenvector|determinant|inverse|transpose|orthogonal)\b',
            r'\b(topology|manifold|group|ring|field|homomorphism|isomorphism)\b',
            r'\b(convergence|divergence|series|sequence|continuity|differentiable)\b',
            
            # Geometric and algebraic terms
            r'\b(polynomial|quadratic|linear|exponential|logarithmic|rational|irrational)\b',
            r'\b(area|volume|perimeter|circumference|radius|diameter|angle|triangle|circle|square|rectangle)\b',
            r'\b(mean|median|mode|variance|standard\s+deviation|correlation|probability)\b',
            
            # Variables and equations
            r'\b[a-z]\s*[=+\-*/^]',  # Variables in equations (x=, y+, etc.)
            r'\b\d*[a-z]\s*[+\-*/^]',  # Coefficients with variables (2x+, 3y-, etc.)
            
            # Question patterns about math
            r'\b(what\s+is|how\s+much\s+is|calculate)\s+\d+',  # "What is 2+2" patterns
            r'\bmath\b|\bmathematics\b|\bmathematical\b',  # Explicit math keywords
            
            # Fractions and decimals
            r'\d+/\d+',  # Fractions like 1/2, 3/4
            r'\d+\.\d+',  # Decimals like 3.14, 2.5
            
            # Percentage calculations
            r'\d+\s*%|\bpercent\b',  # Percentages
            
            # Units that often appear in math problems
            r'\b(degrees?|radians?|meters?|feet|inches?|cm|mm|kg|grams?|seconds?|minutes?|hours?)\b'
        ]
        
        # Non-math indicators - things that clearly indicate non-mathematical content
        self.non_math_indicators = [
            r'\b(weather|temperature|climate|rain|snow|sunny|cloudy)\b',
            r'\b(cook|recipe|food|eat|drink|restaurant|kitchen)\b',
            r'\b(movie|film|actor|actress|cinema|theater)\b',
            r'\b(music|song|singer|band|album|concert)\b',
            r'\b(car|drive|traffic|road|highway|parking)\b',
            r'\b(health|doctor|medicine|hospital|sick|disease)\b',
            r'\b(politics|government|president|election|vote)\b',
            r'\b(sports|football|basketball|soccer|tennis|game)\b',
            r'\b(travel|vacation|hotel|flight|airport|tourist)\b',
            r'\b(shopping|store|buy|sell|price|money|dollar)\b',
            r'\b(work|job|career|office|business|company)\b',
            r'\b(school|teacher|student|class|homework|grade)\b',
            r'\b(family|friend|relationship|love|marriage)\b',
            r'\b(computer|software|internet|website|email)\b',
            r'\b(book|read|write|story|novel|author)\b'
        ]
        
        self.max_length = 1000  # Maximum query length
        self.min_length = 3     # Minimum query length
    
    async def process(self, content: str) -> FilterResult:
        """
        Process and filter input content.
        
        Args:
            content: The input content to filter
            
        Returns:
            FilterResult with safety assessment and filtered content
        """
        issues = []
        confidence = 1.0
        
        # Basic validation
        if not content or not content.strip():
            return FilterResult(
                is_safe=False,
                content="",
                message="Empty query is not allowed",
                issues=["empty_content"],
                confidence=1.0
            )
        
        content = content.strip()
        
        # Length validation
        if len(content) > self.max_length:
            issues.append("content_too_long")
            content = content[:self.max_length]
            confidence -= 0.1
        
        if len(content) < self.min_length:
            return FilterResult(
                is_safe=False,
                content=content,
                message="Query is too short",
                issues=["content_too_short"],
                confidence=1.0
            )
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return FilterResult(
                    is_safe=False,
                    content=content,
                    message="Query contains potentially harmful content",
                    issues=["blocked_pattern"],
                    confidence=1.0
                )
        
        # Enhanced math detection with non-math penalty
        math_score = self._calculate_enhanced_math_score(content)
        if math_score < 0.2:
            return FilterResult(
                is_safe=False,
                content=content,
                message="Please enter a valid math question. Only mathematical questions are allowed.",
                issues=["non_mathematical"],
                confidence=0.0
            )
        
        # Additional content validation
        if self._contains_excessive_special_chars(content):
            issues.append("excessive_special_chars")
            confidence -= 0.2
        
        # Clean and normalize content
        cleaned_content = self._clean_content(content)
        
        # Determine if content is safe
        is_safe = confidence > 0.5 and not any(issue in ["blocked_pattern"] for issue in issues)
        
        message = "Content passed safety checks" if is_safe else "Content failed safety checks"
        
        return FilterResult(
            is_safe=is_safe,
            content=cleaned_content,
            message=message,
            issues=issues,
            confidence=max(0.0, confidence)
        )
    
    def _calculate_enhanced_math_score(self, content: str) -> float:
        """Calculate how mathematical the content appears to be with enhanced logic."""
        import re
        
        content_lower = content.lower()
        
        # Check for explicit non-math indicators first
        non_math_matches = 0
        for pattern in self.non_math_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                non_math_matches += 1
        
        # Strong penalty for non-math content
        if non_math_matches > 0:
            return 0.0
        
        # Calculate positive math indicators
        total_indicators = len(self.math_indicators)
        math_matches = 0
        
        for pattern in self.math_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                math_matches += 1
        
        # Base score from pattern matching
        base_score = math_matches / total_indicators if total_indicators > 0 else 0
        
        # Strong boosts for obvious math patterns
        if re.search(r'^\s*\d+\s*[+\-*/×÷]\s*\d+\s*$', content.strip()):  # Pure arithmetic
            base_score += 0.5
        if re.search(r'\d+\s*[+\-*/×÷]\s*\d+', content):  # Any arithmetic
            base_score += 0.3
        if re.search(r'\b(solve|calculate|find)\b.*[=]', content_lower):  # Equation solving
            base_score += 0.4
        if re.search(r'\b[a-z]\s*[=+\-*/^]', content):  # Variables in equations
            base_score += 0.3
        if re.search(r'\b(derivative|integral|limit|sum)\b', content_lower):  # Calculus
            base_score += 0.4
        if re.search(r'\b(differential|partial).*\bequation\b', content_lower):  # Differential equations
            base_score += 0.5
        if re.search(r'\b(laplace|fourier|transform)\b', content_lower):  # Mathematical transforms
            base_score += 0.4
        if re.search(r'\b(matrix|vector|eigenvalue|determinant)\b', content_lower):  # Linear algebra
            base_score += 0.4
        if re.search(r'\b(area|volume|perimeter)\b.*\b(circle|triangle|rectangle)\b', content_lower):  # Geometry
            base_score += 0.3
        if re.search(r'\d+\s*%|\bpercent\b', content_lower):  # Percentages
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _calculate_math_score(self, content: str) -> float:
        """Calculate how mathematical the content appears to be."""
        return self._calculate_enhanced_math_score(content)
    
    def _contains_excessive_special_chars(self, content: str) -> bool:
        """Check if content contains excessive special characters."""
        special_char_count = len(re.findall(r'[^a-zA-Z0-9\s+\-*/=<>(){}[\].,?!]', content))
        return special_char_count > len(content) * 0.3
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove potentially dangerous characters but preserve math symbols
        content = re.sub(r'[^\w\s+\-*/=<>(){}[\].,?!]', '', content)
        
        return content.strip()

class OutputFilter:
    """
    Filters and validates AI-generated output for safety and quality.
    Ensures responses are appropriate and don't contain harmful information.
    """
    
    def __init__(self):
        """Initialize output filter with validation rules."""
        self.blocked_phrases = [
            "I cannot help with",
            "I'm not able to assist",
            "This request violates",
            "I can't provide information about",
        ]
        
        self.quality_indicators = [
            r'\b(solution|answer|result|calculation)\b',
            r'\b(step|method|approach|process)\b',
            r'\b(therefore|thus|hence|so)\b',
            r'[+\-*/=]',
            r'\b\d+\b',
        ]
        
        self.min_answer_length = 20
        self.max_answer_length = 2000
    
    async def process(self, content: str) -> FilterResult:
        """
        Process and filter output content.
        
        Args:
            content: The output content to filter
            
        Returns:
            FilterResult with safety assessment and filtered content
        """
        issues = []
        confidence = 1.0
        
        if not content or not content.strip():
            return FilterResult(
                is_safe=False,
                content="",
                message="Empty response is not allowed",
                issues=["empty_response"],
                confidence=1.0
            )
        
        content = content.strip()
        
        # Length validation
        if len(content) < self.min_answer_length:
            issues.append("response_too_short")
            confidence -= 0.3
        
        if len(content) > self.max_answer_length:
            issues.append("response_too_long")
            content = content[:self.max_answer_length] + "..."
            confidence -= 0.1
        
        # Check for blocked phrases (refusal patterns)
        for phrase in self.blocked_phrases:
            if phrase.lower() in content.lower():
                issues.append("refusal_pattern")
                confidence -= 0.4
        
        # Check content quality
        quality_score = self._calculate_quality_score(content)
        if quality_score < 0.3:
            issues.append("low_quality")
            confidence -= 0.3
        
        # Check for potential harmful content
        if self._contains_harmful_content(content):
            return FilterResult(
                is_safe=False,
                content=content,
                message="Response contains potentially harmful content",
                issues=["harmful_content"],
                confidence=0.0
            )
        
        # Clean content
        cleaned_content = self._clean_output(content)
        
        is_safe = confidence > 0.4
        message = "Response passed safety checks" if is_safe else "Response has quality or safety issues"
        
        return FilterResult(
            is_safe=is_safe,
            content=cleaned_content,
            message=message,
            issues=issues,
            confidence=max(0.0, confidence)
        )
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate the quality score of the response."""
        matches = 0
        total_indicators = len(self.quality_indicators)
        
        for indicator in self.quality_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                matches += 1
        
        base_score = matches / total_indicators
        
        # Bonus for structured content (contains numbered steps, bullet points, etc.)
        if re.search(r'(\d+\.|•|\*)\s+', content):
            base_score += 0.2
        
        # Bonus for mathematical expressions
        if re.search(r'[+\-*/=<>{}[\]()]', content):
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _contains_harmful_content(self, content: str) -> bool:
        """Check if content contains harmful information."""
        harmful_patterns = [
            r'\b(personal|private|confidential)\s+information\b',
            r'\b(hack|exploit|attack)\b',
            r'\b(illegal|unlawful|criminal)\b',
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _clean_output(self, content: str) -> str:
        """Clean and normalize output content."""
        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        # Ensure proper formatting
        content = content.strip()
        
        return content

class ContentModerator:
    """
    Advanced content moderation using multiple filtering strategies.
    """
    
    def __init__(self):
        """Initialize content moderator."""
        self.input_filter = InputFilter()
        self.output_filter = OutputFilter()
    
    async def moderate_input(self, content: str, context: Optional[Dict[str, Any]] = None) -> FilterResult:
        """Moderate input content with context awareness."""
        result = await self.input_filter.process(content)
        
        # Add context-aware moderation if needed
        if context:
            logger.info(f"Moderating input with context: {context}")
        
        return result
    
    async def moderate_output(self, content: str, context: Optional[Dict[str, Any]] = None) -> FilterResult:
        """Moderate output content with context awareness."""
        result = await self.output_filter.process(content)
        
        # Add context-aware moderation if needed
        if context:
            logger.info(f"Moderating output with context: {context}")
        
        return result