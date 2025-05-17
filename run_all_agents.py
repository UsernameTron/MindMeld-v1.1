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
