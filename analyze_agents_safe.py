import inspect
import json
import os
import re
import sys
from pathlib import Path

# Ensure we can import your agents
sys.path.append(str(Path.cwd()))
from packages.agents.AgentFactory import AGENT_REGISTRY

project_root = Path.cwd()
analysis = {}

# locate shell scripts that call run_agent.py
shells = [str(p.relative_to(project_root)) for p in project_root.glob("*.sh")] + \
         [str(p.relative_to(project_root)) for p in project_root.glob("scripts/*.sh")]

for name, creator in AGENT_REGISTRY.items():
    entry = {
        "agent_name": name,
        "files": {"python": [], "shell": shells, "configs": []},
        "classes": {}, "training_entry_points": [],
        "dataset_paths": [], "hyperparameters": {},
        "model_classes": [], "install_commands": [], "notes": ""
    }
    try:
        # Don’t call the constructor—just grab the class or function
        cls = creator if inspect.isclass(creator) else creator.__class__
        mod = inspect.getmodule(cls)
        path = Path(inspect.getfile(mod)).relative_to(project_root)
        entry["files"]["python"].append(str(path))
        # config files in same folder
        for cfg in path.parent.glob("*.json")+path.parent.glob("*.yml")+path.parent.glob("*.yaml"):
            entry["files"]["configs"].append(str(cfg.relative_to(project_root)))
        # Load source text directly from the file
        src = path.read_text()
        # training hooks
        entry["training_entry_points"] = re.findall(r"def\s+(train\w*)\(", src)
        # datasets
        entry["dataset_paths"] = re.findall(r"[\"'](data[s]?/[^\"']+)[\"']", src)
        # hyperparams
        for k,v in re.findall(r"(\w+)\s*=\s*([0-9.]+)", src):
            if k.lower() in ("lr","learning_rate","batch_size","epochs","num_epochs"):
                entry["hyperparameters"][k] = float(v) if "." in v else int(v)
        # model classes
        entry["model_classes"] = re.findall(r"class\s+(\w*Model)\b", src)
        # pip installs
        entry["install_commands"] = re.findall(r"pip install ([^\n]+)", src)
    except Exception as e:
        entry["notes"] = f"Error: {e}"
    analysis[name] = entry

with open("agent_analysis.json","w") as f:
    json.dump(analysis, f, indent=2)

print("✅ agent_analysis.json generated")
