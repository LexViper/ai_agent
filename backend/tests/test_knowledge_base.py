"""
Unit tests for the knowledge base module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from app.core.knowledge_base import KnowledgeBase, QueryResult


class TestKnowledgeBase:
    """Test cases for KnowledgeBase class."""
    
    @pytest.fixture
    def knowledge_base(self):
        """Create a knowledge base instance for testing."""
        with patch('app.core.knowledge_base.SentenceTransformer'), \
             patch('app.core.knowledge_base.chromadb.Client'):
            kb = KnowledgeBase()
            return kb
    
    def test_knowledge_base_initialization(self, knowledge_base):
        """Test knowledge base initialization."""
        assert knowledge_base.model_name == "all-MiniLM-L6-v2"
        assert knowledge_base.embedding_model is not None
        assert knowledge_base.chroma_client is not None
    
    @pytest.mark.asyncio
    async def test_query_with_no_results(self, knowledge_base):
        """Test query when no results are found."""
        # Mock the collection to return empty results
        knowledge_base.collection = Mock()
        knowledge_base.collection.query.return_value = {
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]]
        }
        
        result = await knowledge_base.query("test question")
        
        assert isinstance(result, QueryResult)
        assert result.confidence == 0.1
        assert "don't have sufficient knowledge" in result.answer
    
    @pytest.mark.asyncio
    async def test_query_with_results(self, knowledge_base):
        """Test query with valid results."""
        # Mock the collection to return results
        knowledge_base.collection = Mock()
        knowledge_base.collection.query.return_value = {
            "documents": [["Sample math content", "Another math result"]],
            "distances": [[0.2, 0.3]],
            "metadatas": [[{"source": "test"}, {"source": "test2"}]]
        }
        
        # Mock the embedding model
        knowledge_base.embedding_model = Mock()
        knowledge_base.embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        
        result = await knowledge_base.query("solve equation")
        
        assert isinstance(result, QueryResult)
        assert result.confidence > 0.1
        assert len(result.sources) > 0
        assert "Mathematical Solution" in result.answer
    
    @pytest.mark.asyncio
    async def test_add_knowledge(self, knowledge_base):
        """Test adding knowledge to the knowledge base."""
        # Mock dependencies
        knowledge_base.embedding_model = Mock()
        knowledge_base.embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        knowledge_base.collection = Mock()
        
        with patch('app.core.knowledge_base.db_manager') as mock_db:
            mock_db.store_knowledge_base_entry = Mock(return_value=True)
            
            await knowledge_base.add_knowledge(
                content="Test math content",
                source="Test Source",
                metadata={"topic": "algebra"}
            )
            
            # Verify collection.add was called
            knowledge_base.collection.add.assert_called_once()
            
            # Verify database storage was called
            mock_db.store_knowledge_base_entry.assert_called_once()
    
    def test_create_synthesis_prompt(self, knowledge_base):
        """Test synthesis prompt creation."""
        question = "Solve 2x + 5 = 13"
        relevant_info = "Linear equation solving methods"
        context = "Algebra homework"
        
        prompt = knowledge_base._create_synthesis_prompt(question, relevant_info, context)
        
        assert question in prompt
        assert relevant_info in prompt
        assert context in prompt
        assert "mathematical AI assistant" in prompt.lower()
    
    def test_simple_synthesis(self, knowledge_base):
        """Test simple synthesis fallback."""
        question = "What is 2+2?"
        documents = ["Addition is a basic arithmetic operation", "2+2 equals 4"]
        
        result = knowledge_base._simple_synthesis(question, documents)
        
        assert "Mathematical Solution" in result
        assert question in result
        assert documents[0] in result


if __name__ == "__main__":
    pytest.main([__file__])
