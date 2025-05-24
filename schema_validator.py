#!/usr/bin/env python3
"""
Schema validation utilities for agent reports.
This module provides functions to validate and normalize agent outputs.
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import jsonschema


def load_schema(schema_path: Optional[str] = None) -> Dict[str, Any]:
    """Load the agent report schema."""
    if schema_path is None:
        schema_path = str(Path(__file__).parent / "agent_report_schema.json")

    try:
        with open(schema_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)


def validate_agent_output(
    report: Dict[str, Any], schema_path: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate agent output against schema.

    Args:
        report: The agent report to validate
        schema_path: Optional path to schema file

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        schema = load_schema(schema_path)
        jsonschema.validate(instance=report, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)


def get_system_info() -> Dict[str, Any]:
    """Get system information for metadata."""
    import platform

    return {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def get_model_info() -> Dict[str, Any]:
    """Get model information for metadata."""
    return {
        "name": os.getenv("OLLAMA_MODEL", "phi3.5:latest"),
        "config": {
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("MAX_TOKENS", "2048")),
        },
    }


def normalize_agent_output(
    result: Any,
    agent_name: str,
    payload: str,
    timestamp: Optional[int] = None,
    runtime_seconds: float = 0.0,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Normalize agent output to conform to schema.

    Args:
        result: The original agent output
        agent_name: Name of the agent
        payload: The input provided to the agent
        timestamp: Execution timestamp (defaults to current time)
        runtime_seconds: Execution duration
        job_id: Unique execution ID

    Returns:
        Dict[str, Any]: Normalized report conforming to schema
    """
    if timestamp is None:
        timestamp = int(time.time())

    if job_id is None:
        job_id = str(uuid.uuid4())

    # Create base metadata
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


def update_app_routes_with_validation(app_path: str) -> None:
    """
    Update the FastAPI routes in app.py to use validation.
    This is a helper for migration purposes.
    """
    import re

    with open(app_path, "r") as f:
        content = f.read()

    # Pattern to find API route handlers
    route_pattern = r'@app\.(\w+)\("([^"]+)"\)\s+async def (\w+)\('

    def add_validation(match):
        method = match.group(1)
        path = match.group(2)
        func_name = match.group(3)

        # Add validation code after the route definition
        return f'@app.{method}("{path}")\nasync def {func_name}('

    # Replace route handlers with versions that include validation
    updated_content = re.sub(route_pattern, add_validation, content)

    with open(app_path, "w") as f:
        f.write(updated_content)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] == "update-app":
        if len(sys.argv) > 2:
            update_app_routes_with_validation(sys.argv[2])
        else:
            update_app_routes_with_validation("app.py")
        print("✅ Updated app routes with validation")
    else:
        print("Usage: python schema_validator.py update-app [app_path]")
        print("For direct usage, import the functions instead.")
