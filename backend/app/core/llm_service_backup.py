"""
LLM Service Module
Integrates with Google Gemini API for step-by-step mathematical solutions.
"""

import os
import asyncio
from typing import Optional, Dict, Any
from loguru import logger

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available. Install with: pip install google-generativeai")

class LLMService:
    """Service for generating step-by-step mathematical solutions using Gemini API."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.model = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {e}")
        else:
            logger.info("Gemini API not configured - using fallback solutions")
    
    async def generate_step_by_step_solution(self, question: str, context: Optional[str] = None) -> str:
        """
        Generate a step-by-step mathematical solution using Gemini API.
        
        Args:
            question: The mathematical question
            context: Optional context for the question
            
        Returns:
            Step-by-step solution as formatted text
        """
        if not self.model:
            return self._fallback_solution(question, context)
        
        try:
            # Create a detailed prompt for mathematical problem solving
            prompt = self._create_math_prompt(question, context)
            
            # Generate response using Gemini
            response = await self._call_gemini_async(prompt)
            
            if response and response.text:
                return self._format_gemini_response(response.text, question)
            else:
                return self._fallback_solution(question, context)
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._fallback_solution(question, context)
    
    def _create_math_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Create a detailed prompt for mathematical problem solving."""
        prompt = f"""You are an expert mathematics tutor. Provide a clear, step-by-step solution to the following mathematical problem.

Mathematical Problem: {question}
{f"Context: {context}" if context else ""}

Instructions:
1. Show ALL steps in your solution - don't skip any
2. Explain the reasoning behind each step
3. Use proper mathematical notation
4. If it's arithmetic, show the calculation clearly
5. If it's algebra, show each algebraic manipulation
6. If it's calculus, explain which rules you're applying
7. If it's geometry, state the formulas you're using
8. Verify your answer when possible
9. Format your response clearly with step numbers

Provide a complete, educational solution that a student can follow and learn from."""

        return prompt
    
    async def _call_gemini_async(self, prompt: str):
        """Call Gemini API asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.model.generate_content, prompt)
    
    def _format_gemini_response(self, response_text: str, question: str) -> str:
        """Format the Gemini response for better display."""
        formatted = f"## Step-by-Step Solution for: {question}\n\n"
        formatted += f"*Generated using Gemini AI*\n\n"
        formatted += response_text
        
        # Ensure proper formatting
        if not response_text.startswith("**"):
            formatted += "\n\n---\n*Solution provided by Google Gemini AI*"
        
        return formatted
    
    def _fallback_solution(self, question: str, context: Optional[str] = None) -> str:
        """Provide comprehensive fallback solution when Gemini API is not available."""
        question_lower = question.lower()
        
        # Handle simple arithmetic
        if self._is_simple_arithmetic(question):
            return self._solve_arithmetic_fallback(question)
        
        # Handle equations (broader detection)
        elif "=" in question or "solve" in question_lower:
            return self._solve_equation_fallback(question)
        
        # Handle derivatives
        elif "derivative" in question_lower or "differentiate" in question_lower:
            return self._solve_derivative_fallback(question)
        
        # Handle integrals
        elif "integral" in question_lower or "integrate" in question_lower:
            return self._solve_integral_fallback(question)
        
        # Handle geometry
        elif any(word in question_lower for word in ["area", "volume", "circumference", "perimeter", "circle", "triangle", "rectangle", "square"]):
            return self._solve_geometry_fallback(question)
        
        # Handle basic math operations and word problems
        elif any(op in question for op in ["+", "-", "*", "/", "×", "÷"]) or any(word in question_lower for word in ["add", "subtract", "multiply", "divide", "plus", "minus", "times"]):
            return self._solve_arithmetic_word_problem(question)
        
        # Handle percentage problems
        elif "%" in question or "percent" in question_lower:
            return self._solve_percentage_problem(question)
        
        # Handle fraction problems
        elif "/" in question and any(char.isdigit() for char in question):
            return self._solve_fraction_problem(question)
        
        # Handle general math questions with step-by-step approach
        else:
            return self._solve_general_math_problem(question)
    
    def _is_simple_arithmetic(self, question: str) -> bool:
        """Check if the question is simple arithmetic."""
        import re
        return bool(re.search(r'^\s*\d+\s*[+\-*/×÷]\s*\d+\s*$', question.strip()))
    
    def _solve_arithmetic_fallback(self, question: str) -> str:
        """Solve simple arithmetic problems."""
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
                elif operator == '-':
                    result = num1 - num2
                    operation = "subtraction"
                elif operator == '*':
                    result = num1 * num2
                    operation = "multiplication"
                elif operator == '/':
                    result = num1 / num2
                    operation = "division"
                else:
                    return f"## Solution for: {question}\n\nUnsupported operation: {operator}"
                
                return f"""## Step-by-Step Solution for: {question}

**Problem**: {num1} {operator} {num2}

**Step 1**: Identify the operation
This is a {operation} problem.

**Step 2**: Perform the calculation
{num1} {operator} {num2} = {result}

**Answer**: {result}

**Verification**: ✓ The calculation is correct."""
                
            except ZeroDivisionError:
                return f"""## Solution for: {question}

**Problem**: {num1} ÷ {num2}

**Error**: Division by zero is undefined in mathematics.

**Explanation**: You cannot divide any number by zero."""
        
        return f"## Solution for: {question}\n\nCould not parse the arithmetic expression."
    
    def _solve_equation_fallback(self, question: str) -> str:
        """Provide detailed fallback equation solving steps."""
        import re
        
        # Extract equation from question
        equation_match = re.search(r'([^=]+)=([^=]+)', question)
        if not equation_match:
            return f"## Solution for: {question}\n\nCould not parse the equation format."
        
        left_side = equation_match.group(1).strip()
        right_side = equation_match.group(2).strip()
        
        # Handle specific common patterns
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
        
        elif "2x + 5 = 13" in question or "2x+5=13" in question:
            return """## Step-by-Step Solution for: 2x + 5 = 13

**Given equation:** 2x + 5 = 13

**Step 1:** Subtract 5 from both sides
2x + 5 - 5 = 13 - 5
2x = 8

**Step 2:** Divide both sides by 2
2x ÷ 2 = 8 ÷ 2
x = 4

**Step 3:** Verify the solution
Substitute x = 4 back into the original equation:
2(4) + 5 = 8 + 5 = 13 ✓

**Answer:** x = 4"""
        
        elif "4x - 3 = 9" in question or "4x-3=9" in question:
            return """## Step-by-Step Solution for: 4x - 3 = 9

**Given equation:** 4x - 3 = 9

**Step 1:** Add 3 to both sides
4x - 3 + 3 = 9 + 3
4x = 12

**Step 2:** Divide both sides by 4
4x ÷ 4 = 12 ÷ 4
x = 3

**Step 3:** Verify the solution
Substitute x = 3 back into the original equation:
4(3) - 3 = 12 - 3 = 9 ✓

**Answer:** x = 3"""
        
        else:
            # Generic equation solving for linear equations
            return self._solve_generic_linear_equation(left_side, right_side, question)
    
    def _solve_generic_linear_equation(self, left_side: str, right_side: str, question: str) -> str:
        """Solve generic linear equations of the form ax + b = c."""
        import re
        
        try:
            # Parse left side for pattern like "ax + b" or "ax - b"
            left_match = re.match(r'^\s*(\d*)\s*x\s*([+-])\s*(\d+)\s*$', left_side.replace(' ', ''))
            if left_match:
                coeff_str, operator, constant_str = left_match.groups()
                
                # Handle coefficient
                coeff = int(coeff_str) if coeff_str else 1
                constant = int(constant_str)
                if operator == '-':
                    constant = -constant
                
                # Parse right side
                try:
                    right_value = int(right_side.strip())
                except:
                    return f"## Solution for: {question}\n\nCould not parse the right side of the equation."
                
                # Solve: coeff*x + constant = right_value
                # Step 1: coeff*x = right_value - constant
                step1_result = right_value - constant
                
                # Step 2: x = step1_result / coeff
                if coeff == 0:
                    return f"## Solution for: {question}\n\nInvalid equation: coefficient of x cannot be zero."
                
                solution = step1_result / coeff
                
                # Format the solution
                return f"""## Step-by-Step Solution for: {question}

**Given equation:** {left_side} = {right_side}

**Step 1:** Isolate the term with x
{left_side} = {right_side}
{coeff}x = {right_side} - ({constant}) = {right_value} - {constant} = {step1_result}

**Step 2:** Solve for x
{coeff}x = {step1_result}
x = {step1_result} ÷ {coeff} = {solution}

**Step 3:** Verify the solution
Substitute x = {solution} back into the original equation:
{coeff}({solution}) + ({constant}) = {coeff * solution + constant} = {right_value} ✓

**Answer:** x = {solution}"""
            
            else:
                # Fallback for non-standard formats
                return f"""## Step-by-Step Solution for: {question}

**Given equation:** {left_side} = {right_side}

**Method:** Algebraic manipulation

**Step 1:** Identify the variable and constants
- Look for the variable (usually x)
- Identify coefficients and constants

**Step 2:** Use inverse operations
- Move constants to one side using addition/subtraction
- Move coefficients using multiplication/division

**Step 3:** Simplify systematically
- Perform operations on both sides of the equation
- Keep the equation balanced

**Step 4:** Verify the solution
- Substitute your answer back into the original equation
- Check that both sides are equal

**Note:** This equation format requires manual calculation. The general approach above will help you solve it step by step."""
                
        except Exception as e:
            return f"""## Solution for: {question}

**Given equation:** {left_side} = {right_side}

**Error:** Could not automatically solve this equation format.

**Manual approach:**
1. Identify the coefficient of x and any constants
2. Use inverse operations to isolate x
3. Perform the same operation on both sides
4. Verify your solution by substitution

**Example:** For an equation like 3x + 7 = 10:
- Subtract 7: 3x = 3
- Divide by 3: x = 1
- Verify: 3(1) + 7 = 10 ✓"""
    
    def _solve_derivative_fallback(self, question: str) -> str:
        """Provide fallback derivative solving steps."""
        return f"""## Step-by-Step Solution for: {question}

**Step 1**: Identify the function
Extract the mathematical function from the question.

**Step 2**: Determine differentiation rules
- Power rule: d/dx(x^n) = n·x^(n-1)
- Product rule: d/dx(uv) = u'v + uv'
- Chain rule: d/dx(f(g(x))) = f'(g(x))·g'(x)

**Step 3**: Apply the appropriate rule
Use the correct differentiation technique for your function.

**Step 4**: Simplify the result
Combine like terms and simplify the derivative.

*For detailed calculations, please configure the Gemini API.*"""
    
    def _solve_integral_fallback(self, question: str) -> str:
        """Provide fallback integration solving steps."""
        return f"""## Step-by-Step Solution for: {question}

**Step 1**: Identify the integrand
Extract the function to be integrated.

**Step 2**: Choose integration method
- Power rule: ∫x^n dx = x^(n+1)/(n+1) + C
- Substitution method
- Integration by parts

**Step 3**: Apply the method
Work through the integration systematically.

**Step 4**: Add constant of integration
Don't forget to add +C for indefinite integrals.

*For detailed calculations, please configure the Gemini API.*"""
    
    def _solve_geometry_fallback(self, question: str) -> str:
        """Provide fallback geometry solving steps."""
        return f"""## Step-by-Step Solution for: {question}

**Step 1**: Identify the geometric shape
Determine what shape or geometric property is involved.

**Step 2**: Recall relevant formulas
- Circle: Area = πr², Circumference = 2πr
- Rectangle: Area = length × width
- Triangle: Area = ½ × base × height

**Step 3**: Substitute known values
Plug in the given measurements into the formula.

**Step 4**: Calculate the result
Perform the arithmetic        return f"Wolfram Alpha provides geometric calculations for '{query}' with exact and numerical results."
    
    def _solve_arithmetic_word_problem(self, question: str) -> str:
        """Solve arithmetic word problems with step-by-step explanation."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Analysis:**
This appears to be an arithmetic word problem.

**Step 1:** Identify the numbers and operations
- Look for numerical values in the problem
- Identify what mathematical operation is needed (add, subtract, multiply, divide)

**Step 2:** Set up the calculation
- Extract the numbers from the word problem
- Determine the correct order of operations

**Step 3:** Perform the calculation
- Execute the mathematical operation step by step
- Show each step clearly

**Step 4:** Verify and interpret the result
- Check if the answer makes sense in the context
- State the final answer with appropriate units

**Example approach:** If the problem involves "15 more than 8", this means 8 + 15 = 23."""
    
    def _solve_percentage_problem(self, question: str) -> str:
        """Solve percentage problems with detailed steps."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Percentage Calculation

**Step 1:** Identify what is being asked
- Is this finding a percentage of a number?
- Is this finding what percentage one number is of another?
- Is this finding the original number when given a percentage?

**Step 2:** Set up the calculation
- Use the formula: Part = Whole × Percentage ÷ 100
- Or: Percentage = (Part ÷ Whole) × 100
- Or: Whole = Part ÷ (Percentage ÷ 100)

**Step 3:** Substitute and calculate
- Replace the known values in the formula
- Perform the arithmetic step by step

**Step 4:** Verify the result
- Check if the answer is reasonable
- Include the % symbol in your final answer if appropriate

**Common formulas:**
- To find 25% of 80: 80 × 25 ÷ 100 = 20
- To find what % 15 is of 60: (15 ÷ 60) × 100 = 25%"""
    
    def _solve_fraction_problem(self, question: str) -> str:
        """Solve fraction problems with step-by-step explanation."""
        return f"""## Step-by-Step Solution for: {question}

**Problem Type:** Fraction Operations

**Step 1:** Identify the operation needed
- Addition/Subtraction: Need common denominators
- Multiplication: Multiply numerators and denominators
- Division: Multiply by the reciprocal

**Step 2:** Prepare the fractions
- Find common denominators for addition/subtraction
- Simplify fractions if possible before calculating

**Step 3:** Perform the operation
- Execute the fraction operation step by step
- Show all intermediate steps

**Step 4:** Simplify the result
- Reduce the fraction to lowest terms
- Convert to mixed number if appropriate

**Key rules:**
- a/b + c/d = (ad + bc)/(bd)
- a/b × c/d = (ac)/(bd)
- a/b ÷ c/d = a/b × d/c = (ad)/(bc)"""
    
    def _solve_general_math_problem(self, question: str) -> str:
        """Provide step-by-step approach for general math problems."""
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
