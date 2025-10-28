from typing import List, Protocol
from abc import ABC, abstractmethod
import re

from app.config import settings


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies"""

    @abstractmethod
    def chunk_text(self, text: str) -> List[str]:
        """Chunk text into smaller pieces"""
        pass


class FixedSizeChunking(ChunkingStrategy):
    """
    Fixed-size chunking with overlap
    
    Splits text into chunks of fixed size with configurable overlap.
    Ideal for consistent chunk sizes and maintaining context continuity.
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into fixed-size chunks with overlap
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Clean and normalize text
        text = self._clean_text(text)
        
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size

            # Extract chunk
            chunk = text[start:end]

            # Only add non-empty chunks
            if chunk.strip():
                chunks.append(chunk.strip())

            # Move start position with overlap
            start += self.chunk_size - self.chunk_overlap

            # Prevent infinite loop
            if self.chunk_size <= self.chunk_overlap:
                break

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class SemanticChunking(ChunkingStrategy):
    """
    Semantic chunking
    
    Splits text based on semantic boundaries (sentences/paragraphs) with sliding window.
    Tries to respect natural language boundaries for better readability and meaning preservation.
    """

    def __init__(self, target_chunk_size: int = None):
        self.target_chunk_size = target_chunk_size or settings.DEFAULT_CHUNK_SIZE
        self.min_chunk_size = self.target_chunk_size // 2
        self.max_chunk_size = self.target_chunk_size * 2

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into semantic chunks based on sentences and paragraphs
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Clean text
        text = self._clean_text(text)

        # Split into paragraphs first
        paragraphs = self._split_paragraphs(text)

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # Split paragraph into sentences
            sentences = self._split_sentences(para)

            for sentence in sentences:
                # Check if adding this sentence would exceed max size
                potential_chunk = current_chunk + " " + sentence if current_chunk else sentence

                if len(potential_chunk) > self.max_chunk_size:
                    # Save current chunk if it meets minimum size
                    if len(current_chunk) >= self.min_chunk_size:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        # Force add to avoid too small chunks
                        chunks.append(potential_chunk.strip())
                        current_chunk = ""
                elif len(potential_chunk) >= self.target_chunk_size:
                    # Chunk is at target size
                    chunks.append(potential_chunk.strip())
                    current_chunk = ""
                else:
                    # Keep accumulating
                    current_chunk = potential_chunk

        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split on double newlines or multiple spaces
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with NLTK if needed)
        # Split on . ! ? followed by space and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]


def get_chunking_strategy(
    strategy_name: str,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> ChunkingStrategy:
    """
    Factory function to get the appropriate chunking strategy
    
    Args:
        strategy_name: Name of the strategy ('fixed_size' or 'semantic')
        chunk_size: Chunk size (for fixed_size strategy)
        chunk_overlap: Chunk overlap (for fixed_size strategy)
        
    Returns:
        ChunkingStrategy instance
    """
    if strategy_name.lower() == "fixed_size":
        return FixedSizeChunking(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strategy_name.lower() == "semantic":
        return SemanticChunking(target_chunk_size=chunk_size or settings.DEFAULT_CHUNK_SIZE)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy_name}. Use 'fixed_size' or 'semantic'")
