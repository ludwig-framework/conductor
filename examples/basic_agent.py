"""
Example: Basic Agent
"""

import asyncio
from conductor import Agent

agent = Agent(
    name="assistant",
    model="gpt-4o",
    instructions="You are a helpful assistant."
)


async def main():
    response = await agent.run("What are the benefits of TypeScript over JavaScript?")
    print(response.content)
    print(f"\nTokens used: {response.usage.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())
