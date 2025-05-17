# MindMeld Agents: Installation, Training, and Testing Guide

Based on the agent analysis and run results, here's a complete guide to installing, training, and testing the MindMeld agent system.

## 1. Installation Requirements

```bash
# Core dependencies
pip install ollama sentence-transformers faiss-cpu transformers torch numpy Pillow torchaudio memory-profiler

# For test generation
pip install pytest pytest-xdist pytest-cov

# For visualization
pip install matplotlib seaborn pandas
```

## 2. Environment Setup

```bash
# Start Ollama service (required for LLM-based agents)
brew install ollama  # MacOS
ollama serve &       # Run in background

# Pull required models
ollama pull mistral   # Base model for most agents
```

## 3. Agent Training (where applicable)

Based on the agent analysis, the following agents have training capabilities:

```bash
# Run TestGeneratorAgent training
python3 -c 'from packages.agents.advanced_reasoning.agents import TestGeneratorAgent; agent = TestGeneratorAgent(); agent.train()'

# Run DependencyAgent training 
python3 -c 'from packages.agents.advanced_reasoning.agents import DependencyAgent; agent = DependencyAgent(); agent.train()'
```

## 4. Running Individual Agents

```bash
# Run dependency analysis
python3 run_agent.py dependency_agent src/ --output-dir=reports/dependency_agent

# Run test generation
python3 run_agent.py test_generator src/ --output-dir=reports/test_generator

# Run CEO agent for high-level analysis
python3 run_agent.py ceo src/ --output-dir=reports/ceo

# Run code optimization
python3 run_agent.py IntegratedCodebaseOptimizer src/ --output-dir=reports/IntegratedCodebaseOptimizer
```

## 5. Batch Run All Agents

```bash
# Use the comprehensive runner script
python3 run_all_agents.py
```

## 6. Validation and Report Analysis

```bash
# Check agent report files
ls -la reports/*/

# Parse all reports into a summary
python3 -c '
import json, glob
from pathlib import Path
reports = {}
for report_file in glob.glob("reports/*/*.json"):
    agent_name = Path(report_file).parent.name
    with open(report_file) as f:
        try:
            data = json.load(f)
            reports[agent_name] = data
        except:
            with open(report_file) as f:
                reports[agent_name] = f.read()
print(json.dumps(reports, indent=2))
' > combined_report.json

# View combined report
cat combined_report.json
```

## 7. Troubleshooting

- If Ollama-based agents fail, ensure Ollama is running with `ollama serve`
- For CodeEmbeddingIndex errors, ensure the model path is valid or use the default
- For SemanticCodeSearch errors, ensure input is properly formatted as a string or dictionary
- For agent instantiation errors, check that all required arguments have defaults in the constructor

## 8. Integration with CI/CD

Add the following to your CI workflow:

```yaml
name: Agent Analysis

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Analyze project
      run: |
        python run_all_agents.py
    - name: Upload analysis reports
      uses: actions/upload-artifact@v2
      with:
        name: agent-reports
        path: reports/
```

This comprehensive plan should allow you to successfully install, train, run, and validate all agents in the MindMeld system.
