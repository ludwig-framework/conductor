"""
Memory - State management for agents
"""

from typing import Any, Optional
from dataclasses import dataclass, field

from conductor.types import Message


class Memory:
    """
    State management for agents.
    
    Allows agents to maintain state across conversations.
    
    Args:
        backend: Storage backend ("memory", "redis", "sqlite", "postgres")
        session_id: Optional session identifier
        ttl: Time-to-live in seconds
        **kwargs: Backend-specific options (e.g., url for redis)
    
    Example:
        memory = Memory(backend="redis", url="redis://localhost:6379", ttl=3600)
        agent = Agent(name="assistant", model="gpt-4o", memory=memory)
    """
    
    def __init__(
        self,
        backend: str = "memory",
        session_id: Optional[str] = None,
        ttl: Optional[int] = None,
        **kwargs,
    ):
        self.backend = backend
        self.session_id = session_id
        self.ttl = ttl
        self._options = kwargs
        
        self._store: dict[str, Any] = {}
        self._history: list[Message] = []
        
        if backend == "redis":
            self._init_redis()
        elif backend == "sqlite":
            self._init_sqlite()
        elif backend == "postgres":
            self._init_postgres()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            import redis
            url = self._options.get("url", "redis://localhost:6379")
            self._redis = redis.from_url(url)
        except ImportError:
            raise ImportError("Install redis: pip install redis")
    
    def _init_sqlite(self):
        """Initialize SQLite connection."""
        import sqlite3
        path = self._options.get("path", "conductor_memory.db")
        self._conn = sqlite3.connect(path)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _init_postgres(self):
        """Initialize PostgreSQL connection."""
        try:
            import psycopg2
            url = self._options.get("url")
            self._conn = psycopg2.connect(url)
        except ImportError:
            raise ImportError("Install psycopg2: pip install psycopg2-binary")
    
    async def get(self, key: str) -> Any:
        """Get a value from memory."""
        if self.backend == "memory":
            return self._store.get(key)
        elif self.backend == "redis":
            value = self._redis.get(self._key(key))
            return value.decode() if value else None
        else:
            return self._store.get(key)
    
    async def set(self, key: str, value: Any) -> None:
        """Set a value in memory."""
        if self.backend == "memory":
            self._store[key] = value
        elif self.backend == "redis":
            self._redis.set(self._key(key), str(value), ex=self.ttl)
        else:
            self._store[key] = value
    
    async def delete(self, key: str) -> None:
        """Delete a value from memory."""
        if self.backend == "memory":
            self._store.pop(key, None)
        elif self.backend == "redis":
            self._redis.delete(self._key(key))
        else:
            self._store.pop(key, None)
    
    async def clear(self) -> None:
        """Clear all values in memory."""
        if self.backend == "memory":
            self._store.clear()
            self._history.clear()
        elif self.backend == "redis":
            # Clear only keys for this session
            if self.session_id:
                for key in self._redis.scan_iter(f"{self.session_id}:*"):
                    self._redis.delete(key)
        else:
            self._store.clear()
            self._history.clear()
    
    async def append(self, message: Message) -> None:
        """Append a message to history."""
        self._history.append(message)
    
    async def history(self, limit: int = 100) -> list[Message]:
        """Get conversation history."""
        return self._history[-limit:]
    
    def _key(self, key: str) -> str:
        """Generate a namespaced key."""
        if self.session_id:
            return f"{self.session_id}:{key}"
        return key
