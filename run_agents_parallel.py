import concurrent.futures
import subprocess
import json
import os
from packages.agents.AgentFactory import AGENT_REGISTRY

def run_agent(agent_name, target_path):
    cmd = ["python", "run_agent.py", agent_name, target_path, 
           f"--output-dir=reports/{agent_name}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return agent_name, result.stdout, result.returncode

def main(target_path, max_workers=None):
    agents = list(AGENT_REGISTRY.keys())
    results = {}
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_agent, agent, target_path) for agent in agents]
        for future in concurrent.futures.as_completed(futures):
            agent_name, output, return_code = future.result()
            results[agent_name] = {
                "success": return_code == 0,
                "output": output
            }
            
    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python run_agents_parallel.py <target_path> [max_workers]")
        sys.exit(1)
    target_path = sys.argv[1]
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else None
    main(target_path, max_workers)
