"""
Types - Common type definitions
"""

from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class Message:
    """A conversation message."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    name: Optional[str] = None
    tool_calls: list = field(default_factory=list)
    tool_call_id: Optional[str] = None


@dataclass
class ToolCall:
    """A tool call from an agent."""
    id: str
    name: str
    arguments: dict


@dataclass
class Usage:
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    @property
    def cost_estimate(self) -> float:
        """Estimate cost in USD (rough estimate)."""
        # Rough pricing: $0.01 per 1K tokens (varies by model)
        return self.total_tokens * 0.00001


@dataclass
class Response:
    """Agent response."""
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: Optional[Usage] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None


@dataclass
class Chunk:
    """Streaming chunk."""
    content: str
    delta: str
    done: bool = False
