import json
import os
from datetime import datetime

import yaml

# List of critical files to include in Claude's context
CRITICAL_FILES = [
    {"path": "run_agent.py", "priority": "Highest"},
    {"path": "packages/agents/AgentFactory.py", "priority": "Highest"},
    {"path": "packages/agents/advanced_reasoning/agents.py", "priority": "Highest"},
    {"path": "agent_report_schema.json", "priority": "Highest"},
    {"path": "app.py", "priority": "Highest"},
    {"path": "utils/llm_client.py", "priority": "High"},
    {"path": "utils/error_handling.py", "priority": "High"},
    {"path": "schema_validator.py", "priority": "High"},
    {"path": "run_all_agents.py", "priority": "Medium"},
    {"path": ".github/workflows/validate-agent-reports.yml", "priority": "Medium"},
    {"path": "docs/AGENT_REPORT_SCHEMA.md", "priority": "Medium"},
    {"path": "docs/PIPELINE_FIXES.md", "priority": "Medium"},
]

def get_file_content(file_path):
    """Read file content if it exists."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    return None

def determine_file_type(file_path):
    """Determine file type based on extension."""
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.py':
        return 'python'
    elif extension == '.json':
        return 'json'
    elif extension == '.md':
        return 'markdown'
    elif extension == '.yml' or extension == '.yaml':
        return 'yaml'
    else:
        return 'text'

def format_for_context(file_path, content, priority):
    """Format file content for Claude context."""
    file_type = determine_file_type(file_path)
    
    # Format the file content with proper markdown code blocks
    formatted_content = f"## {file_path} (Priority: {priority})\n\n"
    formatted_content += f"```{file_type}\n{content}\n```\n\n"
    
    return formatted_content

def generate_context_file():
    """Generate the context file with all critical files."""
    context_directory = ".claude"
    os.makedirs(context_directory, exist_ok=True)
    
    # Start with a header
    context_content = "# MindMeld Repository Context for Claude\n\n"
    context_content += f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Add a summary of the files
    context_content += "## File Index\n\n"
    for file_info in CRITICAL_FILES:
        file_path = file_info["path"]
        priority = file_info["priority"]
        context_content += f"- {file_path} (Priority: {priority})\n"
    
    context_content += "\n## File Contents\n\n"
    
    # Add the content of each file
    for file_info in CRITICAL_FILES:
        file_path = file_info["path"]
        priority = file_info["priority"]
        content = get_file_content(file_path)
        
        if content:
            context_content += format_for_context(file_path, content, priority)
        else:
            context_content += f"## {file_path} (Priority: {priority})\n\n"
            context_content += "**File not found**\n\n"
    
    # Add a system architecture summary from the most important files
    context_content += "## System Architecture Summary\n\n"
    
    # Try to extract key information about the system
    try:
        # If we have a factory file, try to extract agent types
        factory_path = "packages/agents/AgentFactory.py"
        factory_content = get_file_content(factory_path)
        if factory_content:
            # Simple pattern matching to find AGENT_REGISTRY
            import re
            agent_types = re.findall(r'AGENT_REGISTRY\s*=\s*{([^}]*)}', factory_content, re.DOTALL)
            if agent_types:
                context_content += "### Registered Agent Types\n\n"
                # Clean and format the agent registry
                agents = [a.strip() for a in agent_types[0].split(',') if a.strip()]
                for agent in agents:
                    if ':' in agent:
                        name, impl = agent.split(':', 1)
                        name_clean = name.strip().replace('"', '').replace("'", '')
                        context_content += f"- {name_clean}: {impl.strip()}\n"
        
        # Extract API endpoints from app.py
        app_path = "app.py"
        app_content = get_file_content(app_path)
        if app_content:
            # Look for route definitions
            import re
            routes = re.findall(r'@app\.(?:route|get|post|put|delete)\([\'"]([^\'"]*)[\'"]', app_content)
            if routes:
                context_content += "\n### API Endpoints\n\n"
                for route in routes:
                    context_content += f"- {route}\n"
    
    except Exception as e:
        context_content += f"Error analyzing system architecture: {str(e)}\n\n"
    
    # Write the content to the context file
    with open(os.path.join(context_directory, "context.md"), 'w') as f:
        f.write(context_content)

if __name__ == "__main__":
    generate_context_file()
    print("Claude context file generated successfully!")
