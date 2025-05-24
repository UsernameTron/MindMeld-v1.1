import inspect
import json
import re
import sys
from pathlib import Path

# Ensure we can import your agents
sys.path.append(str(Path.cwd()))
from packages.agents.AgentFactory import AGENT_REGISTRY

project_root = Path.cwd()
analysis = {}

# locate shell scripts that call run_agent.py
shells = [str(p.relative_to(project_root)) for p in project_root.glob("*.sh")] + [
    str(p.relative_to(project_root)) for p in project_root.glob("scripts/*.sh")
]

for name, creator in AGENT_REGISTRY.items():
    entry = {
        "agent_name": name,
        "files": {"python": [], "shell": shells, "configs": []},
        "classes": {},
        "training_entry_points": [],
        "dataset_paths": [],
        "hyperparameters": {},
        "model_classes": [],
        "install_commands": [],
        "notes": "",
    }
    try:
        # Don’t call the constructor—just grab the class or function
        cls = creator if inspect.isclass(creator) else creator.__class__
        # First, try the real module file
        mod = inspect.getmodule(cls)
        file_path = None
        if mod and hasattr(mod, "__file__") and mod.__file__:
            file_path = Path(mod.__file__)
        else:
            # fallback: derive from cls.__module__
            mod_name = cls.__module__
            parts = mod_name.split(".")
            cand = project_root.joinpath(*parts)
            if cand.with_suffix(".py").exists():
                file_path = cand.with_suffix(".py")
            elif (cand / "__init__.py").exists():
                file_path = cand / "__init__.py"
        if file_path:
            rel = file_path.relative_to(project_root)
            entry["files"]["python"].append(str(rel))
            # collect configs next to it
            cfgs = (
                list(file_path.parent.glob("*.json"))
                + list(file_path.parent.glob("*.yml"))
                + list(file_path.parent.glob("*.yaml"))
            )
            for cfg in cfgs:
                entry["files"]["configs"].append(str(cfg.relative_to(project_root)))
        # load the source text
        src = file_path.read_text() if file_path else ""
        # training hooks
        entry["training_entry_points"] = re.findall(r"def\s+(train\w*)\(", src)
        # datasets
        entry["dataset_paths"] = re.findall(r"[\"'](data[s]?/[^\"']+)[\"']", src)
        # hyperparams
        for k, v in re.findall(r"(\w+)\s*=\s*([0-9.]+)", src):
            if k.lower() in (
                "lr",
                "learning_rate",
                "batch_size",
                "epochs",
                "num_epochs",
            ):
                entry["hyperparameters"][k] = float(v) if "." in v else int(v)
        # model classes
        entry["model_classes"] = re.findall(r"class\s+(\w*Model)\b", src)
        # pip installs
        entry["install_commands"] = re.findall(r"pip install ([^\n]+)", src)
    except Exception as e:
        entry["notes"] = f"Error: {e}"
    analysis[name] = entry

with open("agent_analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)

print("✅ agent_analysis.json generated")
