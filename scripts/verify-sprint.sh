#!/bin/bash

SPRINT=$1

if [ -z "$SPRINT" ]; then
  echo "Usage: $0 <SprintNumber>"
  exit 1
fi

echo "Verifying Sprint $SPRINT completion..."

if [ "$SPRINT" = "2" ]; then
  COMPONENTS=("Button" "Card" "Select" "LoadingIndicator" "ErrorDisplay" "FeatureErrorBoundary")
  
  COMPLETE=true
  for component in "${COMPONENTS[@]}"; do
    echo "Checking $component..."
    ./scripts/verify-component.sh $component > ./component-check.txt
    
    if grep -q "missing" ./component-check.txt; then
      echo "❌ $component is incomplete"
      COMPLETE=false
    else
      echo "✅ $component is complete"
    fi
  done
  
  if [ "$COMPLETE" = true ]; then
    echo "🎉 Sprint 2 is COMPLETE!"
  else
    echo "⚠️ Sprint 2 is INCOMPLETE. See above for details."
  fi
fi
