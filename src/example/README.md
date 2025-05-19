# MindMeld Codebase Analysis

This directory contains scripts for running comprehensive analysis on the MindMeld codebase using its own agent system. This is a practical example of "eating your own dog food" - using the agent system to analyze itself.

## Prerequisites

Before running the analysis, make sure:

1. You have Ollama installed and available at http://localhost:11434
2. You have pulled the required model:

```bash
ollama pull codellama
```

3. All dependencies are installed:

```bash
pip install -r requirements.txt
```

## Running the Analysis

### Comprehensive Analysis

For a full, in-depth analysis of the codebase:

```bash
cd /path/to/mindmeld-v1.1  # Navigate to the project root
python -m src.example.analyze_codebase
```

The comprehensive script will:

1. Set up a system of specialized agents
2. Analyze the architecture of the MindMeld codebase
3. Examine selected individual files
4. Analyze project dependencies
5. Generate a comprehensive report with recommendations

### Quick Analysis

For a quicker, more focused analysis:

```bash
cd /path/to/mindmeld-v1.1  # Navigate to the project root
python -m src.example.quick_analyze_codebase
```

The quick analysis will:

1. Set up a minimal set of agents
2. Analyze a few key core files
3. Perform a dependency analysis
4. Generate a simple summary of findings

## Output

### Comprehensive Analysis

Results will be stored in the `data/outputs/analysis` directory, including:

- `architecture_analysis.json`: High-level architecture assessment
- `dependency_analysis.json`: Project dependencies assessment
- Individual file analyses with naming pattern `[filename]_analysis.json`
- `final_report.json`: Comprehensive report with recommendations

### Quick Analysis

Results will be stored in the `data/outputs/quick_analysis` directory as a single `quick_analysis_results.json` file.

A summary of findings will also be printed to the console for both analysis types.

## Customization

You can modify the scripts to:

- Use a different model by changing the `model` parameter in `LLMClientFactory.create_client()`
- Analyze more files by adjusting the file selection
- Focus on specific directories by modifying the paths in the script
- Add support for other file types by extending the `extensions` parameter in `collect_files()`

## Troubleshooting

If you encounter issues:

1. Make sure Ollama is running (`ollama serve`)
2. Check if the codellama model is available (`ollama list`)
3. Verify you have the required amount of memory (8GB+ recommended)
4. Check for errors in the console output
