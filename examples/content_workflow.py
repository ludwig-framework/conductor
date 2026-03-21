"""
Example: Content Creation Workflow
"""

import asyncio
from conductor import Agent, Workflow, Step

# Define specialized agents
researcher = Agent(
    name="researcher",
    model="gpt-4o",
    instructions="""You are a research specialist. 
    When given a topic, provide comprehensive research including:
    - Key facts and statistics
    - Recent developments
    - Expert opinions
    - Potential angles for content"""
)

writer = Agent(
    name="writer",
    model="gpt-4o",
    instructions="""You are a professional content writer.
    Create engaging, well-structured content based on the research provided.
    Use a conversational but authoritative tone.
    Include compelling headlines and subheadings."""
)

editor = Agent(
    name="editor",
    model="gpt-4o",
    instructions="""You are a senior editor.
    Review content for:
    - Grammar and spelling
    - Clarity and flow
    - Engagement and readability
    - Factual accuracy
    Provide the polished final version."""
)

# Create the workflow
workflow = Workflow(
    name="content-pipeline",
    steps=[
        Step(agent=researcher, task="Research the following topic: {topic}"),
        Step(agent=writer, task="Write a blog post using this research:\n\n{step_1}"),
        Step(agent=editor, task="Edit and polish this draft:\n\n{step_2}"),
    ]
)


async def main():
    topic = "The impact of AI on software development in 2024"
    
    print(f"Creating content about: {topic}")
    print("=" * 50)
    
    result = await workflow.run(topic=topic)
    
    print("\nFinal Article:")
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
