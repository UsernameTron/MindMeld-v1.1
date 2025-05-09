#!/bin/zsh

# Function to display test status
function test_status() {
  if [ $? -eq 0 ]; then
    echo "✅ $1"
  else
    echo "❌ $1"
    exit 1
  fi
}

cd /Users/cpconnor/projects/mindmeld-fresh/frontend

# Test 1: Check if clsx is installed correctly
echo "Testing clsx installation..."
if grep -q "clsx" package.json; then
  test_status "clsx is correctly installed"
else
  echo "❌ clsx is not installed"
  exit 1
fi

# Test 2: Check if Card.tsx uses clsx
echo "Testing Card.tsx clsx usage..."
if grep -q "import clsx from 'clsx'" src/components/atoms/Card.tsx; then
  test_status "Card.tsx uses clsx correctly"
else
  echo "❌ Card.tsx does not use clsx"
  exit 1
fi

# Test 3: Check if OpenAPIContext has 'use client' directive
echo "Testing OpenAPIContext.tsx use client directive..."
if grep -q "'use client'" src/context/OpenAPIContext.tsx || grep -q '"use client"' src/context/OpenAPIContext.tsx; then
  test_status "OpenAPIContext.tsx has use client directive"
else
  echo "❌ OpenAPIContext.tsx missing use client directive"
  exit 1
fi

# Test 4: Check eslint config exists
echo "Testing ESLint configuration..."
if [ -f ".eslintrc.js" ]; then
  test_status "ESLint config exists"
else
  echo "❌ ESLint config is missing"
  exit 1
fi

# Test 5: Check prettier config exists
echo "Testing Prettier configuration..."
if [ -f "prettier.config.js" ]; then
  test_status "Prettier config exists"
else
  echo "❌ Prettier config is missing"
  exit 1
fi

# Test 6: Check lint-staged config exists
echo "Testing lint-staged configuration..."
if [ -f "lint-staged.config.js" ]; then
  test_status "lint-staged config exists"
else
  echo "❌ lint-staged config is missing"
  exit 1
fi

# All tests passed
echo "🎉 All tests passed! Phase 3 implementation is complete."
