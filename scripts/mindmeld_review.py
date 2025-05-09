#!/usr/bin/env python3
"""
Automated compliance review for MindMeld project.
- Checks for RateLimiter usage in endpoints
- Checks prompt attribution compliance
- Runs static analysis tools
- Generates HTML report
"""
import glob
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = PROJECT_ROOT / "app"
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "personas"
REPORT_PATH = PROJECT_ROOT / "mindmeld_review_report.html"

RATE_LIMITER_PATTERN = re.compile(r"RateLimiter\s*\(")
ENDPOINT_PATTERN = re.compile(r"@app\.(get|post|put|delete)\(")

ATTRIBUTION_FIELDS = [
    "title",
    "version",
    "author",
    "source",
    "license",
    "created",
    "last_modified",
    "description",
]


def find_rate_limiter_usage() -> List[str]:
    """Find endpoints using RateLimiter and those missing it."""
    results = []
    for pyfile in APP_DIR.rglob("*.py"):
        with open(pyfile, "r", encoding="utf-8") as f:
            content = f.read()
        endpoints = [m.start() for m in ENDPOINT_PATTERN.finditer(content)]
        for idx in endpoints:
            snippet = content[idx : idx + 200]
            if "RateLimiter" in snippet:
                results.append(f"{pyfile}: RateLimiter used in endpoint.")
            else:
                results.append(f"{pyfile}: WARNING: Endpoint missing RateLimiter.")
    return results


def check_prompt_attribution() -> List[str]:
    """Check YAML frontmatter for required attribution fields."""
    results = []
    for yfile in PROMPTS_DIR.glob("*.yaml"):
        with open(yfile, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Extract YAML frontmatter
        if lines and lines[0].startswith("# ---"):
            yaml_lines = []
            for line in lines[1:]:
                if line.startswith("# ---"):
                    break
                if line.startswith("# "):
                    yaml_lines.append(line[2:])
            try:
                meta = yaml.safe_load("\n".join(yaml_lines))
                missing = [k for k in ATTRIBUTION_FIELDS if k not in meta]
                if missing:
                    results.append(f"{yfile}: MISSING fields: {', '.join(missing)}")
                else:
                    results.append(f"{yfile}: Attribution OK")
            except Exception as e:
                results.append(f"{yfile}: YAML ERROR: {e}")
        else:
            results.append(f"{yfile}: No YAML frontmatter found")
    return results


def run_static_analysis() -> Dict[str, str]:
    """Run static analysis tools and collect output."""
    tools = {
        "black": ["black", "--check", "."],
        "isort": ["isort", "--check-only", "."],
        "flake8": ["flake8", "."],
        "mypy": ["mypy", "--strict", "app/"],
        "bandit": ["bandit", "-r", "app/", "-c", "pyproject.toml"],
        "safety": ["safety", "check"],
    }
    results = {}
    for name, cmd in tools.items():
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
            results[name] = out.stdout + out.stderr
        except Exception as e:
            results[name] = f"ERROR: {e}"
    return results


def generate_html_report(rate_results, prompt_results, static_results):
    html = ["<html><head><title>MindMeld Compliance Review</title></head><body>"]
    html.append("<h1>MindMeld Compliance Review Report</h1>")
    html.append(
        "<h2>Rate Limiter Usage</h2><pre>{}</pre>".format("\n".join(rate_results))
    )
    html.append(
        "<h2>Prompt Attribution</h2><pre>{}</pre>".format("\n".join(prompt_results))
    )
    html.append("<h2>Static Analysis</h2>")
    for tool, output in static_results.items():
        html.append(f"<h3>{tool}</h3><pre>{output}</pre>")
    html.append("</body></html>")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"HTML report generated at {REPORT_PATH}")


def main():
    print("Checking RateLimiter usage...")
    rate_results = find_rate_limiter_usage()
    print("Checking prompt attribution...")
    prompt_results = check_prompt_attribution()
    print("Running static analysis tools...")
    static_results = run_static_analysis()
    print("Generating HTML report...")
    generate_html_report(rate_results, prompt_results, static_results)
    print("Done.")


if __name__ == "__main__":
    main()
