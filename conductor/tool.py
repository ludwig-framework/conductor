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
    """
    
    def __init__(
        self,
        description: str = None,
        name: Optional[str] = None,
        schema: Optional[dict] = None,
        func: Optional[Callable] = None,
    ):
        if callable(description) and func is None and name is None and schema is None:
            # Used as @Tool without args
            func = description
            description = None
        self.description = description
        self._name = name
        self._schema = schema
        self._func: Optional[Callable] = func
        
        if func is not None:
            self._bind(func)
    
    def _bind(self, func: Callable) -> None:
        self._func = func
        if self._name is None:
            self._name = func.__name__
        if self.description is None:
            # Extract description from docstring
            if func.__doc__:
                # Take first line of docstring
                self.description = func.__doc__.strip().split('\n')[0].strip()
            else:
                self.description = self._name
        if self._schema is None:
            self._schema = self._generate_schema(func)
    
    def __call__(self, func: Callable = None) -> "Tool":
        if func is not None:
            self._bind(func)
            # Copy attributes to function for compatibility
            func.name = self.name
            func.description = self.description
            func.schema = self.schema
            func.to_openai_format = self.to_openai_format
            func.to_anthropic_format = self.to_anthropic_format
            func.execute = self.execute
            func._tool = self
            return func
        return self
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    @property
    def schema(self) -> dict:
        return self._schema
    
    @schema.setter
    def schema(self, value: dict):
        self._schema = value
    
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
        hints = getattr(func, '__annotations__', {})
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            
            param_type = hints.get(param_name, str)
            json_type = self._python_type_to_json(param_type)
            
            properties[param_name] = {"type": json_type}
            
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    
    def _python_type_to_json(self, python_type) -> str:
        """Convert Python type to JSON schema type."""
        # Handle string annotations
        if isinstance(python_type, str):
            if python_type in ('str',):
                return "string"
            elif python_type in ('int',):
                return "integer"
            elif python_type in ('float',):
                return "number"
            elif python_type in ('bool',):
                return "boolean"
            elif python_type.startswith('list'):
                return "array"
            elif python_type.startswith('dict'):
                return "object"
            return "string"
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


# Decorator function
def tool(func: Callable = None, description: str = None, name: str = None, **kwargs):
    """Tool decorator."""
    if func is not None and callable(func):
        t = Tool(description=description, name=name, **kwargs)
        return t(func)
    else:
        def decorator(f):
            t = Tool(description=description or func if isinstance(func, str) else description, name=name, **kwargs)
            return t(f)
        return decorator


# Alias
ToolDecorator = Tool
