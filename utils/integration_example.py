#!/usr/bin/env python3
"""
MindMeld Utilities Integration

This module shows how to use all the new MindMeld utility modules together.
It can be used as a reference implementation for integrating the utilities
into existing or new agent implementations.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.error_handling import (
    MindMeldError,
    Transaction,
    format_error_for_json,
    retry_on_llm_error,
)
from utils.file_operations import read_file, safe_file_write

# Import core utilities
from utils.model_manager import ModelManager
from utils.schema_validator import (
    load_schema,
    normalize_agent_output,
    validate_agent_output,
)
from utils.testing_utils import MockLLMResponse, MockOllamaClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def integrate_utilities_example(
    agent_name: str, payload: str, model_name: Optional[str] = None
):
    """
    Example showing how to use all the MindMeld utility modules together.

    Args:
        agent_name: Name of the agent to run
        payload: Input for the agent (file path, directory, etc.)
        model_name: Optional model name override

    Returns:
        The agent execution result
    """
    # 1. Initialize key components
    model_manager = ModelManager()
    schema = load_schema()
    job_id = f"job_{int(time.time())}"

    # 2. Check model availability
    if agent_name in model_manager.get_llm_dependent_agents():
        agent_model = (
            model_name or model_manager.get_agent_model(agent_name) or "phi3.5:latest"
        )
        logger.info(
            f"Checking availability of model {agent_model} for agent {agent_name}"
        )

        if not model_manager.ensure_model_available(agent_model):
            error_msg = (
                f"Required model {agent_model} is not available for agent {agent_name}"
            )
            logger.error(error_msg)
            return {
                "agent": agent_name,
                "status": "error",
                "error": {"message": error_msg, "type": "ModelUnavailableError"},
            }

    # 3. Execute agent with transaction and retry support
    with Transaction(name=f"agent_execution_{agent_name}") as transaction:
        try:
            # Mock implementation for demonstration purposes
            # In real usage, this would call the actual agent
            @retry_on_llm_error(max_retries=3)
            def execute_agent():
                logger.info(f"Executing agent {agent_name} with payload: {payload}")

                # Simulate agent execution
                # In real usage, this would be replaced with the actual agent call
                return {
                    "agent": agent_name,
                    "status": "success",
                    "data": {
                        "result": f"Simulated execution of {agent_name} on {payload}"
                    },
                }

            # Execute with retry capability
            start_time = time.time()
            result = execute_agent()
            end_time = time.time()

            # Register successful result with transaction
            transaction.register_success(result)

            # 4. Normalize and validate output
            runtime_seconds = end_time - start_time
            normalized_result = normalize_agent_output(
                output=result,
                agent_name=agent_name,
                payload=payload,
                timestamp=int(time.time()),
                runtime_seconds=runtime_seconds,
                job_id=job_id,
            )

            # 5. Validate against schema
            is_valid, error = validate_agent_output(normalized_result, schema)
            if not is_valid:
                logger.warning(f"Validation warning: {error}")
                if "metadata" not in normalized_result:
                    normalized_result["metadata"] = {}
                normalized_result["metadata"]["validation_warning"] = error

            # 6. Save result safely
            output_dir = Path("reports") / agent_name
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{agent_name}_{int(time.time())}.json"

            safe_file_write(output_file, json.dumps(normalized_result, indent=2))
            logger.info(f"Agent result saved to {output_file}")

            return normalized_result

        except Exception as e:
            # 7. Enhanced error handling
            error_data = format_error_for_json(e)
            logger.error(f"Agent execution failed: {error_data.get('message', str(e))}")

            error_result = {
                "agent": agent_name,
                "status": "error",
                "error": error_data,
                "timestamp": int(time.time()),
                "payload": payload,
            }

            # Save error report
            output_dir = Path("reports") / agent_name
            output_dir.mkdir(parents=True, exist_ok=True)
            error_file = output_dir / f"{agent_name}_error_{int(time.time())}.json"

            safe_file_write(error_file, json.dumps(error_result, indent=2))
            logger.error(f"Error report saved to {error_file}")

            return error_result


def run_demo():
    """Run a demonstration of the utilities integration."""
    print("=" * 50)
    print("MindMeld Utilities Integration Demo")
    print("=" * 50)

    # Demo execution
    result = integrate_utilities_example(
        agent_name="demo_agent", payload="example/path.py"
    )

    print("\nExecution Result:")
    print(json.dumps(result, indent=2))

    print("\nUtilities Successfully Integrated!")
    print("=" * 50)


if __name__ == "__main__":
    run_demo()
