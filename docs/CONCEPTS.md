# Core Concepts

Understanding Conductor's core abstractions.

## Agent

An Agent is an LLM with a specific purpose. It has:

- **Name**: Identifier for logging and debugging
- **Model**: The LLM to use (gpt-4o, claude-3-opus, etc.)
- **Instructions**: System prompt defining behavior
- **Tools**: Functions the agent can call
- **Memory**: State persistence across conversations

```python
agent = Agent(
    name="researcher",
    model="gpt-4o",
    instructions="You research topics thoroughly.",
    tools=[search_web, read_article],
    memory=Memory(backend="sqlite")
)
```

## Tool

A Tool is a function an agent can call. Tools are defined using the `@tool` decorator:

```python
@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))
```

The decorator extracts:
- Function name → Tool name
- Docstring → Tool description
- Type hints → Parameter schema

## Workflow

A Workflow chains multiple agents in sequence:

```python
workflow = Workflow(
    name="content-pipeline",
    steps=[
        Step(agent=researcher, task="Research {topic}"),
        Step(agent=writer, task="Write article about: {research}"),
        Step(agent=editor, task="Edit and polish: {draft}"),
    ]
)
```

Variables like `{topic}` are substituted automatically.

## Swarm

A Swarm coordinates multiple agents working together:

```python
swarm = Swarm(
    name="analysis-team",
    agents=[data_analyst, statistician, visualizer],
    strategy="consensus"  # Agents discuss and agree
)
```

Coordination strategies:
- **round-robin**: Each agent responds in turn
- **hierarchical**: One agent delegates to others
- **consensus**: Agents discuss until agreement
- **autonomous**: A coordinator selects the best agent

## Memory

Memory persists state across conversations:

```python
memory = Memory(
    backend="redis",     # memory, sqlite, redis, postgres
    session_id="user-1", # Namespace for this session
    ttl=3600             # Time-to-live in seconds
)
```

## Message

Messages flow between agents:

```python
@dataclass
class Message:
    role: str       # user, assistant, system, tool
    content: str
    tool_calls: list  # If agent wants to call tools
```

## Response

Agents return Response objects:

```python
@dataclass
class Response:
    content: str
    tool_calls: list[ToolCall]
    usage: Usage      # Token counts
    model: str
    finish_reason: str
```
