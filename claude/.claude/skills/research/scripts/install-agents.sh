#!/bin/bash
# Install research skill agents by symlinking to ~/.claude/agents/

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="$HOME/.claude/agents"
SKILL_AGENTS_DIR="$SKILL_DIR/agents"

echo "Installing research skill agents..."
echo "Skill directory: $SKILL_DIR"
echo "Target agents directory: $AGENTS_DIR"
echo ""

# Ensure agents directory exists
mkdir -p "$AGENTS_DIR"

# Counter for successful installations
installed=0

# Symlink each agent file
for agent_file in "$SKILL_AGENTS_DIR"/*.md; do
    # Skip README
    if [[ "$(basename "$agent_file")" == "README.md" ]]; then
        continue
    fi

    agent_name=$(basename "$agent_file")
    target="$AGENTS_DIR/$agent_name"

    # Remove existing symlink or file if it exists
    if [[ -L "$target" ]]; then
        echo "   ⚠️  Removing existing symlink: $agent_name"
        rm "$target"
    elif [[ -f "$target" ]]; then
        echo "   ⚠️  WARNING: Regular file exists at $agent_name (not removing)"
        echo "      Please remove manually if you want to replace it"
        continue
    fi

    # Create relative symlink
    # From ~/.claude/agents/ to ~/.claude/skills/research/agents/
    ln -s "../skills/research/agents/$agent_name" "$target"
    echo "   ✅ Linked: $agent_name"
    ((installed++))
done

echo ""
echo "✅ Installation complete: $installed agents linked"
echo ""
echo "Installed agents:"
ls -la "$AGENTS_DIR"/research-*.md | awk '{print "   - " $NF}'
