# Redis Memory Manager - with fallback to in-memory storage
import json
from typing import List, Dict, Any, Optional
from collections import defaultdict

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

if REDIS_AVAILABLE:
    from app.config import settings


class InMemoryStore:
    """Simple in-memory storage as fallback for Redis"""
    
    def __init__(self):
        self.data: Dict[str, List[str]] = defaultdict(list)
    
    def rpush(self, key: str, value: str) -> None:
        self.data[key].append(value)
    
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        items = self.data.get(key, [])
        if end == -1:
            return items[start:]
        return items[start:end+1]
    
    def delete(self, key: str) -> int:
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    def exists(self, key: str) -> int:
        return 1 if key in self.data else 0
    
    def llen(self, key: str) -> int:
        return len(self.data.get(key, []))
    
    def expire(self, key: str, seconds: int) -> None:
        pass  # No-op for in-memory


class RedisMemoryManager:
    """Manager for Redis-based conversation memory"""

    def __init__(self):
        if REDIS_AVAILABLE:
            try:
                self.client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                # Test connection
                self.client.ping()
                self.using_redis = True
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory storage.")
                self.client = InMemoryStore()
                self.using_redis = False
        else:
            print("Redis not installed. Using in-memory storage for conversation history.")
            self.client = InMemoryStore()
            self.using_redis = False
            
        self.default_ttl = 86400  # 24 hours in seconds

    def _get_session_key(self, session_id: str) -> str:
        """Get the Redis key for a session"""
        return f"chat_session:{session_id}"

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add a message to the conversation history
        
        Args:
            session_id: Unique session identifier
            role: Message role (user, assistant, system)
            content: Message content
        """
        key = self._get_session_key(session_id)
        message = {
            "role": role,
            "content": content
        }
        
        # Store as JSON in a list
        self.client.rpush(key, json.dumps(message))
        
        # Set expiration
        self.client.expire(key, self.default_ttl)

    def get_conversation_history(
        self,
        session_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Unique session identifier
            max_messages: Maximum number of messages to retrieve (most recent)
            
        Returns:
            List of messages in chronological order
        """
        key = self._get_session_key(session_id)
        
        if max_messages:
            # Get last N messages
            messages = self.client.lrange(key, -max_messages, -1)
        else:
            # Get all messages
            messages = self.client.lrange(key, 0, -1)
        
        return [json.loads(msg) for msg in messages]

    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for a session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if successful, False otherwise
        """
        key = self._get_session_key(session_id)
        return self.client.delete(key) > 0

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        key = self._get_session_key(session_id)
        return self.client.exists(key) > 0

    def get_message_count(self, session_id: str) -> int:
        """Get the number of messages in a session"""
        key = self._get_session_key(session_id)
        return self.client.llen(key)

    def format_history_for_prompt(
        self,
        session_id: str,
        max_messages: int = 10
    ) -> str:
        """
        Format conversation history for inclusion in a prompt
        
        Args:
            session_id: Unique session identifier
            max_messages: Maximum number of messages to include
            
        Returns:
            Formatted string of conversation history
        """
        history = self.get_conversation_history(session_id, max_messages)
        
        if not history:
            return ""
        
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)


# Global instance
redis_memory = RedisMemoryManager()
