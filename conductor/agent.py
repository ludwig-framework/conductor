"""
Agent - Core agent implementation
"""

from typing import Any, AsyncIterator, Optional
from pydantic import BaseModel

from conductor.types import Message, Response, Chunk
from conductor.tool import Tool
from conductor.memory import Memory
from conductor.config import Config
from conductor.providers import get_provider


class Agent:
    """
    An AI agent that can process requests and use tools.
    
    Args:
        name: Unique identifier for the agent
        model: LLM model to use (e.g., "gpt-4o", "claude-3-5-sonnet")
        instructions: System prompt for the agent
        tools: List of tools available to the agent
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
        memory: Memory backend for state persistence
        config: Agent configuration
    """
    
    def __init__(
        self,
        name: str,
        model: str,
        instructions: str = "",
        tools: list[Tool] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        memory: Optional[Memory] = None,
        config: Optional[Config] = None,
    ):
        self.name = name
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.memory = memory
        self.config = config or Config()
        
        self._provider = get_provider(model)
        self._history: list[Message] = []
    
    async def run(
        self,
        prompt: str | list[Message],
        **kwargs
    ) -> Response:
        """
        Execute the agent with a prompt.
        
        Args:
            prompt: User message or list of messages
            **kwargs: Additional arguments passed to the provider
            
        Returns:
            Response object with content and metadata
        """
        messages = self._prepare_messages(prompt)
        
        response = await self._provider.complete(
            messages=messages,
            model=self.model,
            tools=self.tools,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        
        # Handle tool calls if present
        while response.tool_calls:
            tool_results = await self._execute_tools(response.tool_calls)
            messages.extend(tool_results)
            
            response = await self._provider.complete(
                messages=messages,
                model=self.model,
                tools=self.tools,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
        
        # Update history
        if self.memory:
            await self.memory.append(Message(role="user", content=str(prompt)))
            await self.memory.append(Message(role="assistant", content=response.content))
        
        return response
    
    async def stream(
        self,
        prompt: str | list[Message],
        **kwargs
    ) -> AsyncIterator[Chunk]:
        """
        Stream the agent response.
        
        Args:
            prompt: User message or list of messages
            **kwargs: Additional arguments
            
        Yields:
            Chunk objects with partial content
        """
        messages = self._prepare_messages(prompt)
        
        async for chunk in self._provider.stream(
            messages=messages,
            model=self.model,
            tools=self.tools,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        ):
            yield chunk
    
    def _prepare_messages(self, prompt: str | list[Message]) -> list[Message]:
        """Prepare message list with system prompt and history."""
        messages = []
        
        if self.instructions:
            messages.append(Message(role="system", content=self.instructions))
        
        if isinstance(prompt, str):
            messages.append(Message(role="user", content=prompt))
        else:
            messages.extend(prompt)
        
        return messages
    
    async def _execute_tools(self, tool_calls: list) -> list[Message]:
        """Execute tool calls and return results as messages."""
        results = []
        
        for call in tool_calls:
            tool = next((t for t in self.tools if t.name == call.name), None)
            if tool:
                result = await tool.execute(**call.arguments)
                results.append(Message(
                    role="tool",
                    content=str(result),
                    tool_call_id=call.id
                ))
        
        return results
    
    def clone(self, **overrides) -> "Agent":
        """Create a copy of this agent with optional overrides."""
        return Agent(
            name=overrides.get("name", self.name),
            model=overrides.get("model", self.model),
            instructions=overrides.get("instructions", self.instructions),
            tools=overrides.get("tools", self.tools),
            temperature=overrides.get("temperature", self.temperature),
            max_tokens=overrides.get("max_tokens", self.max_tokens),
            memory=overrides.get("memory", self.memory),
            config=overrides.get("config", self.config),
        )
