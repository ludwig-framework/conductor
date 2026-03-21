# Examples

## Basic Agent

```python
import asyncio
from conductor import Agent

agent = Agent(
    name="assistant",
    model="gpt-4o",
    instructions="You are a helpful assistant."
)

async def main():
    response = await agent.run("Hello!")
    print(response.content)

asyncio.run(main())
```

## Agent with Tools

```python
import asyncio
import httpx
from conductor import Agent, tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    response = httpx.get(f"https://wttr.in/{city}?format=3")
    return response.text

@tool
def calculate(expression: str) -> str:
    """Calculate a math expression."""
    return str(eval(expression))

agent = Agent(
    name="utility-bot",
    model="gpt-4o",
    instructions="Help users with weather and math.",
    tools=[get_weather, calculate]
)

async def main():
    response = await agent.run("What's the weather in Tokyo?")
    print(response.content)
    
    response = await agent.run("What's 15% of 847?")
    print(response.content)

asyncio.run(main())
```

## Streaming

```python
import asyncio
from conductor import Agent

agent = Agent(
    name="storyteller",
    model="gpt-4o",
    instructions="Tell creative stories."
)

async def main():
    print("Story: ", end="")
    async for chunk in agent.stream("Tell me a short story about a robot"):
        print(chunk.delta, end="", flush=True)
    print()

asyncio.run(main())
```

## Multi-Agent Workflow

```python
import asyncio
from conductor import Agent, Workflow, Step

researcher = Agent(
    name="researcher",
    model="gpt-4o",
    instructions="Research topics thoroughly and provide key facts."
)

writer = Agent(
    name="writer", 
    model="gpt-4o",
    instructions="Write engaging blog posts based on research."
)

editor = Agent(
    name="editor",
    model="gpt-4o",
    instructions="Edit content for clarity and grammar."
)

workflow = Workflow(
    name="blog-post-pipeline",
    steps=[
        Step(agent=researcher, task="Research: {topic}"),
        Step(agent=writer, task="Write a blog post using this research:\n{step_1}"),
        Step(agent=editor, task="Edit this draft:\n{step_2}"),
    ]
)

async def main():
    result = await workflow.run(topic="The future of AI agents")
    print(result)

asyncio.run(main())
```

## Agent Swarm

```python
import asyncio
from conductor import Agent, Swarm

analyst = Agent(
    name="data-analyst",
    model="gpt-4o",
    instructions="Analyze data and find patterns."
)

creative = Agent(
    name="creative-director",
    model="gpt-4o",
    instructions="Generate creative marketing ideas."
)

strategist = Agent(
    name="strategist",
    model="gpt-4o",
    instructions="Develop business strategies."
)

swarm = Swarm(
    name="marketing-team",
    agents=[analyst, creative, strategist],
    strategy="consensus"
)

async def main():
    result = await swarm.run(
        "How should we launch our new AI product?",
        rounds=3
    )
    print("Team consensus:", result)

asyncio.run(main())
```

## Memory Persistence

```python
import asyncio
from conductor import Agent, Memory

memory = Memory(backend="sqlite", session_id="user-123")

agent = Agent(
    name="personal-assistant",
    model="gpt-4o",
    instructions="Remember user preferences and help accordingly.",
    memory=memory
)

async def main():
    # First conversation
    await agent.run("My favorite color is blue and I love pizza.")
    
    # Later conversation (memory persists)
    response = await agent.run("What do you remember about me?")
    print(response.content)

asyncio.run(main())
```
