#!/usr/bin/env python3
"""
Schema Validation Utilities for MindMeld

This module provides a consistent approach to validating data structures
against JSON schemas throughout the MindMeld framework.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import jsonschema

from utils.error_handling import SchemaValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent / "agent_report_schema.json"


def load_schema(schema_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load a JSON schema from a file.

    Args:
        schema_path: Path to schema file, or None to use default

    Returns:
        Loaded schema as a dictionary

    Raises:
        SchemaValidationError: If schema cannot be loaded
    """
    if schema_path is None:
        schema_path = DEFAULT_SCHEMA_PATH

    try:
        with open(schema_path) as f:
            return json.load(f)
    except Exception as e:
        raise SchemaValidationError(
            f"Failed to load schema from {schema_path}: {str(e)}"
        )


def validate_against_schema(
    data: Dict[str, Any],
    schema: Optional[Dict[str, Any]] = None,
    schema_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema: Schema to validate against (if None, will load from schema_path)
        schema_path: Path to schema file (if schema is None)

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if schema is None:
            schema = load_schema(schema_path)

        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error during validation: {str(e)}"


def validate_agent_output(
    report: Dict[str, Any], schema_path: Optional[Union[str, Path]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate agent output against the agent report schema.

    Args:
        report: The agent report to validate
        schema_path: Optional path to schema file

    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_against_schema(report, schema_path=schema_path)


def ensure_valid_agent_output(
    report: Dict[str, Any], schema_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Ensure agent output is valid against schema.

    Args:
        report: The agent report to validate
        schema_path: Optional path to schema file

    Returns:
        The validated report

    Raises:
        SchemaValidationError: If report is invalid
    """
    valid, error = validate_agent_output(report, schema_path)
    if not valid:
        raise SchemaValidationError(f"Agent output validation failed: {error}")

    return report


def normalize_agent_output(
    output: Dict[str, Any],
    agent_name: str,
    payload: str,
    timestamp: int,
    runtime_seconds: float,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Normalize agent output to conform to the schema.

    Args:
        output: Raw agent output
        agent_name: Name of the agent
        payload: Input provided to the agent
        timestamp: Unix timestamp of execution
        runtime_seconds: Execution time in seconds
        job_id: Optional job identifier

    Returns:
        Normalized output conforming to schema
    """
    # Copy system information if it exists
    system_info = output.get("metadata", {}).get("system_info", {})
    if not system_info:
        import platform

        system_info = {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count() or 0,
        }

    # Copy model information if it exists
    model_info = output.get("metadata", {}).get("model_info", {})

    # Create normalized metadata
    metadata = {
        "agent": agent_name,
        "timestamp": timestamp,
        "payload": payload,
        "runtime_seconds": runtime_seconds,
        "system_info": system_info,
    }

    # Add job ID if provided
    if job_id:
        metadata["job_id"] = job_id

    # Add model info if available
    if model_info:
        metadata["model_info"] = model_info

    # Check if output has error information
    if "error" in output:
        normalized = {
            "agent": agent_name,
            "timestamp": timestamp,
            "payload": payload,
            "runtime_seconds": runtime_seconds,
            "metadata": metadata,
            "status": "error",
            "error": output["error"],
        }
    else:
        # Handle success case
        data = output.get("data", {})
        if not data and "result" in output:
            # Convert legacy format
            data = {"result": output["result"]}

        normalized = {
            "agent": agent_name,
            "timestamp": timestamp,
            "payload": payload,
            "runtime_seconds": runtime_seconds,
            "metadata": metadata,
            "status": "success",
            "data": data,
        }

    return normalized


def validate_input_for_agent(
    agent_name: str, input_value: Any, input_type: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate input for an agent based on expected type.

    Args:
        agent_name: Name of the agent
        input_value: Input value to validate
        input_type: Expected input type ("file", "directory", etc.)

    Returns:
        Tuple of (is_valid, error_message)
    """
    import os

    if input_type == "file":
        if not os.path.exists(input_value):
            return False, f"File not found: {input_value}"
        if os.path.isdir(input_value):
            return False, f"Expected file path but received directory: {input_value}"
        return True, None

    elif input_type == "directory":
        if not os.path.exists(input_value):
            return False, f"Directory not found: {input_value}"
        if not os.path.isdir(input_value):
            return False, f"Expected directory but received file: {input_value}"
        return True, None

    elif input_type == "integer":
        try:
            int(input_value)
            return True, None
        except ValueError:
            return False, f"Expected integer but received: {input_value}"

    elif input_type == "string":
        if not isinstance(input_value, str):
            return False, f"Expected string but received: {input_value}"
        return True, None

    # Default case: assume valid
    return True, None
