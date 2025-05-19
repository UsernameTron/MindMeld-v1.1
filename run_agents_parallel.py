import concurrent.futures
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

from packages.agents.AgentFactory import AGENT_REGISTRY
from utils.file_operations import safe_file_write
from utils.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_agent(agent_name: str, target_path: str) -> Tuple[str, str, int]:
    """
    Run a single agent with improved error handling.

    Args:
        agent_name: Name of the agent to run
        target_path: Path to target file/directory for analysis

    Returns:
        Tuple of (agent_name, stdout, return_code)
    """
    cmd = [
        "python",
        "run_agent.py",
        agent_name,
        target_path,
        f"--output-dir=reports/{agent_name}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return agent_name, result.stdout, result.returncode
    except Exception as e:
        logger.error(f"Error running agent {agent_name}: {str(e)}")
        return agent_name, f"Error executing agent: {str(e)}", 1


def main(
    target_path: str, max_workers: int = None, filter_agents: List[str] = None
) -> Dict[str, Any]:
    """
    Run multiple agents in parallel with improved error handling.

    Args:
        target_path: Path to target file/directory for analysis
        max_workers: Maximum number of concurrent workers (None = auto)
        filter_agents: Optional list of agents to run (None = all)

    Returns:
        Dictionary with results for each agent
    """
    # Filter agents if specified
    if filter_agents:
        agents = [a for a in AGENT_REGISTRY.keys() if a in filter_agents]
    else:
        agents = list(AGENT_REGISTRY.keys())

    logger.info(f"Running {len(agents)} agents on target: {target_path}")

    # Pre-check model availability
    model_manager = ModelManager()
    llm_dependent_agents = model_manager.get_llm_dependent_agents()
    agent_models = {
        agent: model_manager.get_agent_model(agent)
        for agent in agents
        if agent in llm_dependent_agents
    }

    # Check models in advance
    for agent, model in agent_models.items():
        if model and not model_manager.check_model_availability(model):
            logger.warning(f"Model {model} for agent {agent} is not available")

    results = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all agent tasks
        future_to_agent = {
            executor.submit(run_agent, agent, target_path): agent for agent in agents
        }

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_agent):
            agent_name, output, return_code = future.result()
            results[agent_name] = {
                "success": return_code == 0,
                "output": output,
                "return_code": return_code,
            }

            # Log progress
            status = "✅" if return_code == 0 else "❌"
            logger.info(f"{status} {agent_name} completed")

    # Ensure the reports directory exists
    os.makedirs("reports", exist_ok=True)

    # Save the results with safe_file_write
    summary_path = Path("reports/summary.json")
    safe_file_write(summary_path, json.dumps(results, indent=2))

    logger.info(f"All agents completed. Summary saved to {summary_path}")
    return results


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Run multiple agents in parallel")
    parser.add_argument("target_path", help="Path to the target file/directory")
    parser.add_argument(
        "--max-workers", type=int, help="Maximum number of parallel workers"
    )
    parser.add_argument(
        "--agents", nargs="+", help="Specific agents to run (space-separated)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run the agents
    results = main(args.target_path, args.max_workers, args.agents)

    # Report overall success/failure
    failed_agents = [agent for agent, data in results.items() if not data["success"]]
    if failed_agents:
        logger.error(f"Failed agents: {', '.join(failed_agents)}")
        sys.exit(1)
    else:
        logger.info("All agents completed successfully")
        sys.exit(0)
