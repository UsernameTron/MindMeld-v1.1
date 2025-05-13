#!/bin/bash

echo "Generating weekly status report on $(date)"

# Generate implementation status
node ./scripts/generate-status.js

# Run technical debt analysis
node ./scripts/analyze-tech-debt.js > ./docs/technical-debt/weekly-analysis-$(date +%Y%m%d).md

# Identify next actions
./scripts/next-action.sh > ./docs/reports/next-actions-$(date +%Y%m%d).txt

echo "Weekly status report complete"
echo "- Implementation status: IMPLEMENTATION_STATUS.md"
echo "- Technical debt analysis: ./docs/technical-debt/weekly-analysis-$(date +%Y%m%d).md"
echo "- Next actions: ./docs/reports/next-actions-$(date +%Y%m%d).txt"
