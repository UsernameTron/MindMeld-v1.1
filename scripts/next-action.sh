#!/bin/bash

# Determine next priority action based on implementation status

echo "Analyzing component status..."

# Check LoadingIndicator
./scripts/verify-component.sh LoadingIndicator > ./loading-status.txt
if grep -q "missing" ./loading-status.txt; then
  echo "NEXT ACTION: Complete LoadingIndicator component"
  echo "Run: ./scripts/migrate-component.sh LoadingIndicator molecules"
  exit 0
fi

# Check ErrorDisplay
./scripts/verify-component.sh ErrorDisplay > ./error-status.txt
if grep -q "missing" ./error-status.txt; then
  echo "NEXT ACTION: Complete ErrorDisplay component"
  echo "Run: ./scripts/migrate-component.sh ErrorDisplay molecules"
  exit 0
fi

# Check FeatureErrorBoundary
./scripts/verify-component.sh FeatureErrorBoundary > ./boundary-status.txt
if grep -q "missing" ./boundary-status.txt; then
  echo "NEXT ACTION: Implement FeatureErrorBoundary component"
  echo "Create component in: ./frontend/src/components/ui/organisms/FeatureErrorBoundary"
  exit 0
fi

echo "All Sprint 2 components are complete!"
echo "NEXT ACTION: Begin Sprint 3 preparation"
echo "Start with CodeEditor component implementation"
