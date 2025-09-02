#!/bin/bash
# Set MCP Environment Variables System-Wide using launchctl
# This script sets environment variables that persist across sessions
# Usage: ./scripts/set-mcp-env-system.sh

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[MCP-System] Setting environment variables system-wide...${NC}"

# Function to set environment variable using launchctl
set_env_var() {
    local var_name="$1"
    local var_value="$2"
    local description="$3"
    
    if [[ -n "$var_value" ]]; then
        launchctl setenv "$var_name" "$var_value"
        echo -e "${GREEN}✓${NC} Set $description"
    else
        echo -e "${YELLOW}⚠${NC}  $description not available (empty value)"
    fi
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/env-mapping.conf"

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}[MCP-System] Error: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}[MCP-System] Loading credentials from pass using config: $CONFIG_FILE${NC}"

# Read the configuration file and process each mapping
while IFS='=' read -r env_var pass_path || [[ -n "$env_var" ]]; do
    # Skip empty lines and comments
    if [[ -z "$env_var" || "$env_var" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Remove any whitespace
    env_var=$(echo "$env_var" | xargs)
    pass_path=$(echo "$pass_path" | xargs)
    
    if [[ -n "$env_var" && -n "$pass_path" ]]; then
        # Get the credential from pass
        credential_value=$(pass show "$pass_path" 2>/dev/null | tr -d '\n\r' | xargs || echo "")
        
        # Set the environment variable
        set_env_var "$env_var" "$credential_value" "$env_var"
    fi
done < "$CONFIG_FILE"

echo -e "${GREEN}[MCP-System] Environment variables set successfully!${NC}"
echo -e "${YELLOW}[MCP-System] These variables are now available system-wide for all processes${NC}"
echo -e "${YELLOW}[MCP-System] No shell sourcing required - MCP servers will read them automatically${NC}"

# Show current environment variables
echo -e "${GREEN}[MCP-System] Current system environment variables:${NC}"
launchctl getenv OPENAI_API_KEY | sed 's/.*/OPENAI_API_KEY=***/' || echo "OPENAI_API_KEY not set"
launchctl getenv GITHUB_TOKEN | sed 's/.*/GITHUB_TOKEN=***/' || echo "GITHUB_TOKEN not set"
launchctl getenv OLLAMA_API_KEY | sed 's/.*/OLLAMA_API_KEY=***/' || echo "OLLAMA_API_KEY not set"
launchctl getenv DEEPSEEK_API_KEY | sed 's/.*/DEEPSEEK_API_KEY=***/' || echo "DEEPSEEK_API_KEY not set"
launchctl getenv GLM_API_KEY | sed 's/.*/GLM_API_KEY=***/' || echo "GLM_API_KEY not set"

echo -e "${GREEN}[MCP-System] Ready for MCP servers!${NC}"
