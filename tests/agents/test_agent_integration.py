# filepath: /Users/cpconnor/projects/mindmeld-v1.1/tests/agents/test_agent_integration.py
# DEPRECATED: This file uses outdated agent references and should not be used.
# Please use /Users/cpconnor/projects/mindmeld-v1.1/tests/test_agent_integration.py instead which uses
# the proper agent imports from packages/agents/claude_agents/agents.

from unittest.mock import patch

import pytest

# These imports reference non-existent modules:
# from agents.test_generator_agent import TestGeneratorAgent
# from agents.code_debug_agent import CodeDebugAgent
# from agents.planner_agent import PlannerAgent


# Setup mock LLM responses
@pytest.fixture
def mock_llm_client():
    with patch("agents.base.LLMClient") as mock_client:
        # Configure mock responses for different prompts
        mock_client.return_value.generate.side_effect = lambda prompt: {
            "analyze": "Mock analysis result",
            "generate_test": "def test_function(): assert True",
            "debug": "Bug found in line 10: variable not initialized",
            "plan": "1. Analyze code\n2. Generate tests\n3. Debug issues",
        }.get(prompt[:10], "Default mock response")
        yield mock_client.return_value


# NOTE: These tests are disabled as they reference non-existent agent modules.
# The proper implementations have been moved to packages/agents/claude_agents/agents/

"""
def test_test_generator_agent(mock_llm_client):
    # Setup
    output_dir = "./test_output"
    os.makedirs(output_dir, exist_ok=True)

    # Create agent
    agent = TestGeneratorAgent(llm_client=mock_llm_client, output_dir=output_dir)

    # Test functionality
    result = agent.generate_tests_for_file("sample_code.py", "def add(a, b): return a + b")

    # Verify results
    assert "test_function" in result
    assert os.path.exists(f"{output_dir}/test_sample_code.py")

def test_debug_agent(mock_llm_client):
    agent = CodeDebugAgent(llm_client=mock_llm_client)
    result = agent.debug_code("def buggy(): x = 1/0")
    assert "Bug found" in result

def test_planner_agent(mock_llm_client):
    agent = PlannerAgent(llm_client=mock_llm_client)
    plan = agent.create_plan("Optimize this codebase")
    assert isinstance(plan, list)
    assert len(plan) > 0

def test_agent_pipeline_integration(mock_llm_client):
    # Test the full pipeline of agents working together
    planner = PlannerAgent(llm_client=mock_llm_client)
    debugger = CodeDebugAgent(llm_client=mock_llm_client)
    test_generator = TestGeneratorAgent(llm_client=mock_llm_client, output_dir="./test_output")

    # Create a plan
    plan = planner.create_plan("Analyze sample code")

    # Debug the code
    debug_result = debugger.debug_code("def sample(): pass")

    # Generate tests
    test_result = test_generator.generate_tests_for_file("sample.py", "def sample(): pass")

    # Check that the flow works
    assert plan and debug_result and test_result
"""
