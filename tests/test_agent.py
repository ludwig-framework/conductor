"""
Tests for Agent functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from conductor import Agent, tool
from conductor.types import Message, Response, Usage


class TestAgent:
    """Tests for the Agent class."""
    
    def test_agent_creation(self):
        """Test basic agent creation."""
        agent = Agent(
            name="test-agent",
            model="gpt-4o",
            instructions="Test instructions"
        )
        
        assert agent.name == "test-agent"
        assert agent.model == "gpt-4o"
        assert agent.instructions == "Test instructions"
        assert agent.tools == []
    
    def test_agent_with_tools(self):
        """Test agent creation with tools."""
        @tool
        def dummy_tool(arg: str) -> str:
            """A dummy tool."""
            return arg
        
        agent = Agent(
            name="test-agent",
            model="gpt-4o",
            tools=[dummy_tool]
        )
        
        assert len(agent.tools) == 1
        assert agent.tools[0].name == "dummy_tool"
    
    @pytest.mark.asyncio
    async def test_agent_run(self):
        """Test agent run method."""
        agent = Agent(
            name="test-agent",
            model="gpt-4o"
        )
        
        mock_response = Response(
            content="Hello!",
            tool_calls=[],
            usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            finish_reason="stop"
        )
        
        with patch.object(agent, '_provider') as mock_provider:
            mock_provider.complete = AsyncMock(return_value=mock_response)
            
            response = await agent.run("Hi")
            
            assert response.content == "Hello!"
            assert response.usage.total_tokens == 15


class TestTool:
    """Tests for the tool decorator."""
    
    def test_tool_decorator(self):
        """Test basic tool decoration."""
        @tool
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together."""
            return a + b
        
        assert add_numbers.name == "add_numbers"
        assert add_numbers.description == "Add two numbers together."
        assert "a" in add_numbers.schema["properties"]
        assert "b" in add_numbers.schema["properties"]
    
    def test_tool_openai_format(self):
        """Test OpenAI format conversion."""
        @tool
        def search(query: str) -> str:
            """Search for information."""
            return query
        
        openai_format = search.to_openai_format()
        
        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "search"
    
    def test_tool_anthropic_format(self):
        """Test Anthropic format conversion."""
        @tool
        def search(query: str) -> str:
            """Search for information."""
            return query
        
        anthropic_format = search.to_anthropic_format()
        
        assert anthropic_format["name"] == "search"
        assert "input_schema" in anthropic_format


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
