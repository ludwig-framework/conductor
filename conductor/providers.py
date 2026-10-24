"""
Providers - LLM provider integrations (Free local models by default)
"""

import os
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


class OllamaProvider(Provider):
    """Ollama local provider (free, open source)."""
    
    def __init__(self):
        try:
            import openai
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.client = openai.AsyncOpenAI(base_url=base_url, api_key="ollama")
        except Exception:
            self.client = None
    
    async def complete(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> Response:
        if not self.client:
            return Response(content="[Ollama not available. Install and run: ollama pull llama-3.2]", tool_calls=[], usage=None, model=model, finish_reason="stop")
        
        formatted_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                **kwargs
            )
            
            choice = response.choices[0]
            usage = None
            if response.usage:
                usage = Usage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )
            
            return Response(
                content=choice.message.content or "",
                tool_calls=[],
                usage=usage,
                model=model,
                finish_reason=choice.finish_reason,
            )
        except Exception as e:
            return Response(content=f"Error: {e}", tool_calls=[], usage=None, model=model, finish_reason="stop")
    
    async def stream(
        self,
        messages: list[Message],
        model: str,
        tools: list[Tool] = None,
        **kwargs
    ) -> AsyncIterator[Chunk]:
        if not self.client:
            yield Chunk(content="[Ollama not available]", delta="", done=True)
            return
        
        formatted_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
        
        try:
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
        except Exception as e:
            yield Chunk(content=f"Error: {e}", delta="", done=True)


class OpenAIProvider(Provider):
    """OpenAI API provider."""
    
    def __init__(self):
        import openai
        try:
            self.client = openai.AsyncOpenAI()
        except Exception:
            self.client = None
    
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
        try:
            self.client = anthropic.AsyncAnthropic()
        except Exception:
            self.client = None
    
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
    """Get the appropriate provider for a model (defaults to free local Ollama)."""
    # Check env for provider override
    provider_override = os.getenv("CONDUCTOR_PROVIDER") or os.getenv("LUDWIG_AI_PROVIDER")
    if provider_override == "openai":
        return OpenAIProvider()
    elif provider_override == "anthropic":
        return AnthropicProvider()
    elif provider_override == "ollama":
        return OllamaProvider()
    
    if model.startswith("gpt") or model.startswith("o1"):
        # Only use OpenAI if key is set, else fallback to Ollama
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIProvider()
        return OllamaProvider()
    elif model.startswith("claude"):
        if os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicProvider()
        return OllamaProvider()
    else:
        # Default to free local Ollama
        return OllamaProvider()
