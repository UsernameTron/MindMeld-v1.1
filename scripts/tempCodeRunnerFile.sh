#!/usr/bin/env bash
set -e
MSG=${1:-"Auto-commit from agent"}
git add .
git commit -m "$MSG"
git push -u origin main
