#!/usr/bin/env python3
"""
Enhanced agent runner for MindMeld platform with improved error handling,
file operations, and LLM interaction.

Includes input validation, schema compliance, error handling, and performance optimization.
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema
import requests
from utils.error_handling import (
    FileProcessingError,
    LLMCallError,
    MindMeldError,
    Transaction,
    ValidationError,
    format_error_for_json,
    retry_on_llm_error,
)
from utils.file_operations import path_exists, read_file, safe_file_write, write_file
from utils.llm_client import get_default_model, get_model_config
from utils.model_manager import ModelManager
from utils.schema_validator import normalize_agent_output, validate_agent_output

from packages.agents.AgentFactory import AGENT_INPUT_TYPES, AGENT_REGISTRY


# load the schema once
def load_schema():
    """Load the agent report schema from the schema file."""
    schema_path = Path(__file__).parent / "agent_report_schema.json"
    try:
        return json.loads(read_file(schema_path))
    except FileProcessingError as e:
        print(f"Error loading schema: {e}")
        # Provide a minimal default schema if the file can't be loaded
        return {
            "type": "object",
            "required": ["agent", "status", "metadata"],
            "properties": {
                "agent": {"type": "string"},
                "status": {"type": "string", "enum": ["success", "error"]},
                "metadata": {"type": "object"},
            },
        }


REPORT_SCHEMA = load_schema()


def get_system_info():
    """Get system information for metadata."""
    return {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def get_model_info():
    """Get model information for metadata."""
    return {
        "name": os.getenv("OLLAMA_MODEL", "phi3.5:latest"),
        "config": {
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("MAX_TOKENS", "2048")),
        },
    }


def validate_input(agent_name: str, payload: str) -> Optional[Dict[str, Any]]:
    """
    Validate that the input matches the agent's expected type.
    Returns an error dict if validation fails, None if validation passes.

    Args:
        agent_name: Name of the agent
        payload: Input payload for the agent

    Returns:
        Error report dict or None if validation passes
    """
    # Skip validation if agent doesn't have a defined input type
    if agent_name not in AGENT_INPUT_TYPES:
        return None

    input_type = AGENT_INPUT_TYPES[agent_name]

    # Check for empty payload
    if not payload or (isinstance(payload, str) and payload.strip() == ""):
        return {
            "agent": agent_name,
            "status": "error",
            "error": {"message": "Empty payload provided", "type": "ValidationError"},
            "metadata": {
                "agent": agent_name,
                "timestamp": int(time.time()),
                "system_info": get_system_info(),
                "model_info": get_model_info(),
            },
        }

    # Validate file input
    if input_type == "file":
        path = Path(payload)
        if not path_exists(path):
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"File not found: {payload}",
                    "type": "ValidationError",
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info(),
                },
            }
        if path.is_dir():
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"Expected file path but received directory: {payload}",
                    "type": "ValidationError",
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info(),
                },
            }

    # Validate directory input
    elif input_type == "directory":
        path = Path(payload)
        if not path_exists(path):
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"Directory not found: {payload}",
                    "type": "ValidationError",
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info(),
                },
            }
        if not path.is_dir():
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"Expected directory path but received file: {payload}",
                    "type": "ValidationError",
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info(),
                },
            }

    # Validate integer input
    elif input_type == "integer":
        try:
            int(payload)  # Just validate, don't convert here
        except (ValueError, TypeError):
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"Agent {agent_name} expected integer input but received: {payload}",
                    "type": "ValidationError",
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info(),
                },
            }

    # All validation passed
    return None


def check_model_availability(model_name="phi3.5:latest"):
    """Check if required model is available using ModelManager."""
    try:
        # Use the model manager to check availability
        model_manager = ModelManager()
        is_available = model_manager.check_model_availability(model_name)

        return is_available
    except Exception as e:
        logger.error(f"Error checking model availability: {str(e)}")
        return False


def normalize_agent_output(
    result: Any,
    agent_name: str,
    payload: str,
    timestamp: int,
    runtime_seconds: float,
    job_id: str,
) -> Dict[str, Any]:
    """
    Normalize the agent output to conform to the schema using schema validator.
    """
    try:
        # Use the schema validator's normalize function
        return normalize_agent_output(
            output=result,
            agent_name=agent_name,
            payload=payload,
            timestamp=timestamp,
            runtime_seconds=runtime_seconds,
            job_id=job_id,
        )
    except ImportError:
        # Fall back to original implementation if module not available
        # Start with base metadata
        metadata = {
            "agent": agent_name,
            "timestamp": timestamp,
            "payload": payload[:200] if payload else "",  # Truncate if too long
            "runtime_seconds": runtime_seconds,
            "job_id": job_id,
            "system_info": get_system_info(),
            "model_info": get_model_info(),
        }

    # For string results (likely errors)
    if isinstance(result, str):
        if "[ERROR]" in result:
            return {
                "agent": agent_name,
                "status": "error",
                "error": {"message": result, "type": "AgentError"},
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": metadata,
            }
        else:
            return {
                "agent": agent_name,
                "status": "success",
                "data": {"result": result},
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": metadata,
            }

    # For dictionary results
    if isinstance(result, dict):
        normalized = {
            "agent": agent_name,
            "timestamp": timestamp,
            "payload": payload,
            "runtime_seconds": runtime_seconds,
        }

        # Copy over metadata if it exists, merge with our metadata
        if "metadata" in result:
            result_metadata = result.pop("metadata", {})
            metadata.update(result_metadata)
        normalized["metadata"] = metadata

        # Determine status
        if "status" in result:
            normalized["status"] = result["status"]
        elif "error" in result and result["error"]:
            normalized["status"] = "error"
            if isinstance(result["error"], str):
                normalized["error"] = {"message": result["error"], "type": "AgentError"}
            else:
                normalized["error"] = result["error"]
        elif "fixed" in result:
            normalized["status"] = "success" if result["fixed"] else "error"
            normalized["data"] = {"fixed": result["fixed"]}
            if "diagnostics" in result:
                normalized["data"]["diagnostics"] = result["diagnostics"]
        else:
            normalized["status"] = "success"

        # For error status, ensure error object exists
        if normalized.get("status") == "error" and "error" not in normalized:
            error_msg = result.get("error", "Unknown error")
            normalized["error"] = {"message": str(error_msg), "type": "AgentError"}

        # Copy all other fields to data
        data_fields = {
            k: v
            for k, v in result.items()
            if k
            not in [
                "agent",
                "status",
                "timestamp",
                "payload",
                "runtime_seconds",
                "metadata",
                "error",
            ]
        }
        if data_fields:
            normalized["data"] = data_fields
        elif "data" not in normalized and normalized.get("status") == "success":
            normalized["data"] = {
                "result": "Agent executed without specific data output"
            }

        return normalized

    # For list or other objects
    return {
        "agent": agent_name,
        "status": "success",
        "data": {"result": str(result) if not isinstance(result, list) else result},
        "timestamp": timestamp,
        "payload": payload,
        "runtime_seconds": runtime_seconds,
        "metadata": metadata,
    }


def main():
    """Run an agent from the command line."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run an agent from the command line")
    parser.add_argument("agent_name", help="Name of the agent to run")
    parser.add_argument(
        "payload", help="Input for the agent (file path, directory path, etc.)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--output-dir", default="reports", help="Directory to save the report in"
    )
    parser.add_argument("--model", help="Override the default model")
    parser.add_argument("--list", action="store_true", help="List available agents")

    args = parser.parse_args()

    # List available agents
    if args.list:
        print("Available agents:")
        for agent in sorted(AGENT_REGISTRY.keys()):
            input_type = AGENT_INPUT_TYPES.get(agent, "any")
            print(f"  {agent} (input: {input_type})")
        return 0

    # Create job ID for traceability
    job_id = str(uuid.uuid4())
    timestamp = int(time.time())

    # Get agent name and payload
    name = args.agent_name
    payload = args.payload

    # Create output directories and report path
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Create agent-specific directory
    agent_dir = output_dir / name
    agent_dir.mkdir(exist_ok=True)

    # Define report path using agent name and timestamp
    report_path = agent_dir / f"{name}_{timestamp}.json"

    # Initialize the model manager
    model_manager = ModelManager()

    # Validate input
    validation_result = validate_input(name, payload)
    if validation_result:
        # Input validation failed, write the error report
        safe_file_write(report_path, json.dumps(validation_result, indent=2))
        print(
            f"❌ Input validation failed: {validation_result.get('error', {}).get('message', 'Unknown error')}"
        )
        return 1

    # Check if agent exists in registry
    if name not in AGENT_REGISTRY:
        error_result = {
            "agent": name,
            "status": "error",
            "error": {"message": f"Unknown agent: {name}", "type": "ImportError"},
            "timestamp": timestamp,
            "payload": payload,
            "metadata": {
                "agent": name,
                "timestamp": timestamp,
                "job_id": job_id,
                "system_info": get_system_info(),
                "model_info": get_model_info(),
            },
        }
        safe_file_write(report_path, json.dumps(error_result, indent=2))
        print(f"❌ Unknown agent: {name}")
        return 1

    # Check model availability for LLM-dependent agents
    if name in model_manager.get_llm_dependent_agents():
        # Get the model for this agent (either from registry or default)
        model_name = (
            args.model
            or model_manager.get_agent_model(name)
            or os.environ.get("OLLAMA_MODEL", "phi3.5:latest")
        )

        # Try to ensure the model is available (with auto-pull if configured)
        if not model_manager.ensure_model_available(model_name):
            error_result = {
                "agent": name,
                "status": "error",
                "error": {
                    "message": f"Required model not available: {model_name}",
                    "type": "ModelUnavailableError",
                },
                "timestamp": timestamp,
                "payload": payload,
                "metadata": {
                    "agent": name,
                    "timestamp": timestamp,
                    "job_id": job_id,
                    "system_info": get_system_info(),
                    "model_info": {"name": model_name},
                },
            }
            safe_file_write(report_path, json.dumps(error_result, indent=2))
            print(f"❌ Model not available: {model_name}")
            return 1
            error_result = {
                "agent": name,
                "status": "error",
                "error": {
                    "message": f"Required model not available: {model_name}",
                    "type": "ModelUnavailableError",
                },
                "timestamp": timestamp,
                "payload": payload,
                "metadata": {
                    "agent": name,
                    "timestamp": timestamp,
                    "job_id": job_id,
                    "system_info": get_system_info(),
                    "model_info": {"name": model_name},
                },
            }
            with open(report_path, "w") as f:
                json.dump(error_result, f, indent=2)
            print(f"❌ Model not available: {model_name}")
            return 1

    # Create the agent
    try:
        creator = AGENT_REGISTRY[name]
        # always instantiate with no args
        if callable(creator):
            agent = creator()
        else:
            agent = creator
    except Exception as e:
        error_result = {
            "agent": name,
            "status": "error",
            "error": {
                "message": f"Failed to create agent {name}: {str(e)}",
                "type": e.__class__.__name__,
            },
            "timestamp": timestamp,
            "payload": payload,
            "metadata": {
                "agent": name,
                "timestamp": timestamp,
                "job_id": job_id,
                "system_info": get_system_info(),
                "model_info": get_model_info(),
            },
        }
        with open(report_path, "w") as f:
            json.dump(error_result, f, indent=2)
        print(f"❌ Failed to create agent: {e}")
        return 1

    # Execute the agent with timing and transaction support
    start_time = time.time()

    # Create a transaction for atomic operations
    with Transaction(name=f"agent_execution_{name}") as transaction:
        try:
            # Define a function for executing agent with retry capabilities
            @retry_on_llm_error(max_retries=3, delay=1.0, backoff_factor=2.0)
            def execute_agent():
                if hasattr(agent, "analyze_deps") and name == "dependency_agent":
                    verbose = "--verbose" in sys.argv
                    return agent.analyze_deps(payload, verbose)
                elif hasattr(agent, "run"):
                    try:
                        return agent.run(payload)
                    except TypeError:
                        return agent.run()
                else:
                    return agent(payload) if callable(agent) else agent

            # Execute the agent with retry capability
            result = execute_agent()

            # Register successful result with transaction
            transaction.register_success(result)

        except Exception as e:
            # Handle execution error with improved error formatting
            end_time = time.time()
            runtime_seconds = end_time - start_time

            # Format error for JSON output
            error_data = format_error_for_json(e)

            # Add agent-specific context
            if not isinstance(e, MindMeldError):
                error_data["agent"] = name

            error_result = {
                "agent": name,
                "status": "error",
                "error": error_data,
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": {
                    "agent": name,
                    "timestamp": timestamp,
                    "job_id": job_id,
                    "system_info": get_system_info(),
                    "model_info": get_model_info(),
                },
            }

            # Use safe_file_write to write the error report
            safe_file_write(report_path, json.dumps(error_result, indent=2))

            print(f"❌ Agent execution failed: {error_data.get('message', str(e))}")
            return 1

    # Calculate runtime and normalize output
    end_time = time.time()
    runtime_seconds = end_time - start_time

    # Normalize the result using schema validator
    try:
        from utils.schema_validator import (
            normalize_agent_output as normalize_schema_output,
        )

        normalized_result = normalize_schema_output(
            output=result,
            agent_name=name,
            payload=payload,
            timestamp=timestamp,
            runtime_seconds=runtime_seconds,
            job_id=job_id,
        )
    except ImportError:
        # Fall back to local normalization if module not available
        normalized_result = normalize_agent_output(
            result, name, payload, timestamp, runtime_seconds, job_id
        )

    # Validate against schema
    try:
        # Use schema validator to validate output
        from utils.schema_validator import validate_agent_output

        validation_success, validation_error = validate_agent_output(
            normalized_result, REPORT_SCHEMA
        )

        if not validation_success:
            # Add validation error but don't fail
            if "metadata" not in normalized_result:
                normalized_result["metadata"] = {}
            normalized_result["metadata"]["validation_error"] = validation_error
            print(f"⚠️ Warning: Schema validation failed: {validation_error}")
    except ImportError:
        # Fall back to direct jsonschema validation
        try:
            jsonschema.validate(instance=normalized_result, schema=REPORT_SCHEMA)
            validation_success = True
        except jsonschema.exceptions.ValidationError as e:
            validation_success = False
            # Add validation error but don't fail
            if "metadata" not in normalized_result:
                normalized_result["metadata"] = {}
            normalized_result["metadata"]["validation_error"] = str(e)
            print(f"⚠️ Warning: Schema validation failed: {e}")

    # Write the report file using safe file write
    safe_file_write(report_path, json.dumps(normalized_result, indent=2))

    print(f"✅ Agent execution complete, report saved to {report_path}")
    if not validation_success:
        print("⚠️ Note: Output required schema normalization")

    return 0


if __name__ == "__main__":
    sys.exit(main())
