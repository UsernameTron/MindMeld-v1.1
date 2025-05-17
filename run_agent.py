#!/usr/bin/env python3
import sys
from pathlib import Path
import json
import jsonschema
import time
import os
import requests
import platform
from packages.agents.AgentFactory import AGENT_REGISTRY

# load the schema once
schema_path = Path(__file__).parent / "agent_report_schema.json"
with open(schema_path) as sf:
    REPORT_SCHEMA = json.load(sf)

if len(sys.argv) < 3:
    print("Usage: python run_agent.py <agent_name> <task-or-input> [--output-dir=DIR]")
    sys.exit(1)

# parse optional --output-dir
args = sys.argv[1:]
name = args[0]
# collect non-flag parts as payload
payload_parts = [a for a in args[1:] if not a.startswith("--")]
payload = " ".join(payload_parts)

# detect output dir flag
out_flag = next((a for a in args[1:] if a.startswith("--output-dir=")), None)
output_dir = Path(out_flag.split("=",1)[1]) if out_flag else Path("reports")/name
output_dir.mkdir(parents=True, exist_ok=True)

if name not in AGENT_REGISTRY:
    print(f"Unknown agent: {name}")
    sys.exit(1)

# Check if Ollama is running before attempting to create agent
try:
    # Try to connect to Ollama API
    ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    if response.status_code != 200:
        print(f"⚠️ Warning: Ollama API returned status code {response.status_code}")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to Ollama API: {e}")
    print("Make sure Ollama is running before running agents.")
    # Continue anyway - the agent will handle the retry logic

creator = AGENT_REGISTRY[name]
# always instantiate with no args
if callable(creator):
    agent = creator()
else:
    agent = creator

try:
    agent = creator(payload) if callable(creator) else creator
except TypeError:
    agent = creator() if callable(creator) else creator

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
    result = f"[ERROR] Agent execution failed: {e}"

# ensure output_dir exists
output_dir.mkdir(parents=True, exist_ok=True)

# Add metadata to the result if it's an object
end_time = time.time()
timestamp = int(end_time)
if isinstance(result, dict):
    result["metadata"] = {
        "agent": name,
        "timestamp": timestamp,
        "payload": payload[:200],
        "runtime_seconds": end_time - start_time,
        "system_info": {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "model_info": {
            "name": os.getenv("OLLAMA_MODEL", "phi3.5:latest"),
        }
    }
report_path = output_dir / f"{name}_{timestamp}.json"
with open(report_path, "w") as f:
    if isinstance(result, (dict, list)):
        json.dump(result, f, indent=2)
    else:
        json.dump({"result": str(result), "metadata": {"agent": name, "timestamp": timestamp}}, f, indent=2)

# validate
try:
    with open(report_path) as rf:
        data = json.load(rf)
    jsonschema.validate(instance=data, schema=REPORT_SCHEMA)
    print(f"✅ Report valid and written to {report_path}")
except Exception as e:
    print(f"❌ Schema validation failed for {report_path}: {e}")
