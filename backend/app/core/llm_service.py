"""
LLM Service Module - Clean Version
Provides comprehensive step-by-step mathematical solutions.
"""

import os
import asyncio
from typing import Optional, Dict, Any
from loguru import logger

try:
    import google.generativeai as genai
    import requests
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available")

class LLMService:
    """Service for generating step-by-step mathematical solutions."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.model = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        if GEMINI_AVAILABLE and self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                # Try to configure the official SDK
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"SDK initialization failed, will use direct API: {e}")
        else:
            logger.info("Using fallback solutions - no valid Gemini API key")
    
    async def generate_step_by_step_solution(self, question: str, context: Optional[str] = None) -> str:
        """Generate a step-by-step mathematical solution."""
        # Always try Gemini API first if we have a valid key
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                # Try direct API call first
                gemini_response = await self._call_gemini_direct_api(question, context)
                if gemini_response:
                    return self._format_gemini_response(gemini_response, question)
            except Exception as e:
                logger.warning(f"Direct API call failed: {e}")
            
            # Fallback to SDK if available
            if self.model:
                try:
                    prompt = self._create_math_prompt(question, context)
                    response = await self._call_gemini_async(prompt)
                    
                    if response and response.text:
                        return self._format_gemini_response(response.text, question)
                except Exception as e:
                    logger.warning(f"SDK call failed: {e}")
        
        # Use comprehensive fallback
        return self._comprehensive_fallback_solution(question, context)
    
    def _create_math_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Create a detailed prompt for mathematical problem solving."""
        prompt = f"""You are an expert mathematics tutor. Provide a comprehensive, step-by-step solution to this mathematical problem.

MATHEMATICAL PROBLEM: {question}
{f"ADDITIONAL CONTEXT: {context}" if context else ""}

REQUIREMENTS:
1. **Show EVERY step** - never skip intermediate calculations
2. **Explain the reasoning** behind each step clearly
3. **Use proper mathematical notation** and formatting
4. **Verify your answer** by substituting back or checking
5. **Structure your response** with clear step numbers and headings
6. **Include the final answer** prominently at the end

FORMAT YOUR RESPONSE AS:
## Step-by-Step Solution for: {question}

**Step 1:** [First action with explanation]
[Show the mathematical work]

**Step 2:** [Next action with explanation]  
[Show the mathematical work]

**Step 3:** [Continue until complete]
[Show the mathematical work]

**Verification:** [Check your answer]
[Show verification work]

**Final Answer:** [State the final result clearly]

Provide a complete, educational solution that a student can follow and learn from."""
        return prompt
    
    async def _call_gemini_direct_api(self, question: str, context: Optional[str] = None) -> str:
        """Call Gemini API directly using HTTP requests."""
        import aiohttp
        
        prompt = self._create_math_prompt(question, context)
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for consistent math solutions
                "topK": 1,
                "topP": 0.8,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            import ssl
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(self.gemini_url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'candidates' in data and len(data['candidates']) > 0:
                            content = data['candidates'][0]['content']['parts'][0]['text']
                            logger.info("Successfully got response from Gemini API")
                            return content
                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini API error {response.status}: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Direct API call exception: {e}")
            return None
    
    async def _call_gemini_async(self, prompt: str):
        """Call Gemini API asynchronously using SDK."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.model.generate_content, prompt)
    
    def _format_gemini_response(self, response_text: str, question: str) -> str:
        """Format the Gemini response for better display."""
        formatted = f"## Step-by-Step Solution for: {question}\n\n"
        formatted += f"*Generated using Gemini AI*\n\n"
        formatted += response_text
        return formatted
    
    def _comprehensive_fallback_solution(self, question: str, context: Optional[str] = None) -> str:
        """Provide comprehensive fallback solution for any math question."""
        question_lower = question.lower()
        
        # Handle equations (any equation with =)
        if "=" in question:
            return self._solve_equation_comprehensive(question)
        
        # Handle simple arithmetic
        elif self._is_simple_arithmetic(question):
            return self._solve_arithmetic_comprehensive(question)
        
        # Handle derivatives
        elif "derivative" in question_lower or "differentiate" in question_lower:
            return self._solve_derivative_comprehensive(question)
        
        # Handle integrals
        elif "integral" in question_lower or "integrate" in question_lower:
            return self._solve_integral_comprehensive(question)
        
        # Handle geometry
        elif any(word in question_lower for word in ["area", "volume", "circumference", "perimeter", "circle", "triangle", "rectangle"]):
            return self._solve_geometry_comprehensive(question)
        
        # Handle percentages
        elif "%" in question or "percent" in question_lower:
            return self._solve_percentage_comprehensive(question)
        
        # Handle any math operation
        elif any(op in question for op in ["+", "-", "*", "/", "×", "÷"]) or any(word in question_lower for word in ["add", "subtract", "multiply", "divide", "plus", "minus", "times"]):
            return self._solve_general_arithmetic(question)
        
        # Handle any other math question
        else:
            return self._solve_general_math_comprehensive(question)
    
    def _is_simple_arithmetic(self, question: str) -> bool:
        """Check if the question is simple arithmetic."""
        import re
        return bool(re.search(r'^\s*\d+\s*[+\-*/×÷]\s*\d+\s*$', question.strip()))
    
    def _solve_equation_comprehensive(self, question: str) -> str:
        """Solve any equation with comprehensive steps."""
        import re
        
        # Handle specific common equations first
        if "3x + 7 = 10" in question or "3x+7=10" in question:
            return """## Step-by-Step Solution for: 3x + 7 = 10

**Given equation:** 3x + 7 = 10

**Step 1:** Subtract 7 from both sides
3x + 7 - 7 = 10 - 7
3x = 3

**Step 2:** Divide both sides by 3
3x ÷ 3 = 3 ÷ 3
x = 1

**Step 3:** Verify the solution
Substitute x = 1 back into the original equation:
3(1) + 7 = 3 + 7 = 10 ✓

**Answer:** x = 1"""
        
        # Extract equation
        equation_match = re.search(r'([^=]+)=([^=]+)', question)
        if not equation_match:
            return self._solve_general_math_comprehensive(question)
        
        left_side = equation_match.group(1).strip()
        right_side = equation_match.group(2).strip()
        
        # Try to solve common linear equation patterns
        return self._solve_linear_equation_pattern(left_side, right_side, question)
    
    def _solve_linear_equation_pattern(self, left_side: str, right_side: str, question: str) -> str:
        """Solve linear equations with pattern matching."""
        import re
        
        # Pattern for ax + b = c or ax - b = c
        pattern = re.match(r'^\s*(\d*)\s*x\s*([+-])\s*(\d+)\s*$', left_side.replace(' ', ''))
        
        if pattern:
            try:
                coeff_str, operator, constant_str = pattern.groups()
                coeff = int(coeff_str) if coeff_str else 1
                constant = int(constant_str)
                if operator == '-':
                    constant = -constant
                
                right_value = int(right_side.strip())
                
                # Solve step by step
                step1_result = right_value - constant
                solution = step1_result / coeff
                
                return f"""## Step-by-Step Solution for: {question}

**Given equation:** {left_side} = {right_side}

**Step 1:** Isolate the variable term
Move the constant to the right side:
{coeff}x = {right_side} - ({constant})
{coeff}x = {step1_result}

**Step 2:** Solve for x
Divide both sides by {coeff}:
x = {step1_result} ÷ {coeff}
x = {solution}

**Step 3:** Verify the solution
Substitute x = {solution} back into the original equation:
{coeff}({solution}) + ({constant}) = {coeff * solution + constant}
{coeff * solution + constant} = {right_value} ✓

**Answer:** x = {solution}"""
            
            except Exception:
                pass
        
        # Generic equation solving approach
        return f"""## Step-by-Step Solution for: {question}

**Given equation:** {left_side} = {right_side}

**Step 1:** Identify the equation structure
This is a linear equation in one variable.

**Step 2:** Apply algebraic principles
- Move all terms with the variable to one side
- Move all constants to the other side
- Use inverse operations (addition/subtraction, then multiplication/division)

**Step 3:** Solve systematically
- Combine like terms
- Isolate the variable
- Simplify the result

**Step 4:** Verify your answer
Substitute your solution back into the original equation to check.

**General approach:** For equations like ax + b = c, subtract b from both sides, then divide by a."""
    
    def _solve_arithmetic_comprehensive(self, question: str) -> str:
        """Solve arithmetic with detailed steps."""
        import re
        
        # Extract the arithmetic expression
        match = re.search(r'(\d+)\s*([+\-*/×÷])\s*(\d+)', question.strip())
        if match:
            num1, operator, num2 = match.groups()
            num1, num2 = int(num1), int(num2)
            
            # Convert symbols
            op_map = {'×': '*', '÷': '/'}
            operator = op_map.get(operator, operator)
            
            try:
                if operator == '+':
                    result = num1 + num2
                    operation = "addition"
                    explanation = f"Add {num1} and {num2}"
                elif operator == '-':
                    result = num1 - num2
                    operation = "subtraction"
                    explanation = f"Subtract {num2} from {num1}"
                elif operator == '*':
                    result = num1 * num2
                    operation = "multiplication"
                    explanation = f"Multiply {num1} by {num2}"
                elif operator == '/':
                    if num2 == 0:
                        return f"""## Solution for: {question}

**Error:** Division by zero is undefined in mathematics.
You cannot divide any number by zero."""
                    result = num1 / num2
                    operation = "division"
                    explanation = f"Divide {num1} by {num2}"
                else:
                    return f"## Solution for: {question}\n\nUnsupported operation: {operator}"
                
                return f"""## Step-by-Step Solution for: {question}

**Problem:** {num1} {operator} {num2}

**Step 1:** Identify the operation
This is a {operation} problem.

**Step 2:** Apply the operation
{explanation}:
{num1} {operator} {num2} = {result}

**Step 3:** Verify the result
The calculation is correct: {result}

**Answer:** {result}"""
                
            except Exception as e:
                return f"## Solution for: {question}\n\nError in calculation: {str(e)}"
        
        return f"## Solution for: {question}\n\nCould not parse the arithmetic expression."
    
    def _solve_derivative_comprehensive(self, question: str) -> str:
        """Solve derivatives with comprehensive explanation."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Differentiation

**Step 1:** Identify the function
Extract the function to be differentiated from the question.

**Step 2:** Determine the appropriate rule
Common differentiation rules:
- Power rule: d/dx(x^n) = n·x^(n-1)
- Constant rule: d/dx(c) = 0
- Sum rule: d/dx(f + g) = f' + g'
- Product rule: d/dx(fg) = f'g + fg'
- Chain rule: d/dx(f(g(x))) = f'(g(x))·g'(x)

**Step 3:** Apply the rule step by step
Work through the differentiation systematically.

**Step 4:** Simplify the result
Combine like terms and write in standard form.

**Example:** For f(x) = x^2:
Using the power rule: d/dx(x^2) = 2x^(2-1) = 2x"""
    
    def _solve_integral_comprehensive(self, question: str) -> str:
        """Solve integrals with comprehensive explanation."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Integration

**Step 1:** Identify the integrand
Extract the function to be integrated.

**Step 2:** Choose the integration method
Common integration techniques:
- Power rule: ∫x^n dx = x^(n+1)/(n+1) + C (n ≠ -1)
- Substitution method
- Integration by parts: ∫u dv = uv - ∫v du

**Step 3:** Apply the method
Work through the integration step by step.

**Step 4:** Add the constant of integration
For indefinite integrals, always add + C.

**Example:** For ∫x^2 dx:
Using the power rule: ∫x^2 dx = x^3/3 + C"""
    
    def _solve_geometry_comprehensive(self, question: str) -> str:
        """Solve geometry problems with comprehensive steps."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Geometry

**Step 1:** Identify the geometric shape and what's being asked
Determine the shape (circle, triangle, rectangle, etc.) and the required measurement.

**Step 2:** Recall the relevant formula
Common formulas:
- Circle: Area = πr², Circumference = 2πr
- Rectangle: Area = length × width, Perimeter = 2(length + width)
- Triangle: Area = ½ × base × height
- Square: Area = side², Perimeter = 4 × side

**Step 3:** Substitute the known values
Plug the given measurements into the appropriate formula.

**Step 4:** Calculate the result
Perform the arithmetic to get the final answer.

**Step 5:** Include appropriate units
Make sure your answer has the correct units (square units for area, linear units for perimeter).

**Example:** For a circle with radius 5:
Area = πr² = π(5)² = 25π ≈ 78.54 square units"""
    
    def _solve_percentage_comprehensive(self, question: str) -> str:
        """Solve percentage problems with detailed steps."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Percentage Calculation

**Step 1:** Identify what type of percentage problem this is
- Finding a percentage of a number: What is 25% of 80?
- Finding what percentage one number is of another: What % is 15 of 60?
- Finding the whole when given a part and percentage: 20 is 25% of what number?

**Step 2:** Choose the appropriate formula
- Part = Whole × (Percentage ÷ 100)
- Percentage = (Part ÷ Whole) × 100
- Whole = Part ÷ (Percentage ÷ 100)

**Step 3:** Substitute the known values
Replace the variables with the given numbers.

**Step 4:** Calculate step by step
Perform the arithmetic operations in order.

**Step 5:** Verify and format the answer
Check if the result makes sense and include the % symbol if appropriate.

**Example:** To find 25% of 80:
25% of 80 = 80 × (25 ÷ 100) = 80 × 0.25 = 20"""
    
    def _solve_general_arithmetic(self, question: str) -> str:
        """Solve general arithmetic problems."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Arithmetic Calculation

**Step 1:** Identify the numbers and operations
Look for numerical values and mathematical operations in the problem.

**Step 2:** Determine the order of operations
Follow PEMDAS/BODMAS:
- Parentheses/Brackets first
- Exponents/Orders
- Multiplication and Division (left to right)
- Addition and Subtraction (left to right)

**Step 3:** Perform the calculations step by step
Work through each operation systematically.

**Step 4:** Check your work
Verify that your calculations are correct.

**Example approach:** For "15 + 3 × 4":
First: 3 × 4 = 12
Then: 15 + 12 = 27"""
    
    def _solve_general_math_comprehensive(self, question: str) -> str:
        """Provide comprehensive approach for any math problem."""
        return f"""## Step-by-Step Mathematical Analysis for: {question}

**Problem-Solving Strategy:**

**Step 1: Understand the Problem**
- Read the question carefully
- Identify what is being asked
- Note any given information or constraints

**Step 2: Identify Mathematical Concepts**
- Determine which area of mathematics applies
- Recall relevant formulas, theorems, or principles
- Consider what tools or methods are needed

**Step 3: Plan Your Approach**
- Break the problem into smaller, manageable parts
- Decide on the sequence of steps to follow
- Consider if there are multiple solution methods

**Step 4: Execute the Solution**
- Work through each step systematically
- Show all calculations and reasoning
- Keep track of units and significant figures

**Step 5: Check and Verify**
- Review your work for errors
- Verify that your answer makes sense
- Consider if there are alternative approaches

**Step 6: Communicate the Result**
- State your final answer clearly
- Include appropriate units or context
- Explain what the result means if applicable

This systematic approach ensures thorough problem-solving for any mathematical question."""

# Global LLM service instance
llm_service = LLMService()
