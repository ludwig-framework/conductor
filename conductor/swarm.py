"""
Swarm - Multi-agent coordination
"""

from typing import Literal
from dataclasses import dataclass

from conductor.agent import Agent


CoordinatorType = Literal["round-robin", "hierarchical", "consensus", "autonomous"]


@dataclass
class SwarmResult:
    """Result of a swarm execution."""
    final_output: str
    agent_outputs: dict[str, list[str]]
    iterations: int


class Swarm:
    """
    Multi-agent coordination system.
    
    Enables multiple agents to work together dynamically on a task.
    
    Args:
        agents: List of participating agents
        coordinator: Coordination strategy
            - "round-robin": Agents take turns
            - "hierarchical": Lead agent coordinates others
            - "consensus": Agents vote on decisions
            - "autonomous": Agents self-organize
    
    Example:
        swarm = Swarm(
            agents=[coder, reviewer, tester],
            coordinator="hierarchical"
        )
        result = await swarm.run("Build a REST API")
    """
    
    def __init__(
        self,
        agents: list[Agent],
        coordinator: CoordinatorType = "round-robin",
        max_iterations: int = 10,
    ):
        self.agents = agents
        self.coordinator = coordinator
        self.max_iterations = max_iterations
    
    async def run(self, task: str) -> SwarmResult:
        """
        Execute the swarm on a task.
        
        Args:
            task: The task description
            
        Returns:
            SwarmResult with outputs from all agents
        """
        if self.coordinator == "round-robin":
            return await self._run_round_robin(task)
        elif self.coordinator == "hierarchical":
            return await self._run_hierarchical(task)
        elif self.coordinator == "consensus":
            return await self._run_consensus(task)
        else:
            return await self._run_autonomous(task)
    
    async def _run_round_robin(self, task: str) -> SwarmResult:
        """Round-robin: each agent processes in sequence."""
        outputs = {agent.name: [] for agent in self.agents}
        current_context = task
        iterations = 0
        
        for i in range(self.max_iterations):
            agent = self.agents[i % len(self.agents)]
            
            prompt = f"Task: {task}\n\nCurrent state: {current_context}\n\nYour turn."
            response = await agent.run(prompt)
            
            outputs[agent.name].append(response.content)
            current_context = response.content
            iterations += 1
            
            # Check for completion signal
            if "[DONE]" in response.content:
                break
        
        return SwarmResult(
            final_output=current_context,
            agent_outputs=outputs,
            iterations=iterations,
        )
    
    async def _run_hierarchical(self, task: str) -> SwarmResult:
        """Hierarchical: first agent coordinates the others."""
        lead = self.agents[0]
        workers = self.agents[1:]
        outputs = {agent.name: [] for agent in self.agents}
        
        # Lead agent plans the work
        plan_prompt = f"Task: {task}\n\nPlan how to distribute this work among: {[w.name for w in workers]}"
        plan = await lead.run(plan_prompt)
        outputs[lead.name].append(plan.content)
        
        # Workers execute
        for worker in workers:
            work_prompt = f"Task: {task}\n\nPlan: {plan.content}\n\nDo your part as {worker.name}."
            result = await worker.run(work_prompt)
            outputs[worker.name].append(result.content)
        
        # Lead synthesizes
        synth_prompt = f"Task: {task}\n\nResults: {outputs}\n\nSynthesize the final output."
        final = await lead.run(synth_prompt)
        outputs[lead.name].append(final.content)
        
        return SwarmResult(
            final_output=final.content,
            agent_outputs=outputs,
            iterations=len(workers) + 2,
        )
    
    async def _run_consensus(self, task: str) -> SwarmResult:
        """Consensus: agents discuss and vote."""
        outputs = {agent.name: [] for agent in self.agents}
        
        # Each agent proposes
        proposals = []
        for agent in self.agents:
            prompt = f"Task: {task}\n\nPropose a solution."
            response = await agent.run(prompt)
            proposals.append((agent.name, response.content))
            outputs[agent.name].append(response.content)
        
        # Each agent votes
        votes = []
        for agent in self.agents:
            vote_prompt = f"Task: {task}\n\nProposals:\n"
            for name, prop in proposals:
                vote_prompt += f"\n{name}: {prop}\n"
            vote_prompt += "\nVote for the best proposal (respond with the agent name)."
            
            vote = await agent.run(vote_prompt)
            votes.append(vote.content.strip())
            outputs[agent.name].append(f"Voted for: {vote.content}")
        
        # Find winner
        from collections import Counter
        winner = Counter(votes).most_common(1)[0][0]
        final = next(prop for name, prop in proposals if name == winner)
        
        return SwarmResult(
            final_output=final,
            agent_outputs=outputs,
            iterations=len(self.agents) * 2,
        )
    
    async def _run_autonomous(self, task: str) -> SwarmResult:
        """Autonomous: agents self-organize based on capabilities."""
        # Simplified: similar to hierarchical but agents volunteer
        return await self._run_hierarchical(task)
