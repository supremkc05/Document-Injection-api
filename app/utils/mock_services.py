"""
Mock utilities for local testing without external services
"""

class MockQdrantManager:
    """Mock Qdrant manager for local testing"""
    
    def __init__(self):
        self.vectors = {}
        self.collection_name = "documents"
    
    def store_vectors(self, document_id: str, chunks: list, embeddings: list) -> int:
        """Mock storing vectors"""
        if document_id not in self.vectors:
            self.vectors[document_id] = []
        
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.vectors[document_id].append({
                "chunk_index": idx,
                "text": chunk,
                "embedding": embedding[:5] if embedding else []  # Store only first 5 dims for mock
            })
        
        return len(chunks)
    
    def search_similar(self, query_embedding: list, top_k: int = 5, document_id: str = None) -> list:
        """Mock similarity search"""
        results = []
        for doc_id, chunks in self.vectors.items():
            if document_id and doc_id != document_id:
                continue
            for chunk in chunks[:top_k]:
                results.append({
                    "text": chunk["text"],
                    "document_id": doc_id,
                    "chunk_index": chunk["chunk_index"],
                    "score": 0.85  # Mock similarity score
                })
        return results[:top_k]
    
    def delete_by_document_id(self, document_id: str) -> bool:
        """Mock delete vectors"""
        if document_id in self.vectors:
            del self.vectors[document_id]
            return True
        return False


class MockRedisMemory:
    """Mock Redis memory for local testing"""
    
    def __init__(self):
        self.sessions = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })
    
    def get_conversation_history(self, session_id: str, max_messages: int = None) -> list:
        """Get conversation history"""
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]
        if max_messages:
            return history[-max_messages:]
        return history
    
    def clear_session(self, session_id: str) -> bool:
        """Clear session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self.sessions
    
    def get_message_count(self, session_id: str) -> int:
        """Get message count"""
        return len(self.sessions.get(session_id, []))
    
    def format_history_for_prompt(self, session_id: str, max_messages: int = 10) -> str:
        """Format history for prompt"""
        history = self.get_conversation_history(session_id, max_messages)
        
        if not history:
            return ""
        
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)


class MockEmbeddingManager:
    """Mock embedding manager for local testing"""
    
    def __init__(self):
        self.dimension = 384
    
    def embed_text(self, text: str) -> list:
        """Generate mock embedding"""
        # Simple mock: use hash of text to generate consistent embedding
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        
        # Generate pseudo-random embedding based on hash
        embedding = []
        for i in range(self.dimension):
            val = ((hash_val + i) % 1000) / 1000.0
            embedding.append(val)
        
        return embedding
    
    def embed_batch(self, texts: list) -> list:
        """Generate mock embeddings for batch"""
        return [self.embed_text(text) for text in texts]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension


# Global mock instances
mock_qdrant_manager = MockQdrantManager()
mock_redis_memory = MockRedisMemory()
mock_embedding_manager = MockEmbeddingManager()
