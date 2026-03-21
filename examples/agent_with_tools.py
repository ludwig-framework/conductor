"""
Example: Agent with Tools
"""

import asyncio
import json
from conductor import Agent, tool


@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a symbol."""
    # Mock data - replace with real API
    prices = {"AAPL": 178.50, "GOOGL": 141.80, "MSFT": 378.90}
    price = prices.get(symbol.upper())
    if price:
        return f"${price:.2f}"
    return "Stock not found"


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Mock data - replace with real search API
    return f"Top results for '{query}': [Mock search results would appear here]"


agent = Agent(
    name="research-assistant",
    model="gpt-4o",
    instructions="""You are a research assistant that can:
    - Look up stock prices
    - Do calculations
    - Search the web
    
    Use your tools to help users get accurate information.""",
    tools=[get_stock_price, calculate, search_web]
)


async def main():
    # Query that requires tool use
    response = await agent.run(
        "What's Apple's stock price? Also calculate what 100 shares would cost."
    )
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
