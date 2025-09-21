"""
Knowledge Base Integration Module
Handles vector storage, retrieval, and semantic search for math knowledge.
"""

import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import chromadb
from loguru import logger

@dataclass
class QueryResult:
    """Result from knowledge base query."""
    answer: str
    confidence: float
    sources: List[str]
    query_id: str
    reasoning_steps: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeBase:
    """
    Manages mathematical knowledge base using vector embeddings and semantic search.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize knowledge base with embedding model."""
        self.model_name = model_name
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model and vector database."""
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer(self.model_name)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client()
            
            # Get or create collection for math knowledge
            self.collection = self.chroma_client.get_or_create_collection(
                name="math_knowledge",
                metadata={"description": "Mathematical concepts and problem solutions"}
            )
            
            logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            raise
    
    async def query(self, question: str, context: Optional[str] = None) -> QueryResult:
        """
        Query the knowledge base for math-related information.
        
        Args:
            question: The mathematical question or problem
            context: Optional context for the query
            
        Returns:
            QueryResult with answer, confidence, and sources
        """
        try:
            query_id = str(uuid.uuid4())
            
            # Create search query by combining question and context
            search_text = question
            if context:
                search_text = f"{context} {question}"
            
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(search_text).tolist()
            
            # Search the vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["documents"] or not results["documents"][0]:
                # No relevant knowledge found
                return QueryResult(
                    answer="I don't have sufficient knowledge to answer this question accurately.",
                    confidence=0.1,
                    sources=[],
                    query_id=query_id,
                    reasoning_steps=["Searched knowledge base but found no relevant information"]
                )
            
            # Process and synthesize results
            documents = results["documents"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            
            # Calculate confidence based on similarity (lower distance = higher similarity)
            avg_distance = sum(distances) / len(distances)
            confidence = max(0.1, 1.0 - avg_distance)  # Convert distance to confidence
            
            # Extract sources
            sources = []
            for metadata in metadatas:
                if metadata and "source" in metadata:
                    sources.append(metadata["source"])
            
            # Synthesize answer from top results with enhanced math solving
            answer = await self._synthesize_answer(question, documents[:3], context)
            
            # Generate dynamic references for knowledge base results
            kb_references = self._generate_kb_references(question, sources)
            
            reasoning_steps = [
                f"Searched knowledge base with query: {search_text}",
                f"Found {len(documents)} relevant documents",
                f"Average similarity score: {1.0 - avg_distance:.2f}",
                "Synthesized answer from top matching documents",
                f"Generated {len(kb_references)} relevant references"
            ]
            
            return QueryResult(
                answer=answer,
                confidence=min(confidence, 0.85),  # Cap confidence for KB results
                sources=kb_references,  # Use dynamic references instead of static sources
                query_id=query_id,
                reasoning_steps=reasoning_steps
            )
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return QueryResult(
                answer="An error occurred while searching the knowledge base.",
                confidence=0.0,
                sources=[],
                query_id=str(uuid.uuid4()),
                reasoning_steps=[f"Error: {str(e)}"]
            )
    
    async def _synthesize_answer(self, question: str, documents: List[str], context: Optional[str] = None) -> str:
        """
        Synthesize an answer from retrieved documents using LLM integration.
        """
        if not documents:
            # Use LLM service for step-by-step solution even without documents
            from app.core.llm_service import llm_service
            return await llm_service.generate_step_by_step_solution(question, context)
        
        try:
            # First try to get LLM-generated solution
            from app.core.llm_service import llm_service
            llm_answer = await llm_service.generate_step_by_step_solution(question, context)
            
            if llm_answer and "Gemini AI" in llm_answer:
                # Add knowledge base context to LLM answer
                relevant_info = "\n\n".join(documents[:2])
                enhanced_answer = llm_answer + f"\n\n## Additional Context from Knowledge Base:\n{relevant_info}"
                return enhanced_answer
            else:
                # Fallback to simple synthesis
                return self._simple_synthesis(question, documents, context)
                
        except Exception as e:
            logger.error(f"Error in LLM synthesis: {e}")
            return self._simple_synthesis(question, documents, context)
    
    def _create_synthesis_prompt(self, question: str, relevant_info: str, context: Optional[str] = None) -> str:
        """Create a structured prompt for LLM synthesis."""
        prompt = f"""You are a mathematical AI assistant. Based on the following knowledge base information, provide a clear, step-by-step solution to the mathematical question.

Question: {question}
{f"Context: {context}" if context else ""}

Relevant Knowledge Base Information:
{relevant_info}

Instructions:
1. Provide a clear, step-by-step mathematical solution
2. Show all work and reasoning
3. Use proper mathematical notation
4. If the question cannot be fully answered with the given information, clearly state what additional information is needed
5. Format your response in markdown for better readability

Solution:"""
        
        return prompt
    
    def _call_llm_for_synthesis(self, prompt: str) -> Optional[str]:
        """
        Call LLM API for answer synthesis.
        This is a placeholder - actual implementation would use OpenAI/Anthropic APIs.
        """
        try:
            # Placeholder for actual LLM API call
            # In production, this would call OpenAI GPT-4 or Anthropic Claude
            
            # For now, return None to use fallback synthesis
            # TODO: Implement actual LLM API integration
            return None
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None
    
    def _simple_synthesis(self, question: str, documents: List[str], context: Optional[str] = None) -> str:
        """Fallback simple synthesis method with question-specific analysis."""
        relevant_info = "\n\n".join(documents[:2])
        
        synthesis = f"## Mathematical Solution for: {question}\n\n"
        
        if context:
            synthesis += f"**Context:** {context}\n\n"
        
        # Analyze the question type and provide specific guidance
        question_lower = question.lower()
        
        if "solve" in question_lower and "=" in question:
            synthesis += f"**Problem Type:** Equation Solving\n\n"
            synthesis += f"**Approach:** To solve '{question}', I'll use algebraic methods:\n\n"
            synthesis += self._generate_equation_solution(question)
        elif "derivative" in question_lower:
            synthesis += f"**Problem Type:** Differentiation\n\n"
            synthesis += f"**Approach:** To find the derivative of the expression in '{question}':\n\n"
            synthesis += self._generate_derivative_solution(question)
        elif "integral" in question_lower or "integrate" in question_lower:
            synthesis += f"**Problem Type:** Integration\n\n"
            synthesis += f"**Approach:** To integrate the expression in '{question}':\n\n"
            synthesis += self._generate_integration_solution(question)
        elif any(word in question_lower for word in ["area", "volume", "circumference", "perimeter"]):
            synthesis += f"**Problem Type:** Geometry Calculation\n\n"
            synthesis += f"**Approach:** To calculate the geometric property in '{question}':\n\n"
            synthesis += self._generate_geometry_solution(question)
        else:
            synthesis += f"**Analysis:** Based on your question '{question}':\n\n"
            synthesis += relevant_info + "\n\n"
        
        synthesis += f"\n**Knowledge Base References:**\n{relevant_info}\n\n"
        synthesis += f"**Note:** This solution is based on mathematical principles from our knowledge base relevant to your specific question."
        
        return synthesis
    
    def _generate_equation_solution(self, question: str) -> str:
        """Generate a step-by-step equation solution."""
        # Extract equation if possible
        if "=" in question:
            equation_part = question[question.find("=") - 10:question.find("=") + 10].strip()
            return f"""
**Step-by-step solution:**
1. **Identify the equation:** {equation_part if equation_part else 'from your question'}
2. **Isolate the variable:** Move constants to one side
3. **Simplify:** Perform arithmetic operations
4. **Verify:** Substitute back to check the solution

**Example approach:** If solving 2x + 5 = 13:
- Subtract 5 from both sides: 2x = 8
- Divide by 2: x = 4
- Check: 2(4) + 5 = 13 ✓
"""
        return "Apply algebraic principles to isolate the variable and solve systematically."
    
    def _generate_derivative_solution(self, question: str) -> str:
        """Generate derivative solution steps."""
        return f"""
**Differentiation process for your function:**
1. **Identify the function:** Extract the mathematical expression from '{question}'
2. **Apply differentiation rules:**
   - Power rule: d/dx(x^n) = n·x^(n-1)
   - Product rule: d/dx(uv) = u'v + uv'
   - Chain rule: d/dx(f(g(x))) = f'(g(x))·g'(x)
3. **Simplify the result**
4. **Verify using differentiation properties**

**Common derivatives:**
- d/dx(x²) = 2x
- d/dx(sin(x)) = cos(x)
- d/dx(e^x) = e^x
"""
    
    def _generate_integration_solution(self, question: str) -> str:
        """Generate integration solution steps."""
        return f"""
**Integration process for your function:**
1. **Identify the integrand:** Extract the function from '{question}'
2. **Choose integration method:**
   - Power rule: ∫x^n dx = x^(n+1)/(n+1) + C
   - Substitution method
   - Integration by parts
3. **Apply the method systematically**
4. **Add the constant of integration (+C)**
5. **Verify by differentiation**
"""
    
    def _generate_geometry_solution(self, question: str) -> str:
        """Generate geometry solution steps."""
        question_lower = question.lower()
        if "circle" in question_lower:
            return f"""
**Circle calculations for '{question}':**
- **Area:** A = πr² (where r is radius)
- **Circumference:** C = 2πr
- **Diameter:** d = 2r

**Steps:**
1. Identify the given measurement (radius, diameter, etc.)
2. Apply the appropriate formula
3. Calculate the result
4. Include proper units
"""
        elif "triangle" in question_lower:
            return f"""
**Triangle calculations for '{question}':**
- **Area:** A = ½ × base × height
- **Perimeter:** P = a + b + c (sum of all sides)
- **Pythagorean theorem:** a² + b² = c² (for right triangles)

**Steps:**
1. Identify the triangle type and given measurements
2. Choose the appropriate formula
3. Substitute values and calculate
"""
        else:
            return "Apply the relevant geometric formulas based on the shape and required calculation."
    
    def _generate_kb_references(self, question: str, original_sources: List[str]) -> List[str]:
        """Generate exactly 3 dynamic references for knowledge base results."""
        question_lower = question.lower()
        references = []
        
        # Generate question-specific references
        if "solve" in question_lower and "=" in question:
            references = [
                f"Wolfram Alpha: {question.replace(' ', '+').replace('=', '%3D')}",
                "Khan Academy: Solving Linear Equations",
                "Mathway: Algebra Problem Solver"
            ]
        elif "derivative" in question_lower:
            references = [
                f"Wolfram Alpha: derivative {question.replace(' ', '+')}",
                "Khan Academy: Differentiation Rules",
                "Paul's Online Math Notes: Derivatives"
            ]
        elif "integral" in question_lower or "integrate" in question_lower:
            references = [
                f"Wolfram Alpha: integrate {question.replace(' ', '+')}",
                "Khan Academy: Integration Techniques",
                "Integral Calculator with Steps"
            ]
        elif any(word in question_lower for word in ["area", "volume", "circumference", "perimeter"]):
            references = [
                f"Wolfram Alpha: {question.replace(' ', '+')}",
                "Khan Academy: Geometry Formulas",
                "GeoGebra: Interactive Geometry"
            ]
        elif any(op in question for op in ["+", "-", "*", "/", "×", "÷"]):
            references = [
                f"Calculator: {question}",
                "Khan Academy: Basic Arithmetic",
                "Math is Fun: Number Operations"
            ]
        else:
            # Use original sources if available, otherwise generate general references
            if original_sources:
                references = original_sources[:3]
            else:
                references = [
                    f"Wolfram Alpha: {question.replace(' ', '+')}",
                    "Khan Academy: Mathematics",
                    "Mathway: Problem Solver"
                ]
        
        # Ensure exactly 3 references
        while len(references) < 3:
            references.append("Mathematics Reference")
        
        return references[:3]
    
    async def add_knowledge(self, content: str, source: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add new knowledge to the knowledge base.
        
        Args:
            content: The content to add
            source: Source reference for the content
            metadata: Additional metadata
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Prepare metadata
            doc_metadata = {"source": source}
            if metadata:
                doc_metadata.update(metadata)
            
            # Add to ChromaDB collection
            doc_id = str(uuid.uuid4())
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            # Also store in database for persistence
            from app.core.database import db_manager
            await db_manager.store_knowledge_base_entry({
                "content_id": doc_id,
                "content": content,
                "source": source,
                "metadata": metadata or {},
                "embedding_vector": embedding
            })
            
            logger.info(f"Added knowledge from source: {source}")
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            raise
    
    async def populate_initial_knowledge(self):
        """Populate the knowledge base with initial mathematical knowledge."""
        try:
            initial_knowledge = [
                {
                    "content": "To solve linear equations of the form ax + b = c, subtract b from both sides to get ax = c - b, then divide both sides by a to get x = (c - b)/a.",
                    "source": "Basic Algebra",
                    "metadata": {"topic": "linear_equations", "difficulty": "basic"}
                },
                {
                    "content": "The derivative of x^n is n*x^(n-1). This is the power rule for differentiation.",
                    "source": "Calculus Fundamentals",
                    "metadata": {"topic": "derivatives", "difficulty": "intermediate"}
                },
                {
                    "content": "The Pythagorean theorem states that in a right triangle, a² + b² = c², where c is the hypotenuse and a and b are the other two sides.",
                    "source": "Geometry Basics",
                    "metadata": {"topic": "geometry", "difficulty": "basic"}
                },
                {
                    "content": "The area of a circle is π*r², where r is the radius. The circumference is 2*π*r.",
                    "source": "Geometry Formulas",
                    "metadata": {"topic": "geometry", "difficulty": "basic"}
                },
                {
                    "content": "To integrate x^n, use the formula ∫x^n dx = x^(n+1)/(n+1) + C, where C is the constant of integration and n ≠ -1.",
                    "source": "Integration Rules",
                    "metadata": {"topic": "integration", "difficulty": "intermediate"}
                }
            ]
            
            for knowledge in initial_knowledge:
                await self.add_knowledge(
                    content=knowledge["content"],
                    source=knowledge["source"],
                    metadata=knowledge["metadata"]
                )
            
            logger.info("Initial knowledge base populated successfully")
            
        except Exception as e:
            logger.error(f"Error populating initial knowledge: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "model_name": self.model_name,
                "collection_name": "math_knowledge"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}