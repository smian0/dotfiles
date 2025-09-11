#!/usr/bin/env bash

# Generate a JSON file with all available agents
# This can be consumed by GitHub Actions, badges, or other tools

set -euo pipefail

# Paths - detect if we're in CI or local environment
if [ -n "${GITHUB_WORKSPACE:-}" ]; then
    # GitHub Actions environment
    DOTFILES_DIR="${GITHUB_WORKSPACE}"
elif [ -d "${HOME}/dotfiles" ]; then
    # Local environment with dotfiles in home
    DOTFILES_DIR="${HOME}/dotfiles"
elif [ -d "$(pwd)/opencode" ]; then
    # We're already in the dotfiles directory
    DOTFILES_DIR="$(pwd)"
else
    # Fallback to current directory
    DOTFILES_DIR="$(pwd)"
fi

OPENCODE_CONFIG="${DOTFILES_DIR}/opencode/.config/opencode/opencode.json"
AGENT_DIR="${DOTFILES_DIR}/opencode/.config/opencode/agent"
OUTPUT_FILE="${DOTFILES_DIR}/agents.json"

# Function to get emoji for agent
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

# Start JSON
echo "{" > "$OUTPUT_FILE"
echo '  "updated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",' >> "$OUTPUT_FILE"
echo '  "agents": [' >> "$OUTPUT_FILE"

# Extract agents
if command -v jq &> /dev/null; then
    agents=$(jq -r '.agent | keys[]' "$OPENCODE_CONFIG" 2>/dev/null | sort)
else
    agents=$(grep -E '^\s*"[^"]+"\s*:\s*\{' "$OPENCODE_CONFIG" | \
             sed -n 's/^\s*"\([^"]*\)"\s*:.*/\1/p' | \
             grep -v -E '^(model|system|temperature|reasoningEffort|tools)$' | \
             sort)
fi

first=true
for agent in $agents; do
    if [ "$first" = false ]; then
        echo "," >> "$OUTPUT_FILE"
    fi
    first=false
    
    emoji=$(get_agent_emoji "$agent")
    description=$(get_agent_description "$agent")
    
    cat >> "$OUTPUT_FILE" << EOF
    {
      "name": "$agent",
      "emoji": "$emoji",
      "trigger": "/oc @$agent",
      "description": "$description"
    }
EOF
done

echo "" >> "$OUTPUT_FILE"
echo "  ]" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo "Generated agents.json with $(echo "$agents" | wc -w) agents"