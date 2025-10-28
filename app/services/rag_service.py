from typing import List, Dict, Any, Optional, Tuple

from app.utils.embeddings import embedding_manager
from app.utils.qdrant_manager import qdrant_manager
from app.utils.redis_memory import redis_memory
from app.config import settings


class CustomRAGService:
    """
    Custom Retrieval-Augmented Generation Service
    
    This is a custom implementation without using LangChain's RetrievalQAChain
    """

    def __init__(self):
        self.top_k = settings.TOP_K_RETRIEVAL
        self.max_context_length = settings.MAX_CONTEXT_LENGTH

    async def chat(
        self,
        session_id: str,
        user_message: str
    ) -> Tuple[str, List[str]]:
        """
        Process a chat message with RAG
        
        Args:
            session_id: Unique session identifier
            user_message: User's message
            
        Returns:
            Tuple of (response, list of source document IDs)
        """
        # 1. Store user message in Redis
        redis_memory.add_message(session_id, "user", user_message)

        # 2. Retrieve relevant context from Qdrant
        relevant_chunks = await self._retrieve_context(user_message)

        # 3. Get conversation history from Redis
        conversation_history = redis_memory.get_conversation_history(
            session_id,
            max_messages=10  # Keep last 10 messages for context
        )

        # 4. Build prompt with context and history
        prompt = self._build_prompt(
            user_message=user_message,
            relevant_chunks=relevant_chunks,
            conversation_history=conversation_history
        )

        # 5. Generate response
        response = await self._generate_response(prompt)

        # 6. Store assistant response in Redis
        redis_memory.add_message(session_id, "assistant", response)

        # 7. Extract source document IDs
        sources = list(set([chunk["document_id"] for chunk in relevant_chunks]))

        return response, sources

    async def _retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from Qdrant
        
        Args:
            query: User's query
            
        Returns:
            List of relevant chunks with metadata
        """
        # Generate embedding for the query
        query_embedding = embedding_manager.embed_text(query)

        # Search in Qdrant
        results = qdrant_manager.search_similar(
            query_embedding=query_embedding,
            top_k=self.top_k
        )

        return results

    def _build_prompt(
        self,
        user_message: str,
        relevant_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Build the prompt for the language model
        
        Args:
            user_message: Current user message
            relevant_chunks: Retrieved relevant chunks
            conversation_history: Previous conversation messages
            
        Returns:
            Formatted prompt string
        """
        # Build context from retrieved chunks
        context_parts = []
        for idx, chunk in enumerate(relevant_chunks, 1):
            text = chunk.get("text", "")
            context_parts.append(f"[Context {idx}]: {text}")
        
        context_str = "\n\n".join(context_parts)
        
        # Trim context if too long
        if len(context_str) > self.max_context_length:
            context_str = context_str[:self.max_context_length] + "..."

        # Build conversation history
        history_str = ""
        if len(conversation_history) > 1:  # Exclude current message
            history_parts = []
            for msg in conversation_history[:-1]:  # Exclude the last (current) message
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_parts.append(f"{role.capitalize()}: {content}")
            history_str = "\n".join(history_parts)

        # Build the complete prompt
        prompt = f"""You are a helpful AI assistant. Use the following context and conversation history to answer the user's question.

Context from documents:
{context_str}

Conversation History:
{history_str}

Current Question: {user_message}

Instructions:
- Answer based on the provided context
- If the context doesn't contain relevant information, say so
- Be conversational and helpful
- Reference the context when applicable
- Keep track of the conversation flow

Answer:"""

        return prompt

    async def _generate_response(self, prompt: str) -> str:
        """
        Generate response based on retrieved context
        
        Args:
            prompt: The formatted prompt with context
            
        Returns:
            Generated response based on context
        """
        # Extract the context and question from the prompt
        lines = prompt.split('\n')
        
        # Find the context section
        context_start = False
        context_parts = []
        question = ""
        
        for line in lines:
            if line.startswith('[Context'):
                context_start = True
            elif line.startswith('Current Question:'):
                question = line.replace('Current Question:', '').strip()
                context_start = False
            elif context_start and line.strip():
                context_parts.append(line.strip())
        
        # If we have context, return it as the answer
        if context_parts:
            # Combine all context parts
            full_context = ' '.join(context_parts)
            
            # Create a natural response
            response = f"Based on the documents, here's what I found:\n\n{full_context[:1000]}"
            
            if len(full_context) > 1000:
                response += "...\n\n(There's more information available in the documents)"
            
            return response
        else:
            return (
                "I couldn't find relevant information in the uploaded documents to answer your question. "
                "Please make sure you've uploaded documents related to your query, or try rephrasing your question."
            )

    def clear_session(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        return redis_memory.clear_session(session_id)

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        return redis_memory.get_conversation_history(session_id)


# Global instance
rag_service = CustomRAGService()
