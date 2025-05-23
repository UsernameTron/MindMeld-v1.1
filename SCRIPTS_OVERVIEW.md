# MindMeld Scripts Overview

This document provides an overview of the scripts available in the MindMeld project, organized by category.

## Agent Execution Scripts
- **scripts/agents/run_agent_simple.py**: Simple agent runner for testing and development. Supports planner, executor, critic, and dependency agents with mock implementations.
- **scripts/agents/run_agent.py**: Enhanced agent runner (currently has syntax issues - use run_agent_simple.py instead)
- **run_all_agents.py**: Run a sequence of agents in pipeline mode, passing outputs as inputs to subsequent agents
- **run_code_debug.py**: Execute the debugging agent to analyze code for issues and suggest fixes
- **run_test_generator.py**: Run the test generation agent to create unit tests for specified code
- **run_dependency_check.py**: Analyze project dependencies for security issues and outdated packages
- **scripts/update_agent_tools.py**: Update agent tool definitions to be compatible with the latest Claude API
- **scripts/verify_api_tools.py**: Test API tool compatibility with the Claude service

## Test and Validation Scripts
- **run_tests_with_env.sh**: Run pytest with proper environment variables loaded from .env file
- **run_test_coverage.sh**: Generate test coverage reports and output HTML visualization
- **validate_reports.py**: Validate agent output reports against JSON schema definitions
- **validate_ci_environment.sh**: Verify that CI environment has all required dependencies and secrets
- **test_redis.py**: Test Redis connection and basic operations for caching layer
- **verify-component.sh**: Validate individual components meet project requirements
- **verify-sprint.sh**: Test completed sprint tasks against acceptance criteria

## Context and Coverage Generation
- **generate_claude_context.py**: Create context files for Claude agents with specific knowledge
- **generate_priority_tests.py**: Identify and generate high-priority tests based on code changes
- **generate_docs.py**: Auto-generate documentation from code comments and docstrings
- **generate_architecture_review.py**: Create architecture diagram and component relationship documentation
- **generate_coverage_badges.py**: Generate coverage badges for README based on test coverage
- **fix_claude_context.sh**: Fix formatting issues in Claude context files to ensure compatibility

## API and Server Scripts
- **scripts/start_api.sh**: Start the MindMeld API server with proper environment configuration
- **monitor_api_health.py**: Monitor API health and send alerts if issues are detected

## Development Tools
- **retry_handler.py**: Utility for retrying failed operations with configurable backoff
- **setup_dev_environment.sh**: Set up development environment with required dependencies

---

### How to Run
- Python scripts: `python script_name.py`
- Shell scripts: `bash script_name.sh` or `./script_name.sh`
- Scripts with arguments: See below for examples

### Common Usage Examples
```bash
# Update tools in Claude agent files
python scripts/update_agent_tools.py

# Verify API tool compatibility
python scripts/verify_api_tools.py

# Run the agent with specific arguments
python scripts/agents/run_agent_simple.py --agent planner --payload "Create a plan to implement testing"
```

---

Update this file as scripts are added, removed, or renamed.
