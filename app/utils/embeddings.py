# Embedding Manager - with fallback to mock service
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("sentence-transformers not installed, using mock service")

from typing import List, Union

if SENTENCE_TRANSFORMERS_AVAILABLE:
    from app.config import settings


class EmbeddingManager:
    """Manager for generating embeddings using sentence transformers"""

    def __init__(self):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not available")
            
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = settings.EMBEDDING_DIMENSION

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.dimension


# Global instance - use real embeddings
if SENTENCE_TRANSFORMERS_AVAILABLE:
    try:
        embedding_manager = EmbeddingManager()
    except Exception as e:
        print(f"Embedding initialization failed: {e}")
        raise
else:
    raise ImportError("sentence-transformers is required but not installed. Run: pip install sentence-transformers")
