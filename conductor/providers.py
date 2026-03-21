"""
Providers - LLM provider integrations
"""

from typing import AsyncIterator
from abc import ABC, abstractmethod

from conductor.types import Message, Response, Chunk, ToolCall, Usage
from conductor.tool import Tool


class Provider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> Response:
        """Generate a completion."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> AsyncIterator[Chunk]:
        """Stream a completion."""
        pass


class OpenAIProvider(Provider):
    """OpenAI API provider."""
    
    def __init__(self):
        import openai
        self.client = openai.AsyncOpenAI()
    
    async def complete(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> Response:
        formatted_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        tool_schemas = None
        if tools:
            tool_schemas = [t.to_openai_format() for t in tools]
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            tools=tool_schemas,
            **kwargs
        )
        
        choice = response.choices[0]
        
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                import json
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))
        
        usage = None
        if response.usage:
            usage = Usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )
        
        return Response(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            usage=usage,
            model=model,
            finish_reason=choice.finish_reason,
        )
    
    async def stream(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> AsyncIterator[Chunk]:
        formatted_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            stream=True,
            **kwargs
        )
        
        full_content = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta
            content = delta.content or ""
            full_content += content
            
            yield Chunk(
                content=full_content,
                delta=content,
                done=chunk.choices[0].finish_reason is not None,
            )


class AnthropicProvider(Provider):
    """Anthropic API provider."""
    
    def __init__(self):
        import anthropic
        self.client = anthropic.AsyncAnthropic()
    
    async def complete(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> Response:
        # Extract system message
        system = ""
        user_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                user_messages.append({"role": m.role, "content": m.content})
        
        tool_schemas = None
        if tools:
            tool_schemas = [t.to_anthropic_format() for t in tools]
        
        response = await self.client.messages.create(
            model=model,
            system=system,
            messages=user_messages,
            tools=tool_schemas,
            max_tokens=kwargs.get("max_tokens", 4096),
            **{k: v for k, v in kwargs.items() if k != "max_tokens"}
        )
        
        content = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))
        
        usage = Usage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        )
        
        return Response(
            content=content,
            tool_calls=tool_calls,
            usage=usage,
            model=model,
            finish_reason=response.stop_reason,
        )
    
    async def stream(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> AsyncIterator[Chunk]:
        system = ""
        user_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                user_messages.append({"role": m.role, "content": m.content})
        
        async with self.client.messages.stream(
            model=model,
            system=system,
            messages=user_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
        ) as stream:
            full_content = ""
            async for text in stream.text_stream:
                full_content += text
                yield Chunk(
                    content=full_content,
                    delta=text,
                    done=False,
                )
            
            yield Chunk(content=full_content, delta="", done=True)


def get_provider(model: str) -> Provider:
    """Get the appropriate provider for a model."""
    if model.startswith("gpt") or model.startswith("o1"):
        return OpenAIProvider()
    elif model.startswith("claude"):
        return AnthropicProvider()
    else:
        # Default to OpenAI-compatible
        return OpenAIProvider()
