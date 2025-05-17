#!/bin/bash
# Run Flake8 across the project
set -e

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  echo "Usage: ./lint.sh [directory]"
  echo ""
  echo "Run Flake8 linting on the entire project or specific directory"
  echo ""
  echo "Options:"
  echo "  --help, -h     Show this help message"
  echo "  directory      Specific directory to lint (default: current directory)"
  exit 0
fi

TARGET_DIR=${1:-.}
echo "Running Flake8 on $TARGET_DIR"

# Run flake8
python -m flake8 "$TARGET_DIR"

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "✅ Flake8 passed!"
else
  echo "❌ Flake8 found issues, please fix them."
  exit $exit_code
fi
