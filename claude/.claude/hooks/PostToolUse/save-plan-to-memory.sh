#!/usr/bin/env bash
# PostToolUse hook for ExitPlanMode
# Automatically saves plan content to Serena memory after exiting plan mode

set -euo pipefail

# Read JSON input from stdin
INPUT=$(cat)

# Debug: Log the raw input for troubleshooting
echo "$INPUT" >> /tmp/claude-exitplanmode-hook-debug.log
echo "---" >> /tmp/claude-exitplanmode-hook-debug.log

# Extract the plan content from ExitPlanMode tool input
# Try both field names (tool_input.plan and input.plan) for compatibility
PLAN=$(echo "$INPUT" | jq -r '.tool_input.plan // .input.plan // empty')

# Only proceed if we have plan content
if [[ -z "$PLAN" || "$PLAN" == "null" ]]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# Get current working directory from hook input
CWD=$(echo "$INPUT" | jq -r '.cwd // "."')

# Generate filename with date and short description
DATE=$(date +%Y-%m-%d)

# Extract title (remove markdown heading prefix like # or ##)
TITLE=$(echo "$PLAN" | head -n 1 | sed 's/^#\+\s*//')

# Sanitize: lowercase, replace non-alphanumeric with dashes, collapse multiple dashes
SANITIZED=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g')

# Truncate to 80 chars
TRUNCATED=$(echo "$SANITIZED" | cut -c1-80)

# If we truncated, find the last complete word (cut at last dash)
if [ ${#SANITIZED} -gt 80 ]; then
  SHORT_DESC=$(echo "$TRUNCATED" | sed 's/-[^-]*$//')
else
  SHORT_DESC="$TRUNCATED"
fi

# Strip leading and trailing dashes
SHORT_DESC=$(echo "$SHORT_DESC" | sed 's/^-*//' | sed 's/-*$//')

FILENAME="plan_${DATE}_${SHORT_DESC}.md"

# Create memory directory if it doesn't exist
MEMORY_DIR="${CWD}/.serena/memories"
mkdir -p "$MEMORY_DIR"

# Format plan content with metadata
cat > "${MEMORY_DIR}/${FILENAME}" <<EOF
# Plan: $(echo "$PLAN" | head -n 1)
**Date**: $(date +%Y-%m-%d\ %H:%M)
**Status**: Approved, ready for implementation
**Saved by**: PostToolUse hook (ExitPlanMode)

---

$PLAN

---

**Implementation Notes**:
- This plan was approved and saved automatically
- Track progress by updating task checkboxes
- Mark status as "In Progress" or "Completed" as work proceeds
EOF

# Output success message to Claude via additionalContext
cat <<EOF
{
  "decision": "allow",
  "additionalContext": "✅ Plan saved to .serena/memories/${FILENAME} for future reference."
}
EOF
