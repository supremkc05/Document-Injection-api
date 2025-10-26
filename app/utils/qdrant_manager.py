# Qdrant Manager - with fallback to mock service
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️  qdrant-client not installed, using mock service")

from typing import List, Dict, Any, Optional
import uuid

if QDRANT_AVAILABLE:
    from app.config import settings


class QdrantManager:
    """Manager for Qdrant vector database operations"""

    def __init__(self):
        if not QDRANT_AVAILABLE:
            raise ImportError("qdrant-client not available")
            
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists, create if not"""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )

    def store_vectors(
        self,
        document_id: str,
        chunks: List[str],
        embeddings: List[List[float]]
    ) -> int:
        """
        Store document chunks and their embeddings in Qdrant
        
        Args:
            document_id: Unique document identifier
            chunks: List of text chunks
            embeddings: List of embedding vectors
            
        Returns:
            Number of vectors stored
        """
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "chunk_index": idx,
                        "text": chunk
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return len(points)

    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            document_id: Optional filter by document_id
            
        Returns:
            List of search results with text and metadata
        """
        query_filter = None
        if document_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter
        )

        return [
            {
                "text": hit.payload.get("text", ""),
                "document_id": hit.payload.get("document_id", ""),
                "chunk_index": hit.payload.get("chunk_index", -1),
                "score": hit.score
            }
            for hit in results
        ]

    def delete_by_document_id(self, document_id: str) -> bool:
        """Delete all vectors for a specific document"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting vectors for document {document_id}: {e}")
            return False


# Global instance - always use mock for local development
print("📦 Using Mock Qdrant (in-memory vector storage)")
from app.utils.mock_services import mock_qdrant_manager
qdrant_manager = mock_qdrant_manager

