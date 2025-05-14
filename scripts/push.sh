#!/usr/bin/env bash
set -e

# Default commit message if none provided
MSG=${1:-"Auto-commit from agent"}

# Update timestamp in PROJECT_STATUS.md
TODAY=$(date +"%Y-%m-%d")
# macOS-compatible in-place edit with sed
sed -i '' "s/## Last Updated: .*$/## Last Updated: $TODAY/" PROJECT_STATUS.md

# Check if any files were modified in components, services, or pages directories
COMPONENT_CHANGES=$(git diff --name-only -- 'src/components/' 'src/services/' 'src/pages/' 'backend/services/' 'backend/routes/')

if [ -n "$COMPONENT_CHANGES" ]; then
  echo "Component changes detected. Consider updating PROJECT_STATUS.md to reflect these changes."
  echo "Changed files:"
  echo "$COMPONENT_CHANGES"
fi

# Prompt for confirmation if PROJECT_STATUS.md hasn't been updated in a while
LAST_STATUS_UPDATE=$(git log -1 --format="%at" -- PROJECT_STATUS.md 2>/dev/null || echo "0")
NOW=$(date +%s)
THREE_DAYS=$((3 * 24 * 60 * 60))

if [ $((NOW - LAST_STATUS_UPDATE)) -gt $THREE_DAYS ]; then
  echo "⚠️ Warning: PROJECT_STATUS.md hasn't been updated in more than 3 days."
  echo "Have you updated the implementation status after your recent changes?"
  
  read -p "Continue with commit? (y/n): " CONFIRM
  if [ "$CONFIRM" != "y" ]; then
    echo "Commit aborted. Please update PROJECT_STATUS.md before committing."
    exit 1
  fi
fi

# Calculate and display project status summary
echo "Generating project status summary..."
TOTAL_COMPONENTS=$(grep -c "^|" PROJECT_STATUS.md)
COMPLETED_COMPONENTS=$(grep -c "✅" PROJECT_STATUS.md)
PCT_COMPLETE=$((COMPLETED_COMPONENTS * 100 / (TOTAL_COMPONENTS - 1))) # -1 for header row

echo "📊 Project Status: $PCT_COMPLETE% complete ($COMPLETED_COMPONENTS/$((TOTAL_COMPONENTS - 1)) components)"

# Proceed with commit
git add .
git commit -m "$MSG"
git push -u origin main

echo "✅ Changes pushed successfully!"