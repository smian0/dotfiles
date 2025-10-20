#!/bin/bash
# Uninstall research skill agents by removing symlinks from ~/.claude/agents/

set -euo pipefail

AGENTS_DIR="$HOME/.claude/agents"

echo "Uninstalling research skill agents..."
echo "Agents directory: $AGENTS_DIR"
echo ""

# Counter for successful removals
removed=0

# Remove each research-* agent symlink
for agent_link in "$AGENTS_DIR"/research-*.md; do
    # Check if file exists (glob might not match anything)
    if [[ ! -e "$agent_link" ]]; then
        continue
    fi

    agent_name=$(basename "$agent_link")

    # Only remove if it's a symlink
    if [[ -L "$agent_link" ]]; then
        rm "$agent_link"
        echo "   ✅ Removed: $agent_name"
        ((removed++))
    elif [[ -f "$agent_link" ]]; then
        echo "   ⚠️  WARNING: $agent_name is a regular file (not a symlink)"
        echo "      Skipping removal - please remove manually if needed"
    fi
done

echo ""
if [[ $removed -eq 0 ]]; then
    echo "ℹ️  No research skill agent symlinks found to remove"
else
    echo "✅ Uninstallation complete: $removed agents removed"
fi
