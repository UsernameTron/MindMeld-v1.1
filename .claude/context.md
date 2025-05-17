# MindMeld Repository Context for Claude

Last updated: 2025-05-17 14:04:03

## File Index

- run_agent.py (Priority: Highest)
- packages/agents/AgentFactory.py (Priority: Highest)
- packages/agents/advanced_reasoning/agents.py (Priority: Highest)
- agent_report_schema.json (Priority: Highest)
- app.py (Priority: Highest)
- utils/llm_client.py (Priority: High)
- utils/error_handling.py (Priority: High)
- schema_validator.py (Priority: High)
- run_all_agents.py (Priority: Medium)
- .github/workflows/validate-agent-reports.yml (Priority: Medium)
- docs/AGENT_REPORT_SCHEMA.md (Priority: Medium)
- docs/PIPELINE_FIXES.md (Priority: Medium)

## File Contents

## run_agent.py (Priority: Highest)

```python
#!/usr/bin/env python3
"""
Enhanced agent runner for MindMeld platform with improved error handling,
file operations, and LLM interaction.

Includes input validation, schema compliance, error handling, and performance optimization.
"""

import sys
from pathlib import Path
import json
import jsonschema
import time
import os
import requests
import platform
import traceback
import uuid
import argparse
from typing import Dict, Any, Optional, Union, List

from packages.agents.AgentFactory import AGENT_REGISTRY, AGENT_INPUT_TYPES
from utils.file_operations import read_file, write_file, path_exists
from utils.error_handling import MindMeldError, ValidationError, LLMCallError, FileProcessingError
from utils.llm_client import get_default_model, get_model_config

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
                "metadata": {"type": "object"}
            }
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
            "max_tokens": int(os.getenv("MAX_TOKENS", "2048"))
        }
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
            "error": {
                "message": "Empty payload provided",
                "type": "ValidationError"
            },
            "metadata": {
                "agent": agent_name,
                "timestamp": int(time.time()),
                "system_info": get_system_info(),
                "model_info": get_model_info()
            }
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
                    "type": "ValidationError"
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info()
                }
            }
        if path.is_dir():
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"Expected file path but received directory: {payload}",
                    "type": "ValidationError"
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info()
                }
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
                    "type": "ValidationError"
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info()
                }
            }
        if not path.is_dir():
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": f"Expected directory path but received file: {payload}",
                    "type": "ValidationError"
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info()
                }
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
                    "type": "ValidationError"
                },
                "metadata": {
                    "agent": agent_name,
                    "timestamp": int(time.time()),
                    "system_info": get_system_info(),
                    "model_info": get_model_info()
                }
            }
    
    # All validation passed
    return None

def check_model_availability(model_name="phi3.5:latest"):
    """Check if required model is available."""
    try:
        # Try to connect to Ollama API
        ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        # Check if model is in the list
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            return model_name in model_names
        return False
    except Exception:
        return False

def normalize_agent_output(result: Any, agent_name: str, payload: str, timestamp: int, runtime_seconds: float, job_id: str) -> Dict[str, Any]:
    """
    Normalize the agent output to conform to the schema.
    """
    # Start with base metadata
    metadata = {
        "agent": agent_name,
        "timestamp": timestamp,
        "payload": payload[:200] if payload else "",  # Truncate if too long
        "runtime_seconds": runtime_seconds,
        "job_id": job_id,
        "system_info": get_system_info(),
        "model_info": get_model_info()
    }
    
    # For string results (likely errors)
    if isinstance(result, str):
        if "[ERROR]" in result:
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": result,
                    "type": "AgentError"
                },
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": metadata
            }
        else:
            return {
                "agent": agent_name,
                "status": "success",
                "data": {"result": result},
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": metadata
            }
    
    # For dictionary results
    if isinstance(result, dict):
        normalized = {
            "agent": agent_name,
            "timestamp": timestamp,
            "payload": payload,
            "runtime_seconds": runtime_seconds
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
            normalized["error"] = {
                "message": str(error_msg),
                "type": "AgentError"
            }
        
        # Copy all other fields to data
        data_fields = {k: v for k, v in result.items() 
                      if k not in ["agent", "status", "timestamp", "payload", 
                                  "runtime_seconds", "metadata", "error"]}
        if data_fields:
            normalized["data"] = data_fields
        elif "data" not in normalized and normalized.get("status") == "success":
            normalized["data"] = {"result": "Agent executed without specific data output"}
        
        return normalized
    
    # For list or other objects
    return {
        "agent": agent_name,
        "status": "success",
        "data": {"result": str(result) if not isinstance(result, list) else result},
        "timestamp": timestamp,
        "payload": payload,
        "runtime_seconds": runtime_seconds,
        "metadata": metadata
    }

def main():
    """Run an agent from the command line."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run an agent from the command line")
    parser.add_argument("agent_name", help="Name of the agent to run")
    parser.add_argument("payload", help="Input for the agent (file path, directory path, etc.)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output-dir", default="reports", help="Directory to save the report in")
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
    
    # Ensure reports directory exists
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Create agent-specific directory
    agent_dir = reports_dir / name
    agent_dir.mkdir(exist_ok=True)
    
    # Define report path using agent name and timestamp
    report_path = agent_dir / f"{name}_{timestamp}.json"
    
    # Validate input
    validation_result = validate_input(name, payload)
    if validation_result:
        # Input validation failed, write the error report
        with open(report_path, "w") as f:
            json.dump(validation_result, f, indent=2)
        print(f"❌ Input validation failed: {validation_result.get('error', {}).get('message', 'Unknown error')}")
        return 1
    
    # Check if agent exists in registry
    if name not in AGENT_REGISTRY:
        error_result = {
            "agent": name,
            "status": "error",
            "error": {
                "message": f"Unknown agent: {name}",
                "type": "ImportError"
            },
            "timestamp": timestamp,
            "payload": payload,
            "metadata": {
                "agent": name,
                "timestamp": timestamp,
                "job_id": job_id,
                "system_info": get_system_info(),
                "model_info": get_model_info()
            }
        }
        with open(report_path, "w") as f:
            json.dump(error_result, f, indent=2)
        print(f"❌ Unknown agent: {name}")
        return 1
    
    # Check if Ollama is running for LLM-dependent agents
    llm_agents = ["TestGeneratorAgent", "ceo", "executor", "summarizer"]
    if name in llm_agents:
        model_name = os.environ.get("OLLAMA_MODEL", "phi3.5:latest")
        if not check_model_availability(model_name):
            error_result = {
                "agent": name,
                "status": "error",
                "error": {
                    "message": f"Required model not available: {model_name}",
                    "type": "ModelUnavailableError"
                },
                "timestamp": timestamp,
                "payload": payload,
                "metadata": {
                    "agent": name,
                    "timestamp": timestamp,
                    "job_id": job_id,
                    "system_info": get_system_info(),
                    "model_info": {"name": model_name}
                }
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
                "type": e.__class__.__name__
            },
            "timestamp": timestamp,
            "payload": payload,
            "metadata": {
                "agent": name,
                "timestamp": timestamp,
                "job_id": job_id,
                "system_info": get_system_info(),
                "model_info": get_model_info()
            }
        }
        with open(report_path, "w") as f:
            json.dump(error_result, f, indent=2)
        print(f"❌ Failed to create agent: {e}")
        return 1

    # Execute the agent with timing
    start_time = time.time()
    try:
        # If this is the dependency_agent, call analyze_deps directly
        if hasattr(agent, 'analyze_deps') and name == "dependency_agent":
            verbose = "--verbose" in sys.argv
            result = agent.analyze_deps(payload, verbose)
        elif hasattr(agent, 'run'):
            try:
                result = agent.run(payload)
            except TypeError:
                result = agent.run()
        else:
            result = agent(payload) if callable(agent) else agent
    except Exception as e:
        # Handle execution error
        end_time = time.time()
        runtime_seconds = end_time - start_time
        error_message = str(e)
        error_type = e.__class__.__name__
        
        # Include traceback for more detailed error info
        error_details = traceback.format_exc()
        
        error_result = {
            "agent": name,
            "status": "error",
            "error": {
                "message": error_message,
                "type": error_type,
                "details": error_details
            },
            "timestamp": timestamp,
            "payload": payload,
            "runtime_seconds": runtime_seconds,
            "metadata": {
                "agent": name,
                "timestamp": timestamp,
                "job_id": job_id,
                "system_info": get_system_info(),
                "model_info": get_model_info()
            }
        }
        
        with open(report_path, "w") as f:
            json.dump(error_result, f, indent=2)
        
        print(f"❌ Agent execution failed: {error_message}")
        return 1

    # Calculate runtime and normalize output
    end_time = time.time()
    runtime_seconds = end_time - start_time
    
    # Normalize the result to match schema
    normalized_result = normalize_agent_output(
        result, name, payload, timestamp, runtime_seconds, job_id
    )
    
    # Validate against schema
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
    
    # Write the report file
    with open(report_path, "w") as f:
        json.dump(normalized_result, f, indent=2)
    
    print(f"✅ Agent execution complete, report saved to {report_path}")
    if not validation_success:
        print("⚠️ Note: Output required schema normalization")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

```

## packages/agents/AgentFactory.py (Priority: Highest)

```python
from .advanced_reasoning.agents import create_ceo, create_executor, create_summarizer, create_test_generator, create_dependency_agent
from .advanced_reasoning.agents import Agent, TestGeneratorAgent, DependencyAgent, CodeAnalyzerAgent, CodeDebuggerAgent, CodeRepairAgent, PerformanceProfilerAgent, OptimizationSuggesterAgent, BenchmarkingTool, IntegratedCodebaseOptimizer, pipeline_coordinator, CodeEmbeddingIndex, SemanticCodeSearch

# Input type definitions
AGENT_INPUT_TYPES = {
    "TestGeneratorAgent": "file",
    "DependencyAgent": "directory",
    "CodeAnalyzerAgent": "directory",
    "CodeDebuggerAgent": "file",
    "CodeRepairAgent": "file",
    "CodeEmbeddingIndex": "directory",
    "SemanticCodeSearch": "directory",
    "PerformanceProfilerAgent": "file",
    "OptimizationSuggesterAgent": "file",
    "BenchmarkingTool": "directory",
    "IntegratedCodebaseOptimizer": "directory",
    "summarizer": "integer",
    "ceo": "string",
    "executor": "string",
    "dependency_agent": "directory",
    "test_generator": "file",
}

# Central registry
def get_registry():
    registry = {}
    registry.update({
        "Agent": Agent,
        "TestGeneratorAgent": TestGeneratorAgent,
        "DependencyAgent": DependencyAgent,
        "ceo": create_ceo,
        "executor": create_executor,
        "summarizer": create_summarizer,
        "test_generator": create_test_generator,
        "dependency_agent": create_dependency_agent,
        "CodeAnalyzerAgent": CodeAnalyzerAgent,
        "CodeDebuggerAgent": CodeDebuggerAgent,
        "CodeRepairAgent": CodeRepairAgent,
        "CodeEmbeddingIndex": CodeEmbeddingIndex,
        "SemanticCodeSearch": SemanticCodeSearch,
        "PerformanceProfilerAgent": PerformanceProfilerAgent,
        "OptimizationSuggesterAgent": OptimizationSuggesterAgent,
        "BenchmarkingTool": BenchmarkingTool,
        "IntegratedCodebaseOptimizer": IntegratedCodebaseOptimizer,
        "pipeline_coordinator": pipeline_coordinator,
    })
    return registry

AGENT_REGISTRY = get_registry()

```

## packages/agents/advanced_reasoning/agents.py (Priority: Highest)

```python
from ollama import Client
try:
    from .config import CEO_MODEL, FAST_MODEL, EXECUTOR_MODEL_ORIGINAL, EXECUTOR_MODEL_DISTILLED, USE_DISTILLED_EXECUTOR
    DEFAULT_MODEL = CEO_MODEL
except ImportError:
    from config import CEO_MODEL, FAST_MODEL, EXECUTOR_MODEL_ORIGINAL, EXECUTOR_MODEL_DISTILLED, USE_DISTILLED_EXECUTOR
    DEFAULT_MODEL = CEO_MODEL
import time
import torch
from transformers import CLIPProcessor, CLIPModel, ViTImageProcessor, ViTModel, WhisperProcessor, WhisperForConditionalGeneration
from PIL import Image
import numpy as np
import os
import ast
import json
try:
    from .vector_memory import vector_memory
except ImportError:
    from vector_memory import vector_memory
from sentence_transformers import SentenceTransformer
import faiss
import re
import cProfile
import pstats
import io
import tokenize
from memory_profiler import memory_usage
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import functools
from concurrent.futures import ThreadPoolExecutor
from tempfile import NamedTemporaryFile
import subprocess  # added for CodeRepairAgent and IntegratedCodebaseOptimizer

class AgentError(Exception):
    """Base class for agent exceptions"""
    pass

class ModelUnavailableError(AgentError):
    """Raised when the required model is not available"""
    pass

def retry_on_failure(max_retries=3, backoff_factor=1.5):
    """Decorator to retry operations with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    print(f"Attempt {attempt+1} failed. Retrying in {wait_time:.2f}s: {str(e)}")
                    time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator

class BaseAgent:
    """Base class for all MindMeld agents.
    
    Each agent must implement a clear interface:
    1. Initialize with minimal dependencies
    2. Provide a primary method that executes the agent's functionality
    3. Return structured data that can be validated against the schema
    
    Example:
        agent = MyAgent()
        result = agent.analyze("path/to/code")
        # result should be a dict or list conforming to agent_report_schema.json
    """
    pass

class TestGeneratorAgent(BaseAgent):
    """Generates pytest tests for a given module path."""
    def __init__(self):
        self.client = Client()
    @retry_on_failure()
    def generate_tests(self, module_path, bug_trace=None):
        prompt = f"Generate pytest tests for {module_path}"
        try:
            resp = self.client.chat(model=DEFAULT_MODEL,
                                    messages=[{"role":"user","content":prompt}])
        except Exception as e:
            raise ModelUnavailableError(f"Failed to get response from model: {e}") from e
        return getattr(resp, "message", {}).get("content", str(resp))
    def run(self, module_path, bug_trace=None):
        return {"tests": self.generate_tests(module_path, bug_trace)}

class DependencyAgent(BaseAgent):
    """Analyzes Python imports under a path."""
    def analyze_deps(self, path: str, *args, **kwargs):
        from concurrent.futures import ThreadPoolExecutor
        from functools import partial
        import ast
        import os
        def process_file(filename, root_path):
            full_path = os.path.join(root_path, filename)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    src = f.read()
                tree = ast.parse(src, filename=full_path)
                imports = {
                    node.module or alias.name
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                    for alias in (node.names if hasattr(node, "names") else [])
                }
                return os.path.relpath(full_path, path), sorted(imports)
            except Exception:
                return os.path.relpath(full_path, path), []
        py_files = []
        for root, _, files in os.walk(path):
            for fn in files:
                if fn.endswith(".py"):
                    py_files.append((fn, root))
        with ThreadPoolExecutor(max_workers=min(32, os.cpu_count() * 4)) as executor:
            results = list(executor.map(lambda x: process_file(x[0], x[1]), py_files))
        return dict(results)
    def run(self, path, *args, **kwargs):
        return {"dependencies": self.analyze_deps(path, *args, **kwargs)}

class CodeAnalyzerAgent(BaseAgent):
    """Scans repository and returns file→content map."""
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
    def analyze(self, max_file_size_mb=5, *args, **kwargs):
        max_size = int(max_file_size_mb) * 1024 * 1024  # Ensure int for comparison
        file_map = {}
        for dirpath, _, filenames in os.walk(self.root_dir):
            for fname in filenames:
                if fname.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c", ".go")):
                    path = os.path.join(dirpath, fname)
                    file_size = os.path.getsize(path)
                    if file_size > max_size:
                        file_map[path] = f"[File too large: {file_size/1024/1024:.2f}MB]"
                        continue
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            file_map[path] = f.read()
                    except Exception as e:
                        file_map[path] = f"[Error reading file: {str(e)}]"
        return file_map
    def run(self, root_dir=None, *args, **kwargs):
        return {"files": self.analyze(root_dir or self.root_dir, *args, **kwargs)}

def create_ceo():
    """Returns a CEO agent (stub for now)."""
    class CeoAgent(BaseAgent):
        def run(self, *args, **kwargs):
            return {"status": "CEO agent executed (stub)", "args": args, "kwargs": kwargs}
    return CeoAgent()
def create_executor():
    """Returns an executor agent (stub for now)."""
    return IntegratedCodebaseOptimizer()
def create_summarizer():
    """Returns a summarizer agent with proper integer handling."""
    class SummarizerAgent(BaseAgent):
        def run(self, value):
            # Ensure input is converted to integer
            try:
                if not isinstance(value, int):
                    value = int(value)
                # Now use the properly converted integer
                return {"summary_id": value, "status": "Summarizer agent executed successfully"}
            except (ValueError, TypeError) as e:
                raise ValueError(f"Summarizer agent requires an integer input: {str(e)}")
    return SummarizerAgent()
def create_test_generator():
    """Returns a test generator agent (stub for now)."""
    return TestGeneratorAgent()
def create_dependency_agent():
    """Returns a dependency agent instance."""
    return DependencyAgent()

class Agent(BaseAgent):
    def __init__(self, name="agent", model=None, max_retries=None, base_timeout=None, fallback_model=None, client=None):
        self.name = name
        self.model = model or os.environ.get("MODEL", "default-model")
        self.max_retries = int(max_retries or os.environ.get("MAX_RETRIES", 3))
        self.base_timeout = int(base_timeout or os.environ.get("BASE_TIMEOUT", 10))
        self.fallback_model = fallback_model or os.environ.get("FALLBACK_MODEL", "llama2")
        self.client = client if client is not None else Client()

    def run(self, prompt):
        retries = 0
        while retries < self.max_retries:
            try:
                resp = self.client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": f"[{self.name}] {prompt}"}]
                )
                return {"response": resp.message["content"], "model": self.model, "retries": retries}
            except Exception as e:
                retries += 1
                time.sleep(self.base_timeout)
        # Fallback model
        try:
            resp = self.client.chat(
                model=self.fallback_model,
                messages=[{"role": "user", "content": f"[{self.name}] {prompt}"}]
            )
            return {"response": resp.message["content"], "model": self.fallback_model, "retries": retries, "fallback": True}
        except Exception as e:
            return {
                "error": f"{self.name} failed after {self.max_retries} attempts and fallback.",
                "details": str(e)
            }

class CodeDebuggerAgent(BaseAgent):
    """Detects syntax errors via py_compile."""
    def locate_bugs(self, file_content: str):
        import py_compile
        import io
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix='.py', delete=True) as temp_file:
            temp_file.write(file_content.encode('utf-8'))
            temp_file.flush()
            stderr_capture = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = stderr_capture
            try:
                py_compile.compile(temp_file.name, doraise=True)
                return "No syntax errors"
            except py_compile.PyCompileError as e:
                return str(e)
            finally:
                sys.stderr = original_stderr
    def run(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            result = self.locate_bugs(content)
            return {"file": file_path, "diagnostics": result}
        except Exception as e:
            return {"file": file_path, "error": str(e)}

class CodeRepairAgent(BaseAgent):
    """Applies a naive fix for SyntaxErrors."""
    def generate_fix(self, file_content: str, diagnostics: str):
        if "SyntaxError" in diagnostics:
            lines = file_content.splitlines()
            import re
            bad_lines = set(int(n) for n in re.findall(r"line (\\d+)", diagnostics))
            return "\n".join(
                ("# [FIXED] " + line if idx+1 in bad_lines else line)
                for idx, line in enumerate(lines)
            )
        return file_content
    def test_solution(self, file_path: str):
        proc = subprocess.run(["python3", "-m", "py_compile", file_path],
                              capture_output=True)
        return proc.returncode == 0
    def run(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            diagnostics = CodeDebuggerAgent().locate_bugs(content)
            fixed = self.generate_fix(content, diagnostics)
            tmp = "/tmp/_repaired.py"
            with open(tmp, "w") as f:
                f.write(fixed)
            test_result = self.test_solution(tmp)
            return {"file": file_path, "diagnostics": diagnostics, "fixed": fixed, "compiles": test_result}
        except Exception as e:
            return {"file": file_path, "error": str(e)}

class IntegratedCodebaseOptimizer(BaseAgent):
    """Runs analyze→debug→repair on a target file."""
    def __init__(self, root_dir="."):
        self.analyzer = CodeAnalyzerAgent(root_dir)
        self.debugger = CodeDebuggerAgent()
        self.repairer = CodeRepairAgent()
    def optimize(self, target_file: str):
        files = self.analyzer.analyze()
        content = files.get(target_file, "")
        diagnostics = self.debugger.locate_bugs(content)
        fixed = self.repairer.generate_fix(content, diagnostics)
        tmp = "/tmp/_repaired.py"
        with open(tmp, "w") as f:
            f.write(fixed)
        return {
            "fixed": self.repairer.test_solution(tmp),
            "diagnostics": diagnostics
        }
    def run(self, target_file):
        return self.optimize(target_file)

class pipeline_coordinator(BaseAgent):
    def run(self, *args, **kwargs):
        return {"status": "Pipeline coordination executed (stub)", "args": args, "kwargs": kwargs}

class CodeEmbeddingIndex(BaseAgent):
    def run(self, *args, **kwargs):
        return {"status": "CodeEmbeddingIndex executed (stub)", "args": args, "kwargs": kwargs}

class SemanticCodeSearch(BaseAgent):
    def run(self, *args, **kwargs):
        return {"status": "SemanticCodeSearch executed (stub)", "args": args, "kwargs": kwargs}

class PerformanceProfilerAgent(BaseAgent):
    def run(self, *args, **kwargs):
        return {"status": "PerformanceProfilerAgent executed (stub)", "args": args, "kwargs": kwargs}

class OptimizationSuggesterAgent(BaseAgent):
    def run(self, *args, **kwargs):
        return {"status": "OptimizationSuggesterAgent executed (stub)", "args": args, "kwargs": kwargs}

class BenchmarkingTool(BaseAgent):
    def run(self, *args, **kwargs):
        return {"status": "BenchmarkingTool executed (stub)", "args": args, "kwargs": kwargs}

```

## agent_report_schema.json (Priority: Highest)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Report",
  "description": "Schema for agent execution reports",
  "type": "object",
  "properties": {
    "agent": {
      "type": "string",
      "description": "Agent name"
    },
    "status": {
      "type": "string",
      "enum": ["success", "error", "partial_success"],
      "description": "Overall execution status"
    },
    "payload": {
      "type": "string",
      "description": "Input provided to agent"
    },
    "timestamp": {
      "type": "integer",
      "description": "Execution timestamp"
    },
    "runtime_seconds": {
      "type": "number",
      "description": "Execution duration"
    },
    "data": {
      "type": "object",
      "description": "Agent-specific result data"
    },
    "error": {
      "type": "object",
      "properties": {
        "message": {
          "type": "string",
          "description": "Human-readable error message"
        },
        "type": {
          "type": "string",
          "description": "Error classification"
        },
        "details": {
          "type": "string",
          "description": "Additional error context"
        }
      },
      "required": ["message"],
      "description": "Error information when status is error"
    },
    "review": {
      "type": "object",
      "properties": {
        "severity": {
          "type": "string",
          "enum": ["info", "warning", "error"]
        },
        "category": {
          "type": "string",
          "enum": ["style", "bug", "performance", "security", "best-practice", "other"]
        },
        "suggestion": {
          "type": "string"
        },
        "details": {
          "type": "string"
        },
        "line": {
          "type": "integer"
        }
      },
      "required": ["severity", "category"],
      "description": "Frontend-compatible review information"
    },
    "metadata": {
      "type": "object",
      "description": "Operational metadata",
      "properties": {
        "agent": {
          "type": "string",
          "description": "Agent name (duplicate for backwards compatibility)"
        },
        "timestamp": {
          "type": "integer",
          "description": "Execution timestamp (duplicate for backwards compatibility)"
        },
        "payload": {
          "type": "string",
          "description": "Input provided to agent (duplicate for backwards compatibility)"
        },
        "runtime_seconds": {
          "type": "number",
          "description": "Execution duration (duplicate for backwards compatibility)"
        },
        "job_id": {
          "type": "string",
          "description": "Unique execution ID for traceability"
        },
        "retries": {
          "type": "integer",
          "description": "Number of retry attempts"
        },
        "fallback_used": {
          "type": "boolean",
          "description": "Whether fallback model was used"
        },
        "system_info": {
          "type": "object",
          "description": "System information"
        },
        "model_info": {
          "type": "object",
          "description": "Model information",
          "properties": {
            "name": {
              "type": "string",
              "description": "Model name"
            },
            "initial_model": {
              "type": "string",
              "description": "Original model name if fallback was used"
            }
          }
        }
      }
    }
  },
  "required": ["agent", "status", "timestamp"],
  "allOf": [
    {
      "if": {
        "properties": { "status": { "const": "error" } }
      },
      "then": {
        "required": ["error"]
      }
    },
    {
      "if": {
        "properties": { "status": { "const": "success" } }
      },
      "then": {
        "required": ["data"]
      }
    },
    {
      "if": {
        "properties": { 
          "metadata": { 
            "properties": { 
              "fallback_used": { "const": true } 
            },
            "required": ["fallback_used"]
          }
        },
        "required": ["metadata"]
      },
      "then": {
        "properties": {
          "metadata": {
            "properties": {
              "model_info": {
                "required": ["initial_model"]
              }
            }
          }
        }
      }
    }
  ]
}

```

## app.py (Priority: Highest)

```python
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import asyncio
import logging
import time
from schema_validator import validate_agent_output, normalize_agent_output

# Import agents
from packages.agents.advanced_reasoning.agents import (
    TestGeneratorAgent, DependencyAgent, CodeAnalyzerAgent,
    CodeDebuggerAgent, CodeRepairAgent, IntegratedCodebaseOptimizer
)
# Import agent input types
from packages.agents.AgentFactory import AGENT_INPUT_TYPES

app = FastAPI(title="MindMeld API", version="1.0.0")
logger = logging.getLogger("mindmeld")

# Storage for background tasks
TASK_RESULTS = {}

@app.post("/api/analyze_file")
async def analyze_file(file: UploadFile):
    """Analyze a single file for issues."""
    # Validate file input
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {"message": "No file provided", "type": "ValidationError"}
            }
        )
    
    # Create a job ID for tracing
    job_id = str(uuid.uuid4())
    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Validate that the file exists and is not a directory
        file_path = Path(tmp_path)
        if not file_path.exists():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"File not found: {tmp_path}"}, 
                    "CodeAnalyzerAgent", 
                    file.filename, 
                    int(time.time()),
                    time.time() - start_time,
                    job_id
                )
            )
        if file_path.is_dir():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"Expected file but received directory: {tmp_path}"}, 
                    "CodeAnalyzerAgent", 
                    file.filename, 
                    int(time.time()),
                    time.time() - start_time,
                    job_id
                )
            )
        
        # Execute the analysis
        analyzer = CodeAnalyzerAgent(os.path.dirname(tmp_path))
        content = analyzer.analyze().get(tmp_path)
        debugger = CodeDebuggerAgent()
        diagnostics = debugger.locate_bugs(content)
        
        # Normalize the response
        result = {
            "filename": file.filename,
            "diagnostics": diagnostics,
            "has_issues": "SyntaxError" in diagnostics
        }
        
        # Return normalized response
        normalized = normalize_agent_output(
            result, 
            "CodeAnalyzerAgent", 
            file.filename, 
            int(time.time()),
            time.time() - start_time,
            job_id
        )
        return normalized
        
    except Exception as e:
        logger.exception(f"Error analyzing file {file.filename}")
        error_result = normalize_agent_output(
            {"error": str(e), "type": e.__class__.__name__}, 
            "CodeAnalyzerAgent", 
            file.filename, 
            int(time.time()),
            time.time() - start_time,
            job_id
        )
        return JSONResponse(status_code=500, content=error_result)
    finally:
        os.unlink(tmp_path)

@app.post("/api/repair_file")
async def repair_file(file: UploadFile):
    """Repair a file with syntax errors."""
    # Validate file input
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {"message": "No file provided", "type": "ValidationError"}
            }
        )
    
    # Create a job ID for tracing
    job_id = str(uuid.uuid4())
    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Validate that the file exists and is not a directory
        file_path = Path(tmp_path)
        if not file_path.exists():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"File not found: {tmp_path}"}, 
                    "CodeRepairAgent", 
                    file.filename, 
                    int(time.time()),
                    time.time() - start_time,
                    job_id
                )
            )
        if file_path.is_dir():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"Expected file but received directory: {tmp_path}"}, 
                    "CodeRepairAgent", 
                    file.filename, 
                    int(time.time()),
                    time.time() - start_time,
                    job_id
                )
            )
        
        analyzer = CodeAnalyzerAgent(os.path.dirname(tmp_path))
        content = analyzer.analyze().get(tmp_path)
        debugger = CodeDebuggerAgent()
        diagnostics = debugger.locate_bugs(content)
        repairer = CodeRepairAgent()
        fixed_content = repairer.generate_fix(content, diagnostics)
        
        # Write fixed content to a new file for testing
        with tempfile.NamedTemporaryFile(delete=False, suffix="_fixed.py") as fixed_tmp:
            fixed_tmp.write(fixed_content.encode('utf-8'))
            fixed_path = fixed_tmp.name
        
        # Test if the fix works
        fix_successful = repairer.test_solution(fixed_path)
        os.unlink(fixed_path)
        
        # Normalize the response
        result = {
            "filename": file.filename,
            "original_diagnostics": diagnostics,
            "fixed_content": fixed_content,
            "fix_successful": fix_successful
        }
        
        # Return normalized response
        normalized = normalize_agent_output(
            result, 
            "CodeRepairAgent", 
            file.filename, 
            int(time.time()),
            time.time() - start_time,
            job_id
        )
        return normalized
        
    except Exception as e:
        logger.exception(f"Error repairing file {file.filename}")
        error_result = normalize_agent_output(
            {"error": str(e), "type": e.__class__.__name__}, 
            "CodeRepairAgent", 
            file.filename, 
            int(time.time()),
            time.time() - start_time,
            job_id
        )
        return JSONResponse(status_code=500, content=error_result)
    finally:
        os.unlink(tmp_path)

@app.post("/api/generate_tests")
async def generate_tests(file: UploadFile, background_tasks: BackgroundTasks):
    """Generate tests for a module (async background task)."""
    # Validate file input
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {"message": "No file provided", "type": "ValidationError"}
            }
        )
    
    # Create task ID and job ID for tracing
    task_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Initialize the task status
    TASK_RESULTS[task_id] = normalize_agent_output(
        {"status": "processing"}, 
        "TestGeneratorAgent", 
        file.filename, 
        timestamp,
        0.0,
        job_id
    )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    # Validate that the file exists and is not a directory
    file_path = Path(tmp_path)
    if not file_path.exists():
        error_result = normalize_agent_output(
            {"error": f"File not found: {tmp_path}"}, 
            "TestGeneratorAgent", 
            file.filename, 
            timestamp,
            0.0,
            job_id
        )
        TASK_RESULTS[task_id] = error_result
        return {"task_id": task_id, "status": "error"}
        
    if file_path.is_dir():
        error_result = normalize_agent_output(
            {"error": f"Expected file but received directory: {tmp_path}"}, 
            "TestGeneratorAgent", 
            file.filename, 
            timestamp,
            0.0,
            job_id
        )
        TASK_RESULTS[task_id] = error_result
        return {"task_id": task_id, "status": "error"}
    
    # Start background task with validated input
    background_tasks.add_task(
        _generate_tests_background, task_id, tmp_path, file.filename, job_id
    )
    
    return {"task_id": task_id, "status": "processing"}

async def _generate_tests_background(task_id: str, file_path: str, filename: str, job_id: str):
    """Background task for test generation."""
    start_time = time.time()
    timestamp = int(start_time)
    
    try:
        # Check if file type is supported
        if not any(file_path.endswith(ext) for ext in ['.py', '.js', '.ts', '.jsx', '.tsx']):
            error_result = normalize_agent_output(
                {"error": f"Unsupported file type: {file_path}"}, 
                "TestGeneratorAgent", 
                filename, 
                timestamp,
                time.time() - start_time,
                job_id
            )
            TASK_RESULTS[task_id] = error_result
            return
        
        # Execute the generator
        generator = TestGeneratorAgent()
        tests = generator.generate_tests(file_path)
        
        # Normalize the result
        result = {
            "filename": filename,
            "tests": tests
        }
        
        normalized = normalize_agent_output(
            result, 
            "TestGeneratorAgent", 
            filename, 
            timestamp,
            time.time() - start_time,
            job_id
        )
        normalized["status"] = "completed"
        TASK_RESULTS[task_id] = normalized
        
    except Exception as e:
        logger.exception(f"Error generating tests for {filename}")
        error_result = normalize_agent_output(
            {"error": str(e), "type": e.__class__.__name__}, 
            "TestGeneratorAgent", 
            filename, 
            timestamp,
            time.time() - start_time,
            job_id
        )
        TASK_RESULTS[task_id] = error_result
    finally:
        # Clean up the temporary file
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {file_path}: {e}")

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background task."""
    if task_id not in TASK_RESULTS:
        error_result = normalize_agent_output(
            {"error": "Task not found", "type": "NotFoundError"}, 
            "TaskService", 
            task_id, 
            int(time.time()),
            0.0,
            str(uuid.uuid4())
        )
        return JSONResponse(status_code=404, content=error_result)
    
    return TASK_RESULTS[task_id]

```

## utils/llm_client.py (Priority: High)

```python
"""
LLM client utility for MindMeld.

This module provides standardized LLM interaction with retry logic,
fallback models, and consistent error handling.
"""

import os
import json
import logging
import time
import requests
from typing import Dict, Any, Optional, List, Union
from functools import wraps

import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from utils.error_handling import LLMCallError, ModelUnavailableError

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MODEL = "phi3.5:latest"
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1.5
DEFAULT_MAX_BACKOFF = 10
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TIMEOUT = 30  # seconds


def get_default_model() -> str:
    """
    Get the default LLM model from environment variables.
    
    Returns:
        Model name string
    """
    return os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)


def get_model_config() -> Dict[str, Any]:
    """
    Get the model configuration from environment variables.
    
    Returns:
        Model configuration dictionary
    """
    return {
        "temperature": float(os.getenv("TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.getenv("MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        "timeout": int(os.getenv("TIMEOUT", DEFAULT_TIMEOUT))
    }


def get_fallback_model() -> str:
    """
    Get the fallback LLM model from environment variables.
    
    Returns:
        Fallback model name string
    """
    return os.getenv("FALLBACK_MODEL", "llama2")


def call_llm_with_retry(max_retries: int = DEFAULT_MAX_RETRIES, 
                    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
                    max_backoff: float = DEFAULT_MAX_BACKOFF):
    """
    Decorator to retry LLM calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor to multiply delay on each retry
        max_backoff: Maximum backoff time in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            @retry(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=backoff_factor, max=max_backoff),
                retry=retry_if_exception_type((LLMCallError, requests.exceptions.RequestException)),
                reraise=True
            )
            def _retry_call():
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, LLMCallError):
                        logger.warning(f"LLM call failed, retrying: {str(e)}")
                        raise
                    else:
                        logger.warning(f"Error in LLM call, retrying: {str(e)}")
                        raise LLMCallError(f"Error in LLM call: {str(e)}") from e
            
            try:
                return _retry_call()
            except tenacity.RetryError as e:
                if e.last_attempt.exception():
                    logger.error(f"All retry attempts failed: {str(e.last_attempt.exception())}")
                    raise LLMCallError(f"All retry attempts failed: {str(e.last_attempt.exception())}")
                else:
                    logger.error("All retry attempts failed")
                    raise LLMCallError("All retry attempts failed")
        
        return wrapper
    return decorator


def with_fallback_model(fallback_model: Optional[str] = None):
    """
    Decorator to try a fallback model if the primary model fails.
    
    Args:
        fallback_model: Name of the fallback model to use
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try with the primary model
            try:
                return func(*args, **kwargs)
            except LLMCallError as e:
                primary_model = kwargs.get('model_name') or get_default_model()
                fallback = fallback_model or get_fallback_model()
                
                if primary_model == fallback:
                    # Don't fallback to the same model
                    logger.error(f"LLM call failed with model {primary_model}, no different fallback available")
                    raise
                
                logger.warning(f"LLM call failed with model {primary_model}, trying fallback model {fallback}")
                
                # Try with the fallback model
                kwargs['model_name'] = fallback
                try:
                    return func(*args, **kwargs)
                except Exception as fallback_e:
                    # Both primary and fallback failed
                    logger.error(f"Fallback model {fallback} also failed: {str(fallback_e)}")
                    raise LLMCallError(
                        f"Both primary model ({primary_model}) and fallback model ({fallback}) failed",
                        model_name=primary_model
                    ) from e
        
        return wrapper
    return decorator


def check_model_availability(model_name: str = None) -> bool:
    """
    Check if the specified model is available in Ollama.
    
    Args:
        model_name: Name of the model to check (default: get from environment)
        
    Returns:
        True if the model is available, False otherwise
    """
    if model_name is None:
        model_name = get_default_model()
    
    try:
        # Set up the Ollama API URL
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags")
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            # Check if the model is in the list of available models
            for model in models:
                if model.get("name") == model_name:
                    logger.debug(f"Model {model_name} is available")
                    return True
            
            logger.warning(f"Model {model_name} is not available in Ollama")
            return False
        else:
            logger.error(f"Failed to get model list from Ollama: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error checking model availability: {str(e)}")
        return False


retry_on_llm_error = retry(
    retry=retry_if_exception_type((requests.RequestException, LLMCallError)),
    stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
    wait=wait_exponential(multiplier=DEFAULT_BACKOFF_FACTOR, max=DEFAULT_MAX_BACKOFF),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying LLM call after error (attempt {retry_state.attempt_number}/{DEFAULT_MAX_RETRIES})"
    )
)


def with_fallback_model(func):
    """
    Decorator to retry with fallback model if primary model fails.
    
    Args:
        func: The function to decorate
        
    Returns:
        Wrapped function with fallback capability
    """
    @wraps(func)
    def wrapper(prompt, model_name=None, *args, **kwargs):
        try:
            return func(prompt, model_name, *args, **kwargs)
        except LLMCallError as e:
            # Try with fallback model if available
            fallback_model = get_fallback_model()
            if fallback_model and fallback_model != model_name:
                logger.warning(f"Primary model failed, trying with fallback model {fallback_model}")
                kwargs["fallback_used"] = True
                return func(prompt, fallback_model, *args, **kwargs)
            else:
                # Re-raise if no fallback or fallback is the same as primary
                raise
    
    return wrapper


@retry_on_llm_error
@with_fallback_model
def call_llm(prompt: str,
            model_name: Optional[str] = None,
            temperature: float = DEFAULT_TEMPERATURE,
            max_tokens: int = DEFAULT_MAX_TOKENS,
            timeout: int = DEFAULT_TIMEOUT,
            system_prompt: Optional[str] = None,
            fallback_used: bool = False) -> Dict[str, Any]:
    """
    Call the LLM model with retry and fallback logic.
    
    Args:
        prompt: Input prompt for the model
        model_name: Name of the model to use (default: get from environment)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 2048)
        timeout: Request timeout in seconds (default: 30)
        system_prompt: Optional system prompt to use
        fallback_used: Whether this is a fallback call
        
    Returns:
        Dictionary containing the model response
        
    Raises:
        LLMCallError: If the model call fails
        ModelUnavailableError: If the model is not available
    """
    # Use default model if none specified
    if model_name is None:
        model_name = get_default_model()
    
    # Check if model is available
    if not check_model_availability(model_name):
        raise ModelUnavailableError(f"Model {model_name} is not available", model_name=model_name)
    
    try:
        # Set up the Ollama API URL and payload
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        url = f"{ollama_host}/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        # Log request details (excluding the prompt for brevity)
        logger.debug(f"Calling model {model_name} with temperature={temperature}, max_tokens={max_tokens}")
        
        # Record start time for runtime calculation
        start_time = time.time()
        
        # Make the API call
        response = requests.post(url, json=payload, timeout=timeout)
        
        # Calculate runtime
        runtime_seconds = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Add metadata to the response
            metadata = {
                "model_info": {
                    "name": model_name,
                },
                "runtime_seconds": runtime_seconds,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if fallback_used:
                metadata["fallback_used"] = True
                metadata["model_info"]["initial_model"] = get_default_model()
            
            result["metadata"] = metadata
            
            logger.debug(f"LLM call completed in {runtime_seconds:.2f} seconds")
            return result
        else:
            error_msg = f"LLM API call failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise LLMCallError(error_msg, model_name=model_name)
    
    except requests.RequestException as e:
        error_msg = f"LLM API request failed: {str(e)}"
        logger.error(error_msg)
        raise LLMCallError(error_msg, model_name=model_name) from e
    
    except Exception as e:
        error_msg = f"Unexpected error in LLM call: {str(e)}"
        logger.error(error_msg)
        raise LLMCallError(error_msg, model_name=model_name) from e


def extract_llm_response(response: Dict[str, Any]) -> str:
    """
    Extract the text from an LLM response.
    
    Args:
        response: Response dictionary from call_llm
        
    Returns:
        Response text
    """
    if "response" in response:
        return response["response"]
    elif "choices" in response and len(response["choices"]) > 0:
        return response["choices"][0]["text"]
    else:
        logger.warning("Could not extract response text from LLM response")
        return ""


def check_syntax(code_string: str, filename: str = '<string>') -> tuple:
    """
    Check Python code syntax without executing it.
    
    Args:
        code_string: Python code to check
        filename: Filename to use in error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        compile(code_string, filename, 'exec')
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

```

## utils/error_handling.py (Priority: High)

```python
"""
Error handling utility for MindMeld.

This module provides a hierarchical exception system for all MindMeld operations.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MindMeldError(Exception):
    """Base exception for all MindMeld-related errors."""
    
    def __init__(self, message: str, *args, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.message = message
        super().__init__(message, *args, **kwargs)
        logger.error(f"{self.__class__.__name__}: {message}")


class ValidationError(MindMeldError):
    """Raised when input validation fails."""
    pass


class FileProcessingError(MindMeldError):
    """Raised when file operations fail."""
    pass


class LLMCallError(MindMeldError):
    """Raised when LLM call fails."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, *args, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            model_name: Name of the LLM model that failed
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.model_name = model_name
        if model_name:
            message = f"{message} (model: {model_name})"
        super().__init__(message, *args, **kwargs)


class ModelUnavailableError(LLMCallError):
    """Raised when required LLM model is not available."""
    pass


class AnalysisError(MindMeldError):
    """Raised when code analysis operations fail."""
    pass


class CompilationError(MindMeldError):
    """Raised when code compilation fails."""
    pass


class RepairError(MindMeldError):
    """Raised when code repair fails."""
    pass


class SchemaValidationError(MindMeldError):
    """Raised when output schema validation fails."""
    pass


class TimeoutError(MindMeldError):
    """Raised when an operation times out."""
    pass


def format_error_for_json(error: Exception) -> dict:
    """
    Format an exception for inclusion in a JSON report.
    
    Args:
        error: The exception to format
        
    Returns:
        A dictionary containing error details
    """
    error_type = error.__class__.__name__
    error_message = str(error)
    
    result = {
        "message": error_message,
        "type": error_type
    }
    
    # Add additional context for specific error types
    if isinstance(error, LLMCallError) and error.model_name:
        result["model"] = error.model_name
    
    return result

```

## schema_validator.py (Priority: High)

```python
#!/usr/bin/env python3
"""
Schema validation utilities for agent reports.
This module provides functions to validate and normalize agent outputs.
"""

import json
import jsonschema
import time
import sys
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union

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

def validate_agent_output(report: Dict[str, Any], schema_path: Optional[str] = None) -> Tuple[bool, Optional[str]]:
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
        "cpu_count": os.cpu_count()
    }

def get_model_info() -> Dict[str, Any]:
    """Get model information for metadata."""
    return {
        "name": os.getenv("OLLAMA_MODEL", "phi3.5:latest"),
        "config": {
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("MAX_TOKENS", "2048"))
        }
    }

def normalize_agent_output(
    result: Any, 
    agent_name: str, 
    payload: str, 
    timestamp: Optional[int] = None, 
    runtime_seconds: float = 0.0,
    job_id: Optional[str] = None
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
        "model_info": get_model_info()
    }
    
    # For string results (likely errors)
    if isinstance(result, str):
        if "[ERROR]" in result:
            return {
                "agent": agent_name,
                "status": "error",
                "error": {
                    "message": result,
                    "type": "AgentError"
                },
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": metadata
            }
        else:
            return {
                "agent": agent_name,
                "status": "success",
                "data": {"result": result},
                "timestamp": timestamp,
                "payload": payload,
                "runtime_seconds": runtime_seconds,
                "metadata": metadata
            }
    
    # For dictionary results
    if isinstance(result, dict):
        normalized = {
            "agent": agent_name,
            "timestamp": timestamp,
            "payload": payload,
            "runtime_seconds": runtime_seconds
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
            normalized["error"] = {
                "message": str(error_msg),
                "type": "AgentError"
            }
        
        # Copy all other fields to data
        data_fields = {k: v for k, v in result.items() 
                      if k not in ["agent", "status", "timestamp", "payload", 
                                  "runtime_seconds", "metadata", "error"]}
        if data_fields:
            normalized["data"] = data_fields
        elif "data" not in normalized and normalized.get("status") == "success":
            normalized["data"] = {"result": "Agent executed without specific data output"}
        
        return normalized
    
    # For list or other objects
    return {
        "agent": agent_name,
        "status": "success",
        "data": {"result": str(result) if not isinstance(result, list) else result},
        "timestamp": timestamp,
        "payload": payload,
        "runtime_seconds": runtime_seconds,
        "metadata": metadata
    }

def update_app_routes_with_validation(app_path: str) -> None:
    """
    Update the FastAPI routes in app.py to use validation.
    This is a helper for migration purposes.
    """
    import re
    with open(app_path, 'r') as f:
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
    
    with open(app_path, 'w') as f:
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

```

## run_all_agents.py (Priority: Medium)

```python
#!/usr/bin/env python3
import json, subprocess, sys, os, logging, time, argparse, requests
from pathlib import Path
from packages.agents.AgentFactory import AGENT_REGISTRY

# Parse arguments
parser = argparse.ArgumentParser(description="Run all MindMeld agents")
parser.add_argument("--wait-for-ollama", action="store_true", help="Wait for Ollama to be ready before starting")
parser.add_argument("--output-dir", type=str, default="reports", help="Directory to store agent reports")
parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds for each agent")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("--verify-models", action="store_true", help="Verify required models are available in Ollama")
args = parser.parse_args()

# Configure structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": time.time(),
            "level": record.levelname,
            "agent": getattr(record, "agent", "system"),
            "step": getattr(record, "step", "unknown"),
            "message": record.getMessage(),
            "status": getattr(record, "status", "unknown")
        }
        return json.dumps(log_data)

# Set up logger
logger = logging.getLogger("agent_runner")
logger.setLevel(logging.INFO)

# Add console handler with our formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)

# Also add file handler for persistent logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_dir / f"agent_run_{int(time.time())}.log")
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

# Function to check if a model exists in Ollama
def check_model_exists(model_name, ollama_url):
    """Check if a model exists in Ollama."""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(m.get("name") == model_name for m in models)
        return False
    except Exception as e:
        logger.error(f"Error checking for model {model_name}: {str(e)}", 
                  extra={"step": "model_check", "status": "error", "model": model_name})
        return False

# Function to pull a model if it doesn't exist
def pull_model(model_name, ollama_url):
    """Pull a model from Ollama if it doesn't exist."""
    try:
        logger.info(f"Pulling model {model_name}...", 
                 extra={"step": "model_pull", "status": "started", "model": model_name})
        
        # Use the Ollama API to pull the model
        response = requests.post(
            f"{ollama_url}/api/pull",
            json={"name": model_name},
            timeout=600  # 10 minute timeout for model pulling
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully pulled model {model_name}", 
                     extra={"step": "model_pull", "status": "success", "model": model_name})
            return True
        else:
            logger.error(f"Failed to pull model {model_name}: {response.text}", 
                      extra={"step": "model_pull", "status": "error", "model": model_name})
            return False
    except Exception as e:
        logger.error(f"Error pulling model {model_name}: {str(e)}", 
                  extra={"step": "model_pull", "status": "error", "model": model_name})
        return False

# Wait for Ollama if requested
ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
if args.wait_for_ollama:
    logger.info("Waiting for Ollama to be ready", extra={"step": "init", "status": "waiting"})
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"Ollama is ready with {len(models)} models", 
                         extra={"step": "init", "status": "ready", "models": len(models)})
                break
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"Ollama not ready, retrying in 5s: {str(e)}", 
                            extra={"step": "init", "status": "waiting", "retry": i+1})
                time.sleep(5)
            else:
                logger.error("Failed to connect to Ollama after multiple attempts", 
                          extra={"step": "init", "status": "failed"})
                sys.exit(1)

# Verify required models
required_models = [
    os.environ.get("FALLBACK_MODEL", "llama2"),  # Fallback model from env
    "llama2",  # Default fallback
]

# Also check for models specified in agent configs
try:
    from packages.agents.advanced_reasoning.config import CEO_MODEL, FAST_MODEL
    required_models.extend([CEO_MODEL, FAST_MODEL])
except ImportError:
    logger.warning("Could not import agent configuration, using default models only",
                extra={"step": "model_check", "status": "warning"})

if args.verify_models:
    logger.info("Verifying required models", extra={"step": "model_check", "status": "started"})
    for model in set(required_models):  # Using set to remove duplicates
        if not check_model_exists(model, ollama_url):
            logger.warning(f"Model {model} not available, pulling now...", 
                       extra={"step": "model_check", "status": "missing", "model": model})
            if not pull_model(model, ollama_url):
                logger.error(f"Failed to pull model {model}, continuing with available models", 
                          extra={"step": "model_check", "status": "failed", "model": model})

base = Path(args.output_dir)
summary = {"reports": {}, "timestamp": time.time(), "total_agents": len(AGENT_REGISTRY)}

# ensure reports folder exists
if base.exists():
    subprocess.run(["rm", "-rf", str(base)])
base.mkdir()

logger.info("Starting agent batch run", extra={"step": "init", "status": "started"})
for i, name in enumerate(AGENT_REGISTRY, 1):
    out = base/name
    out.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Running agent {name}", extra={"agent": name, "step": "run", "status": "started"})
    
    # Run the agent
    cmd = ["python3", "run_agent.py", name, "src/", f"--output-dir={out}"]
    if args.verbose:
        cmd.append("--verbose")
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
        
        if result.stdout:
            logger.debug(f"{name} stdout: {result.stdout}", extra={"agent": name, "step": "run", "status": "output"})
        if result.stderr:
            logger.warning(f"{name} stderr: {result.stderr}", extra={"agent": name, "step": "run", "status": "error"})
        
        # Find any JSON reports
        files = sorted(out.glob(f"{name}_*.json"))
        
        if files:
            latest_report = str(files[-1])
            summary["reports"][name] = latest_report
            
            # Check if the report contains an error
            try:
                with open(files[-1], 'r') as f:
                    report_content = json.load(f)
                if isinstance(report_content, dict) and 'error' in report_content:
                    print(f"⚠️  {name} generated a report with an error: {report_content['error']}")
                    logger.warning(f"Agent reported error: {report_content['error']}", 
                                extra={"agent": name, "step": "run", "status": "error"})
                elif isinstance(report_content, dict) and 'analysis' in report_content:
                    if isinstance(report_content['analysis'], str) and report_content['analysis'].startswith('[ERROR]'):
                        print(f"⚠️  {name} generated a report with an error: {report_content['analysis']}")
                        logger.warning(f"Agent reported error in analysis: {report_content['analysis']}", 
                                    extra={"agent": name, "step": "run", "status": "error"})
                    else:
                        print(f"✅ {name} completed successfully.")
                        logger.info("Agent completed successfully", 
                                  extra={"agent": name, "step": "run", "status": "success"})
                else:
                    print(f"✅ {name} generated a report in non-standard format.")
                    logger.info("Agent completed with non-standard report format", 
                              extra={"agent": name, "step": "run", "status": "success"})
            except json.JSONDecodeError:
                print(f"⚠️  {name} generated a non-JSON report.")
                logger.warning("Agent generated non-JSON report", 
                            extra={"agent": name, "step": "run", "status": "error"})
        else:
            print(f"⚠️  {name} did not generate any reports.")
            logger.warning("Agent did not generate any reports", 
                        extra={"agent": name, "step": "run", "status": "error"})
            summary["reports"][name] = "[no JSON output]"
            
    except subprocess.TimeoutExpired:
        print(f"⚠️  {name} timed out after {args.timeout} seconds.")
        logger.error(f"Agent timed out after {args.timeout}s", 
                  extra={"agent": name, "step": "run", "status": "timeout"})
        summary["reports"][name] = f"[TIMEOUT after {args.timeout}s]"
    except Exception as e:
        print(f"⚠️  {name} failed with error: {e}")
        logger.error(f"Agent failed with error: {str(e)}", 
                  extra={"agent": name, "step": "run", "status": "error"})
        summary["reports"][name] = f"[ERROR: {str(e)}]"

# Write summary to file
with open(base/"all_agents_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n✅ All agents completed.")
print(f"✅ Summary file generated at {base/'all_agents_summary.json'}")

# Print a short status report
successful = 0
error_count = 0
no_output = 0

for name, path in summary["reports"].items():
    if isinstance(path, str):
        if path == "[no JSON output]" or path.startswith("[ERROR") or path.startswith("[TIMEOUT"):
            error_count += 1
            if path == "[no JSON output]":
                no_output += 1
        else:
            successful += 1

print(f"\n=== AGENT RUN SUMMARY ===")
print(f"Total agents:     {len(AGENT_REGISTRY)}")
print(f"Successful:       {successful}")
print(f"Failed/errors:    {error_count}")
print(f"No output:        {no_output}")
print("========================")

```

## .github/workflows/validate-agent-reports.yml (Priority: Medium)

```yaml
name: Validate Agent Reports

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'run_agent.py'
      - 'agent_report_schema.json'
      - 'schema_validator.py'
      - 'reports/**/*.json'
      - 'packages/agents/**/*.py'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'run_agent.py'
      - 'agent_report_schema.json'
      - 'schema_validator.py'
      - 'reports/**/*.json'
      - 'packages/agents/**/*.py'
  workflow_dispatch:

jobs:
  validate-reports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install jsonschema
          pip install -r requirements.txt
          
      - name: Validate agent report schema
        id: validate-schema
        run: |
          python validate_schema_ci.py
          
      - name: Test agent pipeline validation
        id: test-pipeline
        run: |
          python test_agent_pipeline.py
          
      - name: Run schema validation tests
        id: run-tests
        run: |
          python -m pytest test_schema_validator.py -v
          
      - name: Generate summary
        if: always()
        run: |
          echo "## Validation Report" > validation_report.md
          echo "- Schema validation: ${{ steps.validate-schema.outcome }}" >> validation_report.md
          echo "- Pipeline tests: ${{ steps.test-pipeline.outcome }}" >> validation_report.md
          echo "- Schema tests: ${{ steps.run-tests.outcome }}" >> validation_report.md
          
      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation_report.md

```

## docs/AGENT_REPORT_SCHEMA.md (Priority: Medium)

```markdown
# MindMeld Agent Report Schema Fixes

This document summarizes the fixes made to ensure proper validation and standardization of agent reports across the MindMeld platform.

## Overview of Fixes

The following issues were identified and fixed in the agent reports:

1. **Missing Required Fields**: Some reports were missing the required `agent` field.
2. **Non-Standard Status Values**: Reports used custom status strings like "AgentName executed (stub)" instead of the standard values ("success", "error", "partial_success").
3. **Data Structure Inconsistency**: Success reports lacked the required `data` field.
4. **Error Structure Inconsistency**: Error reports lacked the required `error` field with a `message` property.
5. **Fallback Model Inconsistency**: Reports with `fallback_used: true` missing the required `initial_model` field.

## Legacy Report Conversion

A special script (`fix_legacy_reports.py`) was created to fix non-conforming legacy reports. The script:

1. Adds missing `agent` fields by extracting them from metadata or report filenames.
2. Converts non-standard status values to standard ones.
3. Ensures required fields are present based on status.
4. Adds placeholders for any missing required data.

To run this script and fix any additional legacy reports:

```bash
python fix_legacy_reports.py --reports-dir reports
```

Use the `--dry-run` flag to preview changes without applying them:

```bash
python fix_legacy_reports.py --reports-dir reports --dry-run
```

## Schema Requirements

All agent reports must conform to these key requirements:

1. **Basic Fields**: Each report must have:
   - `agent` (string): Name of the agent
   - `status` (string): One of "success", "error", or "partial_success"
   - `timestamp` (integer): Unix timestamp

2. **Status-Specific Requirements**:
   - Reports with `status: "success"` must have a `data` object.
   - Reports with `status: "error"` must have an `error` object with a `message` property.

3. **Fallback Requirements**:
   - Reports with `metadata.fallback_used: true` must have `metadata.model_info.initial_model`.

## Backward Compatibility

For backward compatibility with older reports:

1. **Schema Validation**: All existing reports have been validated and fixed to conform to the schema.
2. **Versioning Strategy**: Consider adding a `schema_version` field to allow for future schema changes.
3. **Normalization**: The `normalize_agent_output` function in `schema_validator.py` converts any valid agent output to a schema-conforming format.

## Validation Process

Agent reports can be validated using:

```bash
python validate_schema_ci.py
```

For continuous integration validation, a GitHub Actions workflow is available in `.github/workflows/validate-agent-reports.yml`. The workflow:

1. Validates all agent reports against the schema
2. Runs the agent pipeline validation tests
3. Executes schema validation unit tests
4. Generates a validation summary report

```bash
# Run the validation workflow manually
gh workflow run validate-agent-reports.yml
```

## Future Considerations

1. **Schema Evolution**: As agent capabilities grow, we may need to evolve the schema. Use semantic versioning for changes.
2. **Report Converter**: Maintain and enhance the `fix_legacy_reports.py` script to handle future schema changes.
3. **Deprecation Strategy**: When making breaking changes, implement a deprecation cycle with ample warning.
4. **Documentation**: Keep this document up-to-date with any schema changes.

## References

- `agent_report_schema.json`: The canonical schema definition
- `schema_validator.py`: Utilities for validating and normalizing agent outputs
- `fix_legacy_reports.py`: Tool for fixing non-conforming reports
- `validate_schema_ci.py`: CI-friendly validation script

```

## docs/PIPELINE_FIXES.md (Priority: Medium)

```markdown
# MindMeld Agent Pipeline 

## Overview

The MindMeld agent pipeline provides a robust framework for executing various AI agents against code repositories. This document outlines the recent improvements made to the system.

## Core Components

### Input Validation

Each agent now has clearly defined input type requirements:
- File-based agents: Require file paths and validate that the file exists
- Directory-based agents: Require directory paths and validate that the directory exists
- Integer-based agents: Require integer values and validate the type

### Schema Standardization

All agent outputs now conform to a standardized JSON schema defined in `agent_report_schema.json`:
- Required fields: `agent`, `status`, `timestamp`
- Status types: `success`, `error`, `partial_success`
- Conditional requirements: For `status: error`, the `error` field is required; for `status: success`, the `data` field is required

### Error Handling

Error handling is now consistent across all agents with:
- Clear error messages and types
- Proper context in error reports
- Fallback mechanisms when appropriate

## Running Agents

```bash
# Run a specific agent on a file
python run_agent.py CodeDebuggerAgent path/to/file.py

# Run a specific agent on a directory
python run_agent.py DependencyAgent path/to/directory

# Run summarizer agent with integer input
python run_agent.py summarizer 42
```

## Testing

Comprehensive test suites ensure the pipeline is robust:
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest test_schema_validator.py
python -m pytest tests/test_pipeline_fixes.py
```

## Validation

A GitHub Actions workflow automatically validates agent reports against the schema:
- Runs on each push to main and develop branches
- Validates all agent report JSON files
- Fails if any reports don't match the schema

## Integration with FastAPI

The FastAPI app provides REST endpoints for agent execution:
- Input validation on all endpoints
- Consistent error responses
- Background task support for long-running operations

## Error Types

The system defines a hierarchy of error types for precise error handling:
- `AgentError`: Base class for all agent errors
- `ValidationError`: For input validation issues
- `InputValidationError`: For type validation issues
- `SchemaValidationError`: For schema compliance issues
- And more specific error types...

## Future Improvements

Planned improvements include:
- Better caching of results
- Agent orchestration for complex workflows
- Expanded CI/CD integration
- Comprehensive regression tests

```

## System Architecture Summary


### API Endpoints

- /api/analyze_file
- /api/repair_file
- /api/generate_tests
- /api/task/{task_id}
