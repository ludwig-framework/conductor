"""
Example: Agent Swarm for Problem Solving
"""

import asyncio
from conductor import Agent, Swarm

# Create a team of specialized agents
analyst = Agent(
    name="data-analyst",
    model="gpt-4o",
    instructions="""You are a data analyst. 
    You analyze problems from a data-driven perspective.
    Focus on metrics, patterns, and evidence-based insights."""
)

creative = Agent(
    name="creative-strategist",
    model="gpt-4o",
    instructions="""You are a creative strategist.
    You think outside the box and propose innovative solutions.
    Focus on unique angles and creative approaches."""
)

pragmatist = Agent(
    name="pragmatist",
    model="gpt-4o",
    instructions="""You are a practical implementer.
    You focus on feasibility, resources, and execution.
    Identify potential obstacles and realistic timelines."""
)

devil_advocate = Agent(
    name="devil-advocate",
    model="gpt-4o",
    instructions="""You challenge ideas constructively.
    Point out potential flaws and risks.
    Help the team stress-test their thinking."""
)

# Create a swarm with consensus strategy
swarm = Swarm(
    name="strategy-team",
    agents=[analyst, creative, pragmatist, devil_advocate],
    strategy="consensus"
)


async def main():
    problem = """
    Our SaaS startup has 1000 users but only 2% convert to paid.
    Monthly churn is 8%. We have $50k runway left.
    How should we prioritize our next 3 months?
    """
    
    print("Problem:")
    print(problem)
    print("=" * 50)
    print("\nTeam Discussion:")
    print("=" * 50)
    
    result = await swarm.run(problem, rounds=3)
    
    print("\nTeam Consensus:")
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
