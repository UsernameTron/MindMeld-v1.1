#!/bin/zsh
# Run all agents in AGENT_REGISTRY on src/ and output to reports/<agent>

for agent in $(python3 - << 'PYCODE'
from packages.agents.AgentFactory import AGENT_REGISTRY
print("\n".join(AGENT_REGISTRY.keys()))
PYCODE
); do
  echo "▶️ Running $agent on src/"
  python3 run_agent.py "$agent" src/ \
    --output-dir="reports/$agent" \
    --verbose
done
