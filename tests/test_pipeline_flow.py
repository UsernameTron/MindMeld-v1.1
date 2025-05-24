#!/usr/bin/env python3
"""
Tests for the end-to-end pipeline flow between agents.
"""

from unittest.mock import MagicMock

import pytest

from packages.agents.claude_agents.agents.executor import ExecutorAgent
from packages.agents.claude_agents.agents.planner import PlannerAgent
from packages.agents.claude_agents.api.client import ClaudeAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock Claude API client with side effects for different agent calls."""
    client = MagicMock(spec=ClaudeAPIClient)

    # Configure planner agent mock response
    planner_api_response = MagicMock()
    planner_api_response.content = [
        MagicMock(
            text="""```json
{
  "objective": "Summarize research papers",
  "steps": [
    {
      "id": "step_1",
      "description": "Extract key information from papers",
      "expected_outcome": "List of extracted facts and findings"
    },
    {
      "id": "step_2",
      "description": "Identify common themes across papers",
      "expected_outcome": "Thematic groupings of research findings"
    },
    {
      "id": "step_3",
      "description": "Write concise summary of all papers",
      "expected_outcome": "Consolidated summary document"
    }
  ]
}
```"""
        )
    ]

    # Configure executor agent mock responses
    executor_responses = [
        MagicMock(
            content=[
                MagicMock(
                    text="""
I've extracted the key information from the research papers:

1. Paper 1: "Deep Learning Approaches for NLP"
   - Key finding: Transformer models outperform RNNs on most NLP tasks
   - Methodology: Comparative analysis across 12 benchmarks
   - Limitations: High computational requirements

2. Paper 2: "Efficient Transformers"
   - Key finding: Sparse attention patterns reduce computation by 70%
   - Methodology: Novel algorithm for attention pruning
   - Limitations: Small accuracy degradation (1-2%)

3. Paper 3: "Low-Resource NLP"
   - Key finding: Data augmentation improves performance by 15% in low-resource settings
   - Methodology: Back-translation and synonym replacement techniques
   - Limitations: Language-specific patterns affect generalizability
"""
                )
            ]
        ),
        MagicMock(
            content=[
                MagicMock(
                    text="""
Common themes identified across papers:

1. Efficiency vs Performance Trade-offs
   - All papers discuss the balance between computational efficiency and model performance
   - Sparse models consistently show promising directions for practical applications

2. Architectural Innovations
   - Attention mechanisms continue to drive progress in the field
   - Hybrid architectures combining different model types show strong results

3. Data Requirements
   - Papers increasingly focus on reducing data dependencies
   - Transfer learning appears in all papers as a critical technique
"""
                )
            ]
        ),
        MagicMock(
            content=[
                MagicMock(
                    text="""
# Research Summary: Recent Advances in NLP Models

This summary synthesizes findings from three recent papers on natural language processing approaches.

## Key Findings

Recent research indicates transformer architectures substantially outperform recurrent neural networks across NLP benchmarks, though with higher computational demands. Efficiency improvements through sparse attention mechanisms demonstrate promising results, reducing computation by up to 70% with minimal accuracy impact (1-2%).

Data augmentation techniques, particularly back-translation and synonym replacement, show a consistent 15% improvement in low-resource settings, though language-specific patterns affect generalizability.

## Emerging Trends

The literature reveals a consistent focus on balancing efficiency and performance, with sparse models emerging as a practical direction for real-world applications. Attention mechanisms continue to drive architectural innovation, while hybrid approaches combining different model types demonstrate strong results.

Data dependency reduction appears as a cross-cutting concern, with all papers emphasizing transfer learning techniques to maximize performance with limited training data.

## Research Implications

These findings suggest future NLP research should focus on sparse modeling techniques, efficient attention mechanisms, and transfer learning approaches that can work effectively in data-constrained environments.
"""
                )
            ]
        ),
    ]

    # Use a persistent counter to track calls
    call_count = {"value": 0}

    def mock_api_side_effect(*args, **kwargs):
        if "Summarize research papers" in str(
            args
        ) or "Summarize research papers" in str(kwargs):
            return planner_api_response
        else:
            response = executor_responses[call_count["value"]]
            call_count["value"] += 1
            if call_count["value"] >= len(executor_responses):
                call_count["value"] = 0
            return response

    client.send_message.side_effect = mock_api_side_effect
    return client


@pytest.fixture
def planner_agent(mock_api_client):
    """Create a planner agent with the configured mock client."""
    return PlannerAgent(api_client=mock_api_client)


@pytest.fixture
def executor_agent(mock_api_client):
    """Create an executor agent with the configured mock client."""
    return ExecutorAgent(api_client=mock_api_client)


def test_end_to_end_pipeline(planner_agent, executor_agent):
    """Test the complete planning and execution pipeline."""
    # Get plan from planner agent
    plan = planner_agent.process("Summarize research papers")

    # Verify plan structure
    assert isinstance(plan, dict)
    assert "steps" in plan
    assert isinstance(plan["steps"], list)

    # Execute each step in the plan
    for step in plan["steps"]:
        # Verify step structure
        assert "description" in step
        assert "expected_outcome" in step

        # Process step with executor
        output = executor_agent.process(
            {"id": step["id"], "description": step["description"]}
        )

        # Verify executor output
        assert isinstance(output, dict)
        assert "task_id" in output
        assert output["task_id"] == step["id"]
        assert "completion" in output
