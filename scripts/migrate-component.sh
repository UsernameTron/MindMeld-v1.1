#!/bin/bash

# Check if arguments are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <ComponentName> <TargetCategory>"
  echo "TargetCategory should be one of: atoms, molecules, organisms"
  exit 1
fi

COMPONENT=$1
CATEGORY=$2

# Validate category
if [[ ! "$CATEGORY" =~ ^(atoms|molecules|organisms)$ ]]; then
  echo "Error: Category must be one of: atoms, molecules, organisms"
  exit 1
fi

# Find component
FOUND_PATH=""
POSSIBLE_PATHS=(
  "./frontend/src/components/$COMPONENT"
  "./frontend/src/components/ui/$COMPONENT"
  "./frontend/src/components/atoms/$COMPONENT"
  "./frontend/src/components/molecules/$COMPONENT"
  "./frontend/src/components/organisms/$COMPONENT"
  "./frontend/src/components/ui/atoms/$COMPONENT"
  "./frontend/src/components/ui/molecules/$COMPONENT"
  "./frontend/src/components/ui/organisms/$COMPONENT"
)

for path in "${POSSIBLE_PATHS[@]}"; do
  if [ -d "$path" ]; then
    FOUND_PATH=$path
    break
  fi
done

if [ -z "$FOUND_PATH" ]; then
  echo "Error: Component '$COMPONENT' not found"
  exit 1
fi

# Create target directory
TARGET_PATH="./frontend/src/components/ui/$CATEGORY/$COMPONENT"
mkdir -p "$TARGET_PATH"

# Copy files to target
echo "Migrating component from $FOUND_PATH to $TARGET_PATH"
cp "$FOUND_PATH"/* "$TARGET_PATH"/

# Backup original location
BACKUP_DIR="./backup/components/$(date +%Y%m%d)/$COMPONENT"
mkdir -p "$BACKUP_DIR"
cp -r "$FOUND_PATH"/* "$BACKUP_DIR"/

# Find imports to update
echo "Files that need import updates:"
grep -r --include="*.tsx" --include="*.ts" "from ['\"].*$COMPONENT['\"]" ./frontend/src

# Create migration record
echo "$COMPONENT migrated from $FOUND_PATH to $TARGET_PATH on $(date)" >> ./docs/planning/migration-log.txt

echo "Migration completed. Please:"
echo "1. Update imports across the codebase"
echo "2. Run tests to confirm no regressions"
echo "3. Update documentation status"
