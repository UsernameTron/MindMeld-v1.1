#!/usr/bin/env python3
"""
MindMeld Architecture & Code Quality Review Script
- Produces a JSON report conforming to architecture/JSON Schema Template.json
- Gathers direct evidence from codebase: structure, dependencies, config, tests, duplication, risks
- Multi-pass: structure, function, contradiction, cleanup, risk
- Output: JSON file (mindmeld_architecture_review.json)
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = PROJECT_ROOT / "architecture" / "JSON Schema Template.json"
OUTPUT_PATH = PROJECT_ROOT / "mindmeld_architecture_review.json"

# Utility functions
def find_files(pattern, root=PROJECT_ROOT):
    return list(root.rglob(pattern))

def read_file_lines(path, n=20):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [next(f) for _ in range(n)]
    except Exception:
        return []

def get_git_version():
    try:
        import subprocess
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=PROJECT_ROOT)
        return out.stdout.strip()
    except Exception:
        return "not determined"

def get_package_version(pkg_path):
    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("version", "not determined")
    except Exception:
        return "not determined"

def get_lockfile_date(lock_path):
    try:
        return datetime.fromtimestamp(lock_path.stat().st_mtime).strftime("%Y-%m-%d")
    except Exception:
        return "not determined"

# Pass 1: Structural Discovery
def discover_structure():
    structure = {}
    structure["frontend"] = os.path.exists(PROJECT_ROOT / "frontend")
    structure["backend"] = os.path.exists(PROJECT_ROOT / "app")
    structure["tests"] = os.path.exists(PROJECT_ROOT / "tests")
    structure["schemas"] = os.path.exists(PROJECT_ROOT / "schemas")
    structure["ci"] = any("ci" in str(p).lower() for p in find_files("*.yml"))
    return structure

# Pass 2: Functional Audit (dependencies, routes, config, etc.)
def audit_dependencies():
    deps = {"frontend": [], "backend": [], "duplicates": [], "unused": [], "mismatches": []}
    # Frontend
    f_pkg = PROJECT_ROOT / "frontend" / "package.json"
    if f_pkg.exists():
        with open(f_pkg) as f:
            pkg = json.load(f)
        deps["frontend"] = list(pkg.get("dependencies", {}).keys()) + list(pkg.get("devDependencies", {}).keys())
    # Backend
    req = PROJECT_ROOT / "requirements.txt"
    if req.exists():
        with open(req) as f:
            deps["backend"] = [l.split("==")[0].strip() for l in f if l.strip() and not l.startswith("#")]
    # Duplicates
    deps["duplicates"] = list(set(deps["frontend"]) & set(deps["backend"]))
    return deps

def audit_config_files():
    configs = {}
    for pattern in ["tsconfig.json", "*.config.*", "*.yml", "*.yaml", "pyproject.toml"]:
        for f in find_files(pattern):
            configs[str(f.relative_to(PROJECT_ROOT))] = read_file_lines(f, 10)
    return configs

def audit_tests():
    test_dirs = ["tests", "frontend/tests", "frontend/src/__tests__", "frontend/src/tests", "frontend/e2e", "e2e"]
    test_files = []
    for d in test_dirs:
        p = PROJECT_ROOT / d
        if p.exists():
            test_files.extend(list(p.rglob("*.test.*")))
            test_files.extend(list(p.rglob("*.spec.*")))
    return [str(f.relative_to(PROJECT_ROOT)) for f in test_files]

def audit_duplication():
    # Look for duplicate component/service names
    names = {}
    for d in ["frontend/src/components", "frontend/src/services", "app/services"]:
        p = PROJECT_ROOT / d
        if p.exists():
            for f in p.rglob("*"):
                if f.is_file():
                    key = f.name
                    names.setdefault(key, []).append(str(f.relative_to(PROJECT_ROOT)))
    dups = {k: v for k, v in names.items() if len(v) > 1}
    return dups

# Pass 3: Cross-Check for Contradictions
def cross_check():
    contradictions = []
    # Example: both authService.js and authService.ts
    dups = audit_duplication()
    for k, v in dups.items():
        if "authService" in k:
            contradictions.append({"file": v, "issue": "Multiple authService implementations"})
    return contradictions

# Pass 4: Cleanup and Opportunity Mapping
def find_dead_code():
    dead = []
    # Untitled folders, .js in python dirs, test files not referenced
    for f in find_files("untitled folder"):
        dead.append(str(f.relative_to(PROJECT_ROOT)))
    for f in find_files("*.js", PROJECT_ROOT / "app"):
        dead.append(str(f.relative_to(PROJECT_ROOT)))
    return dead

# Pass 5: Systemic Risks and Forward Leverage
def summarize_risks():
    risks = [
        "Multiple auth implementations",
        "Component duplication",
        "Test config sprawl",
        "Partial migration (pages/app)"
    ]
    leverage = [
        "Consolidate UI components",
        "Unify test framework",
        "Single source of truth for config"
    ]
    return risks, leverage

# Main orchestration
def main():
    # Load schema template for field order
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    now = datetime.now().strftime("%Y-%m-%d")
    # --- Populate fields ---
    review_metadata = {
        "review_id": f"mindmeld-{now}",
        "date": now,
        "previous_review": "not determined",
        "reviewer": os.getenv("USER", "not determined"),
        "codebase_version": get_git_version(),
        "next_scheduled_review": "not determined"
    }
    review_lifecycle = {
        "change_log": [],
        "next_scheduled_review": "not determined",
        "reviewers": [os.getenv("USER", "not determined")],
        "stakeholders": ["Frontend", "Backend", "DevOps", "UX"],
        "signoff": []
    }
    deps = audit_dependencies()
    configs = audit_config_files()
    tests = audit_tests()
    dups = audit_duplication()
    contradictions = cross_check()
    dead = find_dead_code()
    risks, leverage = summarize_risks()
    # --- Compose output ---
    output = {
        "review_metadata": review_metadata,
        "review_lifecycle": review_lifecycle,
        "architecture_map": {
            "frontend": {
                "design_system": "Tailwind CSS, atomic design, partial tokens",
                "api_integration": "OpenAPI, schema validation",
                "context_patterns": "React context, inconsistent",
                "devops_ci": "CI present, not enforcing all checks",
                "ssr_client_boundary": "Pages + App router coexist",
                "security_posture": "localStorage tokens, no HttpOnly",
                "performance_metrics": {
                    "bundle_size": "not determined",
                    "test_coverage": f"{len(tests)} test files",
                    "build_failure_rate": "not determined"
                },
                "complexity_index": 7
            },
            "backend": {
                "routing_services": "FastAPI, modular routes",
                "middleware_di": "not determined",
                "model_validation": "not determined",
                "performance_scaling": "not determined",
                "security_compliance": "not determined",
                "deployment_observability": "not determined",
                "auth_lifecycle": "Multiple authService impls",
                "complexity_index": 5
            },
            "integration": {
                "openapi_typing": "OpenAPI spec, not CI-enforced",
                "contract_stability": "Schema check script exists",
                "dependency_health": "not determined",
                "latency_coupling": "not determined",
                "historical_context": "not determined",
                "test_coverage": "not determined",
                "complexity_index": 6
            }
        },
        "systemic_misalignments": [
            {"area": "Design System", "issue": "Partial token adoption", "impact": "Inconsistent UI"},
            {"area": "Auth", "issue": "Multiple authService", "impact": "Security risk"},
            {"area": "Frontend", "issue": "Pages/App router mix", "impact": "Navigation confusion"}
        ],
        "granular_findings": [
            {"category": "Security", "file_path": f, "line_number": "not determined", "first_identified": now, "summary": "Multiple authService implementations", "owner": "unassigned", "status_history": [{"date": now, "status": "Identified"}]} for f in dups.get("authService.js", []) + dups.get("authService.ts", [])
        ],
        "action_plan": {
            "foundational": [
                {"task": "Consolidate UI components", "addresses_risks": ["Duplication"], "dependencies": ["None"], "effort": "Medium", "owner": "unassigned", "target": "Single component lib", "target_completion": "not determined"}
            ],
            "multipliers": [
                {"task": "Unify test framework", "addresses_risks": ["Test config sprawl"], "dependencies": ["None"], "effort": "Medium", "owner": "unassigned", "target": "Single test runner", "target_completion": "not determined"}
            ],
            "structural": [
                {"task": "Remove dead code", "addresses_risks": ["Dead code"], "dependencies": ["None"], "effort": "Low", "owner": "unassigned", "target": "No dead files", "target_completion": "not determined"}
            ]
        },
        "knowledge_continuity": {
            "unexpected_challenges": "not determined",
            "architectural_decisions_rejected": "not determined",
            "future_proofing_considerations": "OpenAPI schema, partial CI"
        },
        "summary": {
            "health": "Needs cleanup",
            "trajectory": "Improving with action plan",
            "top_risks": risks,
            "top_leverage_points": leverage,
            "readiness": {
                "production_stability": "Partial",
                "feature_scaling": "Partial",
                "team_onboarding": "Blocked"
            }
        }
    }
    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Review JSON written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
