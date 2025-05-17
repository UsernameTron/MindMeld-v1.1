#!/bin/zsh
# Run all agents in AGENT_REGISTRY on src/ and output to reports/<agent>
# Improved version with parallel execution and better error handling

# Create the reports directory if it doesn't exist
mkdir -p reports

# Get the list of available agents
agents=$(python3 - << 'PYCODE'
from packages.agents.AgentFactory import AGENT_REGISTRY
print("\n".join(AGENT_REGISTRY.keys()))
PYCODE
)

# Check if we should run in parallel
PARALLEL=false
MAX_WORKERS=4

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --parallel|-p)
      PARALLEL=true
      shift
      ;;
    --max-workers|-w)
      MAX_WORKERS="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --parallel, -p       Run agents in parallel"
      echo "  --max-workers, -w N  Maximum number of parallel workers (default: 4)"
      echo "  --help, -h           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Define execution function
run_agent() {
  local agent="$1"
  echo "▶️ Running $agent on src/"
  python3 run_agent.py "$agent" src/ \
    --output-dir="reports/$agent" \
    --verbose

  local exit_code=$?
  if [ $exit_code -eq 0 ]; then
    echo "✅ Agent $agent completed successfully"
  else
    echo "❌ Agent $agent failed with exit code $exit_code"
  fi
  return $exit_code
}

# Run either in parallel or sequentially
if [ "$PARALLEL" = true ]; then
  echo "🚀 Running agents in parallel with $MAX_WORKERS workers"

  # Run with python's ProcessPoolExecutor
  python3 run_agents_parallel.py src/ $MAX_WORKERS

  echo "📊 Results summary saved to reports/summary.json"
else
  # Run agents sequentially
  echo "🔄 Running agents sequentially"

  success_count=0
  failure_count=0

  for agent in $agents; do
    run_agent "$agent"
    if [ $? -eq 0 ]; then
      ((success_count++))
    else
      ((failure_count++))
    fi
  done

  # Create a simple summary report
  summary="{\"summary\": {\"total\": $(($success_count + $failure_count)), \"success\": $success_count, \"failed\": $failure_count}}"
  echo $summary > reports/summary.json

  echo "📊 All agents completed: $success_count succeeded, $failure_count failed"
fi
