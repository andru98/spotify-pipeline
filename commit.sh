#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-update project}"

cd "$(dirname "$0")"

git add .
git commit -m "$MESSAGE"

echo "Committed successfully."
