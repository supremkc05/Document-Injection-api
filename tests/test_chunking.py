import pytest
from app.utils.chunking import StrategyA, StrategyB


class TestChunkingStrategies:
    """Test chunking strategies"""

    def test_strategy_a_basic(self):
        """Test basic fixed-size chunking"""
        text = "This is a test. " * 100
        chunker = StrategyA(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 100 for chunk in chunks)

    def test_strategy_a_empty_text(self):
        """Test strategy A with empty text"""
        chunker = StrategyA(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text("")
        
        assert chunks == []

    def test_strategy_b_basic(self):
        """Test semantic chunking"""
        text = "This is sentence one. This is sentence two. This is sentence three."
        chunker = StrategyB(target_chunk_size=50)
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0

    def test_strategy_b_empty_text(self):
        """Test strategy B with empty text"""
        chunker = StrategyB(target_chunk_size=100)
        chunks = chunker.chunk_text("")
        
        assert chunks == []

    def test_strategy_b_paragraph_handling(self):
        """Test strategy B with paragraphs"""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunker = StrategyB(target_chunk_size=50)
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
