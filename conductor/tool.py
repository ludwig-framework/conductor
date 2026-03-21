"""
Tool - Tool decorator and registry
"""

import inspect
from typing import Any, Callable, Optional
from functools import wraps


class Tool:
    """
    Decorator to define agent tools.
    
    Tools are functions that agents can call to interact with external systems.
    
    Args:
        description: What the tool does (shown to the LLM)
        name: Tool identifier (defaults to function name)
        schema: JSON schema for parameters (auto-generated if not provided)
    
    Example:
        @Tool(description="Search the web for information")
        async def web_search(query: str) -> str:
            return results
    """
    
    def __init__(
        self,
        description: str,
        name: Optional[str] = None,
        schema: Optional[dict] = None,
    ):
        self.description = description
        self._name = name
        self._schema = schema
        self._func: Optional[Callable] = None
    
    def __call__(self, func: Callable) -> "Tool":
        self._func = func
        if self._name is None:
            self._name = func.__name__
        if self._schema is None:
            self._schema = self._generate_schema(func)
        return self
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def schema(self) -> dict:
        return self._schema
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        if self._func is None:
            raise RuntimeError("Tool function not set")
        
        if inspect.iscoroutinefunction(self._func):
            return await self._func(**kwargs)
        else:
            return self._func(**kwargs)
    
    def _generate_schema(self, func: Callable) -> dict:
        """Generate JSON schema from function signature."""
        sig = inspect.signature(func)
        hints = func.__annotations__
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            
            param_type = hints.get(param_name, str)
            json_type = self._python_type_to_json(param_type)
            
            properties[param_name] = {"type": json_type}
            
            # Add description from docstring if available
            if func.__doc__:
                # Simple docstring parsing
                pass
            
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    
    def _python_type_to_json(self, python_type) -> str:
        """Convert Python type to JSON schema type."""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_map.get(python_type, "string")
    
    def to_openai_format(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema,
            }
        }
    
    def to_anthropic_format(self) -> dict:
        """Convert to Anthropic tool use format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.schema,
        }
