#!/bin/bash
# Fix common linting issues automatically
set -e

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  echo "Usage: ./lint_fix.sh [directory]"
  echo ""
  echo "Automatically fix linting issues in the project or specific directory"
  echo ""
  echo "Options:"
  echo "  --help, -h     Show this help message"
  echo "  directory      Specific directory to fix (default: current directory)"
  exit 0
fi

TARGET_DIR=${1:-.}
echo "Fixing linting issues in $TARGET_DIR"

# Run isort to fix import ordering
echo "🔧 Fixing import order with isort..."
python -m isort "$TARGET_DIR"

# Run black to fix formatting
echo "🔧 Fixing code formatting with black..."
python -m black "$TARGET_DIR"

# Run flake8 to check if there are remaining issues
echo "🔍 Checking for remaining issues with flake8..."
python -m flake8 "$TARGET_DIR" || {
  echo ""
  echo "⚠️ Some issues couldn't be fixed automatically."
  echo "   Please fix the remaining issues manually."
}

echo ""
echo "✅ Automatic fixes applied!"
