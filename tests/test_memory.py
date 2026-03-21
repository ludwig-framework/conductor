"""
Tests for Memory functionality
"""

import pytest
from conductor import Memory
from conductor.types import Message


class TestMemory:
    """Tests for the Memory class."""
    
    def test_memory_creation_default(self):
        """Test default memory creation."""
        memory = Memory()
        
        assert memory.backend == "memory"
        assert memory.session_id is None
    
    def test_memory_creation_with_session(self):
        """Test memory creation with session."""
        memory = Memory(session_id="user-123", ttl=3600)
        
        assert memory.session_id == "user-123"
        assert memory.ttl == 3600
    
    @pytest.mark.asyncio
    async def test_memory_set_get(self):
        """Test setting and getting values."""
        memory = Memory()
        
        await memory.set("key1", "value1")
        result = await memory.get("key1")
        
        assert result == "value1"
    
    @pytest.mark.asyncio
    async def test_memory_delete(self):
        """Test deleting values."""
        memory = Memory()
        
        await memory.set("key1", "value1")
        await memory.delete("key1")
        result = await memory.get("key1")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_memory_clear(self):
        """Test clearing all values."""
        memory = Memory()
        
        await memory.set("key1", "value1")
        await memory.set("key2", "value2")
        await memory.clear()
        
        assert await memory.get("key1") is None
        assert await memory.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_memory_history(self):
        """Test conversation history."""
        memory = Memory()
        
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi there!")
        
        await memory.append(msg1)
        await memory.append(msg2)
        
        history = await memory.history()
        
        assert len(history) == 2
        assert history[0].content == "Hello"
        assert history[1].content == "Hi there!"
    
    def test_memory_key_namespacing(self):
        """Test key namespacing with session_id."""
        memory = Memory(session_id="user-123")
        
        key = memory._key("test-key")
        
        assert key == "user-123:test-key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
