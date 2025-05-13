#!/bin/bash

# Check if component name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <ComponentName>"
  exit 1
fi

COMPONENT=$1
COMPONENT_PATHS=(
  "./frontend/src/components/$COMPONENT"
  "./frontend/src/components/ui/atoms/$COMPONENT"
  "./frontend/src/components/ui/molecules/$COMPONENT"
  "./frontend/src/components/ui/organisms/$COMPONENT"
  "./frontend/src/components/ui/molecules/$COMPONENT"
  "./frontend/src/components/ui/organisms/$COMPONENT"
)

# Check if component exists
FOUND=0
for path in "${COMPONENT_PATHS[@]}"; do
  if [ -d "$path" ]; then
    COMPONENT_PATH=$path
    FOUND=1
    break
  fi
done

if [ $FOUND -eq 0 ]; then
  echo "❌ Component '$COMPONENT' not found"
  exit 1
fi

echo "Found component at: $COMPONENT_PATH"

# Check implementation files
if [ -f "$COMPONENT_PATH/$COMPONENT.tsx" ]; then
  echo "✅ Implementation file exists"
else
  echo "❌ Implementation file missing"
fi

if [ -f "$COMPONENT_PATH/$COMPONENT.test.tsx" ]; then
  echo "✅ Test file exists"
else
  echo "❌ Test file missing"
fi

if [ -f "$COMPONENT_PATH/$COMPONENT.stories.tsx" ]; then
  echo "✅ Storybook file exists"
else
  echo "❌ Storybook file missing"
fi

if [ -f "$COMPONENT_PATH/index.ts" ]; then
  echo "✅ Index file exists"
else
  echo "❌ Index file missing"
fi

# Check TypeScript props interface
if grep -q "interface ${COMPONENT}Props" "$COMPONENT_PATH/$COMPONENT.tsx"; then
  echo "✅ TypeScript props interface found"
else
  echo "❌ TypeScript props interface missing"
fi

# Check test coverage (simplified)
if [ -f "$COMPONENT_PATH/$COMPONENT.test.tsx" ]; then
  TEST_COUNT=$(grep -c "test\|it(" "$COMPONENT_PATH/$COMPONENT.test.tsx")
  echo "ℹ️ Found $TEST_COUNT tests"
fi

echo "Component verification complete"
