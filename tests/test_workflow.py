"""
Tests for Workflow functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from conductor import Agent, Workflow, Step
from conductor.types import Response, Usage


class TestWorkflow:
    """Tests for the Workflow class."""
    
    def test_workflow_creation(self):
        """Test basic workflow creation."""
        agent = Agent(name="test", model="gpt-4o")
        
        workflow = Workflow(
            name="test-workflow",
            steps=[
                Step(agent=agent, task="Do something")
            ]
        )
        
        assert workflow.name == "test-workflow"
        assert len(workflow.steps) == 1
    
    def test_workflow_variable_substitution(self):
        """Test variable substitution in task templates."""
        agent = Agent(name="test", model="gpt-4o")
        
        workflow = Workflow(
            name="test-workflow",
            steps=[
                Step(agent=agent, task="Research {topic}")
            ]
        )
        
        step = workflow.steps[0]
        result = step.task.format(topic="AI")
        
        assert result == "Research AI"
    
    @pytest.mark.asyncio
    async def test_workflow_run(self):
        """Test workflow execution."""
        agent1 = Agent(name="agent1", model="gpt-4o")
        agent2 = Agent(name="agent2", model="gpt-4o")
        
        workflow = Workflow(
            name="test-workflow",
            steps=[
                Step(agent=agent1, task="Step 1: {topic}"),
                Step(agent=agent2, task="Step 2: {step_1}"),
            ]
        )
        
        mock_response = Response(
            content="Result",
            tool_calls=[],
            usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            finish_reason="stop"
        )
        
        with patch.object(agent1, 'run', AsyncMock(return_value=mock_response)):
            with patch.object(agent2, 'run', AsyncMock(return_value=mock_response)):
                result = await workflow.run(topic="Test")
                
                assert result == "Result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
