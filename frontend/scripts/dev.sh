#!/bin/zsh
cd "$(dirname "$0")/.."
case "$1" in
  fetch-schema) npx ts-node src/api/schema/fetch-schema.ts ;;
  generate-types) npm run generate-types ;;
  storybook) npm run storybook ;;
  *) echo "Usage: $0 {fetch-schema|generate-types|storybook}" ;;
esac
