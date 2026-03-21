"""
Workflow - Multi-agent orchestration
"""

from typing import Any, Optional
from dataclasses import dataclass

from conductor.agent import Agent


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    name: str
    agent: Agent
    prompt_template: str
    output: Optional[str] = None


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    outputs: dict[str, str]
    final_output: str
    steps_completed: int


class Workflow:
    """
    Orchestrate multiple agents in sequence.
    
    Args:
        steps: List of (name, agent, prompt_template) tuples
        parallel: Whether to run independent steps concurrently
    
    Example:
        workflow = Workflow([
            ("research", researcher, "Find information about {topic}"),
            ("write", writer, "Write based on: {research.output}")
        ])
        result = await workflow.run(topic="AI agents")
    """
    
    def __init__(
        self,
        steps: list[tuple[str, Agent, str]],
        parallel: bool = False,
    ):
        self.steps = [
            WorkflowStep(name=name, agent=agent, prompt_template=template)
            for name, agent, template in steps
        ]
        self.parallel = parallel
    
    async def run(self, **variables) -> WorkflowResult:
        """
        Execute the workflow with input variables.
        
        Args:
            **variables: Variables to substitute in prompts
            
        Returns:
            WorkflowResult with all outputs
        """
        outputs = {}
        
        for step in self.steps:
            # Substitute variables and previous outputs
            prompt = self._substitute(step.prompt_template, variables, outputs)
            
            # Run the agent
            response = await step.agent.run(prompt)
            step.output = response.content
            outputs[step.name] = response.content
        
        return WorkflowResult(
            outputs=outputs,
            final_output=self.steps[-1].output if self.steps else "",
            steps_completed=len(self.steps),
        )
    
    def _substitute(
        self,
        template: str,
        variables: dict,
        outputs: dict,
    ) -> str:
        """Substitute variables and step outputs in template."""
        result = template
        
        # Substitute input variables
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        # Substitute step outputs
        for step_name, output in outputs.items():
            result = result.replace(f"{{{step_name}.output}}", str(output))
        
        return result
