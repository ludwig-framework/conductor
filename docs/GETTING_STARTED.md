# Getting Started

This guide will help you build your first AI agent with Conductor.

## Prerequisites

- Python 3.10+
- An OpenAI or Anthropic API key

## Installation

```bash
pip install conductor-agents
```

## Your First Agent

Create a file called `agent.py`:

```python
import asyncio
from conductor import Agent

# Create an agent
agent = Agent(
    name="assistant",
    model="gpt-4o",
    instructions="You are a helpful assistant."
)

# Run the agent
async def main():
    response = await agent.run("What is the capital of France?")
    print(response.content)

asyncio.run(main())
```

Set your API key and run:

```bash
export OPENAI_API_KEY=sk-...
python agent.py
```

## Adding Tools

Tools let agents interact with the world:

```python
from conductor import Agent, tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your API call here
    return f"Sunny, 72°F in {city}"

agent = Agent(
    name="weather-bot",
    model="gpt-4o",
    instructions="Help users check the weather.",
    tools=[get_weather]
)

async def main():
    response = await agent.run("What's the weather in Paris?")
    print(response.content)
```

## Streaming Responses

For real-time output:

```python
async def main():
    async for chunk in agent.stream("Tell me a story"):
        print(chunk.delta, end="", flush=True)
    print()
```

## Memory

To maintain conversation state:

```python
from conductor import Agent, Memory

memory = Memory(backend="sqlite")
agent = Agent(
    name="assistant",
    model="gpt-4o",
    memory=memory
)

# Memory persists across runs
await agent.run("My name is Alice")
await agent.run("What's my name?")  # "Your name is Alice"
```

## Next Steps

- [Concepts](CONCEPTS.md) - Core abstractions
- [Tools](TOOLS.md) - Connecting to external systems
- [Workflows](WORKFLOWS.md) - Multi-agent orchestration
- [Swarms](SWARMS.md) - Agent collaboration
