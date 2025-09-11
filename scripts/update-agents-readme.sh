#!/usr/bin/env bash

# Script to dynamically update README.md with available OpenCode agents
# This extracts agents from the OpenCode configuration and updates the README

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
DOTFILES_DIR="${HOME}/dotfiles"
OPENCODE_CONFIG="${DOTFILES_DIR}/opencode/.config/opencode/opencode.json"
AGENT_DIR="${DOTFILES_DIR}/opencode/.config/opencode/agent"
README="${DOTFILES_DIR}/README.md"
WORKFLOW_FILE="${DOTFILES_DIR}/.github/workflows/opencode.yml"

# Function to get emoji for agent from workflow file
get_agent_emoji() {
    local agent_name="$1"
    case "$agent_name" in
        news) echo "📰" ;;
        reasoning) echo "🧠" ;;
        websearch) echo "🔍" ;;
        markdown-pro) echo "📝" ;;
        helper) echo "🛠️" ;;
        review) echo "👁️" ;;
        plan) echo "📋" ;;
        build) echo "🏗️" ;;
        general) echo "🎯" ;;
        *) echo "🤖" ;;
    esac
}

# Function to get agent description
get_agent_description() {
    local agent_name="$1"
    case "$agent_name" in
        news) echo "Aggregates and summarizes latest news from multiple sources" ;;
        reasoning) echo "Provides step-by-step reasoning for complex problems" ;;
        websearch) echo "Searches the web and provides concise summaries" ;;
        markdown-pro) echo "Specialized markdown formatting and documentation" ;;
        helper) echo "General assistance and utility functions" ;;
        review) echo "Code review and analysis capabilities" ;;
        plan) echo "Strategic planning and project organization" ;;
        build) echo "Build automation and deployment assistance" ;;
        general) echo "General-purpose AI assistance" ;;
        *) echo "Custom agent for specialized tasks" ;;
    esac
}

# Extract agents from config
echo -e "${YELLOW}Extracting agents from OpenCode configuration...${NC}"

# Create temporary file for the agents section
TEMP_AGENTS=$(mktemp)

cat > "$TEMP_AGENTS" << 'EOF'
## OpenCode GitHub Bot

This repository includes an AI-powered GitHub bot that responds to commands in issue comments. Trigger it using `/oc` or `/opencode` in any issue or PR comment.

### Available Agents

| Agent | Trigger | Description |
|-------|---------|-------------|
EOF

# Extract agents from opencode.json using jq
if command -v jq &> /dev/null; then
    # Use jq to parse JSON
    agents=$(jq -r '.agent | keys[]' "$OPENCODE_CONFIG" 2>/dev/null | sort)
else
    # Fallback to grep/sed if jq is not available
    agents=$(grep -E '^\s*"[^"]+"\s*:\s*\{' "$OPENCODE_CONFIG" | \
             sed -n 's/^\s*"\([^"]*\)"\s*:.*/\1/p' | \
             grep -v -E '^(model|system|temperature|reasoningEffort|tools)$' | \
             sort)
fi

# Add each agent to the table
for agent in $agents; do
    emoji=$(get_agent_emoji "$agent")
    description=$(get_agent_description "$agent")
    agent_display=$(echo "$agent" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
    echo "| $emoji **${agent_display}** | \`/oc @${agent}\` | ${description} |" >> "$TEMP_AGENTS"
done

# Also check for agent files that might not be in config
if [ -d "$AGENT_DIR" ]; then
    for agent_file in "$AGENT_DIR"/*.md; do
        if [ -f "$agent_file" ]; then
            agent_name=$(basename "$agent_file" .md)
            # Check if agent is already in list
            if ! echo "$agents" | grep -q "^${agent_name}$"; then
                emoji=$(get_agent_emoji "$agent_name")
                description=$(get_agent_description "$agent_name")
                agent_display=$(echo "$agent_name" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
                echo "| $emoji **${agent_display}** | \`/oc @${agent_name}\` | ${description} |" >> "$TEMP_AGENTS"
            fi
        fi
    done
fi

cat >> "$TEMP_AGENTS" << 'EOF'

### Usage Examples

```bash
# Get latest news
/oc @news get latest tech news

# Reasoning through a problem
/oc @reasoning explain the halting problem

# Search the web
/oc @websearch latest AI developments

# General query (no agent)
/oc what is the capital of France?
```
EOF

# Create backup of README
cp "$README" "${README}.backup"

# Update README - remove old OpenCode section and insert new one
echo -e "${YELLOW}Updating README.md...${NC}"

# Use awk to replace the section
awk '
BEGIN { in_section = 0; printed = 0 }
/^## OpenCode GitHub Bot/ { in_section = 1; next }
/^## / && in_section { in_section = 0 }
!in_section && !printed { print }
/^## License/ && !printed { 
    while ((getline line < "'"$TEMP_AGENTS"'") > 0) {
        print line
    }
    print ""
    printed = 1
    print
}
' "$README" > "${README}.tmp"

# Move the updated file
mv "${README}.tmp" "$README"

# Clean up
rm -f "$TEMP_AGENTS"

echo -e "${GREEN}✅ README.md updated successfully with latest agents!${NC}"

# Show what agents were found
echo -e "${GREEN}Found agents:${NC}"
for agent in $agents; do
    emoji=$(get_agent_emoji "$agent")
    echo "  $emoji $agent"
done