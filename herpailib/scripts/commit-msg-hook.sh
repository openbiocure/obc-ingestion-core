#!/bin/bash

# Enforce Conventional Commit format: type: subject
COMMIT_MSG_FILE=$1
COMMIT_MSG=$(head -n1 "$COMMIT_MSG_FILE")

# Regex for allowed commit message format (e.g., docs:, feat:, fix:, chore:, etc.)
PATTERN="^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert|meta)(\([a-zA-Z0-9\-]+\))?: .{1,100}$"

if [[ ! "$COMMIT_MSG" =~ $PATTERN ]]; then
  echo "❌ Commit message format invalid!"
  echo "✅ Expected format: <type>(optional-scope): <subject>"
  echo "   Example: docs(readme): add roadmap link at top of README"
  exit 1
fi