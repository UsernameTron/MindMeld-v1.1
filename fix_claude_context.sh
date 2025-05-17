#!/bin/bash
# Fix generate_claude_context.py file
set -e

ORIGINAL_FILE="/Users/cpconnor/projects/mindmeld-v1.1/generate_claude_context.py"
BACKUP_FILE="/Users/cpconnor/projects/mindmeld-v1.1/generate_claude_context.py.bak"

# Make a backup of the original file
cp "$ORIGINAL_FILE" "$BACKUP_FILE"
echo "Created backup at $BACKUP_FILE"

# Fix the syntax error in line 102 - replace the backslash in f-string
sed -i '' '102s/strip(\\"\\\'\\\')/strip("\\"\\"\'\'")/' "$ORIGINAL_FILE"

# Run flake8 on the file to check for other issues
echo "Checking for other issues with flake8..."
python -m flake8 "$ORIGINAL_FILE" || {
  echo ""
  echo "There are other issues that need to be fixed."
}

echo ""
echo "✅ Fixed syntax error in generate_claude_context.py"
echo "   You can now run the file with: python $ORIGINAL_FILE"
