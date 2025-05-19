#!/usr/bin/env python3
"""
repo_healthcheck.py: Unified repo health and hygiene scanner.
Performs:
 1. TODO/FIXME/XXX scanner
 2. Import-Health Checker (Python/TS)
 3. Env-Var & Config Validator
 4. Dependency Auditor (Python/Node)
 5. Large-File Detector (>10MB)
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# --- CONFIG ---
REQUIRED_ENV_VARS = ["CLAUDE_API_KEY", "PHI_MODEL_PATH"]
CONFIG_EXTS = [".json", ".yml", ".yaml"]
LARGE_FILE_MB = 10
IGNORE_DIRS = {'.git', 'node_modules', 'run', 'logs', 'output', 'outputs', 'htmlcov', '__pycache__', 'playwright-report', 'temp'}

# --- 1. TODO/FIXME/XXX Scanner ---
def scan_todos(root):
    print("\n=== [1] TODO/FIXME/XXX Scanner ===")
    todo_re = re.compile(r"(TODO|FIXME|XXX)", re.IGNORECASE)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            if fn.endswith(('.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.sh', '.json', '.yml', '.yaml')):
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if todo_re.search(line):
                                print(f"{path}:{i}: {line.strip()}")
                except Exception as e:
                    print(f"[WARN] Could not read {path}: {e}")

# --- 2. Import-Health Checker ---
def check_python_imports(root):
    print("\n--- Python Import/Compile Check ---")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            if fn.endswith('.py'):
                path = os.path.join(dirpath, fn)
                try:
                    subprocess.check_output([sys.executable, '-m', 'py_compile', path], stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR] {path}: {e.output.decode().strip()}")

def check_ts_imports(root):
    print("\n--- TypeScript Import/Compile Check ---")
    tsc = shutil.which('tsc')
    if not tsc:
        print("[WARN] tsc (TypeScript compiler) not found in PATH.")
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            if fn.endswith(('.ts', '.tsx')):
                path = os.path.join(dirpath, fn)
                try:
                    subprocess.check_output([tsc, '--noEmit', path], stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR] {path}: {e.output.decode().strip()}")

# --- 3. Env-Var & Config Validator ---
def check_env_vars():
    print("\n=== [3] Env-Var & Config Validator ===")
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            print(f"[MISSING] Env var: {var}")
        else:
            print(f"[OK] Env var: {var}")

def check_config_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in CONFIG_EXTS:
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, encoding='utf-8') as f:
                        if ext == '.json':
                            json.load(f)
                        else:
                            import yaml
                            yaml.safe_load(f)
                    print(f"[OK] Config parses: {path}")
                except Exception as e:
                    print(f"[ERROR] Config parse failed: {path}: {e}")

# --- 4. Dependency Auditor ---
def check_python_deps():
    print("\n--- Python Dependency Auditor ---")
    req = Path('requirements.txt')
    if req.exists():
        try:
            import pkg_resources
            with open(req) as f:
                for line in f:
                    pkg = line.strip().split('==')[0]
                    if pkg and not pkg.startswith('#'):
                        try:
                            pkg_resources.get_distribution(pkg)
                        except Exception:
                            print(f"[MISSING] Python package: {pkg}")
        except ImportError:
            print("[WARN] pkg_resources not available. Skipping Python dep check.")


def check_node_deps():
    print("\n--- Node.js Dependency Auditor ---")
    if not Path('package.json').exists():
        print("[INFO] No package.json found.")
        return
    try:
        with open('package.json') as f:
            pkg = json.load(f)
        deps = set(pkg.get('dependencies', {}).keys()) | set(pkg.get('devDependencies', {}).keys())
        lock = None
        if Path('yarn.lock').exists():
            lock = Path('yarn.lock').read_text()
        elif Path('package-lock.json').exists():
            lock = Path('package-lock.json').read_text()
        else:
            print("[WARN] No lockfile found.")
        for dep in deps:
            if lock and dep not in lock:
                print(f"[MISSING] Node dep not in lockfile: {dep}")
    except Exception as e:
        print(f"[ERROR] Node dep check failed: {e}")

# --- 5. Large-File Detector ---
def detect_large_files(root):
    print("\n=== [5] Large-File Detector (>10MB) ===")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            try:
                size_mb = os.path.getsize(path) / (1024*1024)
                if size_mb > LARGE_FILE_MB:
                    print(f"[LARGE] {path}: {size_mb:.2f} MB")
            except Exception:
                continue

# --- MAIN ---
if __name__ == "__main__":
    import shutil
    root = os.path.dirname(os.path.abspath(__file__))
    scan_todos(root)
    print("\n=== [2] Import-Health Checker ===")
    check_python_imports(root)
    check_ts_imports(root)
    check_env_vars()
    check_config_files(root)
    check_python_deps()
    check_node_deps()
    detect_large_files(root)
    print("\n[Done]")
