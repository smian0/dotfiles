#!/bin/bash
# Wrapper script that combines claudia-statusline with current prompt display
# Line 1: claudia-statusline output
# Line 2: Current prompt preview

# Run claudia-statusline and capture output
line1=$(/Users/smian/.local/bin/statusline "$@")

# Get current prompt from capture-prompt.py output
project_id=$(basename "$(pwd)" | tr '/' '-' | tr ' ' '_')
prompt_file="/tmp/claude-${project_id}-current-prompt.txt"

if [ -f "$prompt_file" ] && [ -s "$prompt_file" ]; then
    # Read prompt and truncate to 150 characters
    prompt=$(head -c 150 "$prompt_file")
    # Add icon and format
    line2="💬 ${prompt}..."
else
    # No prompt file or empty - show placeholder
    line2="💬 Ready"
fi

# Output both lines
echo "$line1"
echo "$line2"
