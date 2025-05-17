#!/bin/bash
# Comprehensive Python code quality check
set -e

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  echo "Usage: ./check_code_quality.sh [directory]"
  echo ""
  echo "Run a comprehensive code quality check on Python files"
  echo ""
  echo "Options:"
  echo "  --help, -h     Show this help message"
  echo "  directory      Specific directory to check (default: current directory)"
  exit 0
fi

TARGET_DIR=${1:-.}
echo "Running code quality checks on $TARGET_DIR"

# Check for Python syntax errors
echo "🔍 Checking for syntax errors..."
find "$TARGET_DIR" -name "*.py" -exec python -m py_compile {} \; || {
  echo "❌ Found Python syntax errors!"
  exit 1
}

# Run flake8
echo "🔍 Running Flake8..."
python -m flake8 "$TARGET_DIR" || {
  echo "⚠️ Flake8 found style issues."
}

# Check for common security issues with bandit
if command -v bandit &>/dev/null; then
  echo "🔍 Checking for security issues with Bandit..."
  bandit -r "$TARGET_DIR" -ll || {
    echo "⚠️ Bandit found potential security issues."
  }
else
  echo "⚠️ Bandit not installed. To check for security issues, install with:"
  echo "   pip install bandit"
fi

# Check for type issues with mypy
if command -v mypy &>/dev/null; then
  echo "🔍 Checking for type issues with mypy..."
  mypy --ignore-missing-imports "$TARGET_DIR" || {
    echo "⚠️ mypy found type issues."
  }
else
  echo "⚠️ mypy not installed. To check for type issues, install with:"
  echo "   pip install mypy"
fi

# Check for complexity
echo "🔍 Checking for complex code..."
python -m flake8 --select=C901 --max-complexity=10 "$TARGET_DIR" || {
  echo "⚠️ Found complex code that might need refactoring."
}

echo ""
echo "✅ Code quality check completed!"
