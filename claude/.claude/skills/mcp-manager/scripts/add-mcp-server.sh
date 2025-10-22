#!/bin/bash

# Interactive wizard to add a new MCP server
# Usage: add-mcp-server.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
prompt() {
    local prompt_text="$1"
    local default_value="$2"
    local result

    if [[ -n "$default_value" ]]; then
        echo -en "${CYAN}${prompt_text} [${default_value}]: ${NC}"
    else
        echo -en "${CYAN}${prompt_text}: ${NC}"
    fi

    read -r result
    if [[ -z "$result" ]] && [[ -n "$default_value" ]]; then
        echo "$default_value"
    else
        echo "$result"
    fi
}

confirm() {
    local prompt_text="$1"
    local response
    echo -en "${YELLOW}${prompt_text} (y/n): ${NC}"
    read -r response
    [[ "$response" =~ ^[Yy]$ ]]
}

# Banner
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     MCP Server Configuration Wizard      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Determine scope
echo -e "${CYAN}Where should this server be configured?${NC}"
echo "  1) User level (~/.claude/.mcp.json) - Available globally"
echo "  2) Project level (./.claude/.mcp.json) - Project-specific"
echo ""
scope=$(prompt "Select scope (1 or 2)" "1")

case $scope in
    1)
        MCP_FILE="${HOME}/.claude/.mcp.json"
        SCOPE_NAME="user"
        ;;
    2)
        MCP_FILE="./.claude/.mcp.json"
        SCOPE_NAME="project"
        ;;
    *)
        echo -e "${RED}Invalid scope selection${NC}"
        exit 1
        ;;
esac

# Create file if it doesn't exist
if [[ ! -f "$MCP_FILE" ]]; then
    mkdir -p "$(dirname "$MCP_FILE")"
    echo '{"mcpServers":{}}' > "$MCP_FILE"
    echo -e "${GREEN}✓ Created new configuration file: $MCP_FILE${NC}"
    echo ""
fi

# Validate existing JSON
if ! jq empty "$MCP_FILE" 2>/dev/null; then
    echo -e "${RED}✗ Invalid JSON in existing file: $MCP_FILE${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}═══ Server Configuration ═══${NC}"
echo ""

# Server name
while true; do
    SERVER_NAME=$(prompt "Server name (e.g., my-server)")

    if [[ -z "$SERVER_NAME" ]]; then
        echo -e "${RED}Server name cannot be empty${NC}"
        continue
    fi

    # Check for existing server
    if jq -e ".mcpServers[\"$SERVER_NAME\"]" "$MCP_FILE" >/dev/null 2>&1; then
        echo -e "${RED}✗ Server '$SERVER_NAME' already exists${NC}"
        if confirm "Overwrite existing server?"; then
            break
        fi
        continue
    fi

    break
done

# Command
echo ""
echo -e "${CYAN}Common commands:${NC}"
echo "  1) npx      - Node packages (most common)"
echo "  2) uvx      - Python packages via uv"
echo "  3) python3  - Direct Python script"
echo "  4) node     - Direct Node script"
echo "  5) custom   - Custom command"
echo ""
cmd_choice=$(prompt "Select command (1-5)" "1")

case $cmd_choice in
    1) COMMAND="npx" ;;
    2) COMMAND="uvx" ;;
    3) COMMAND="python3" ;;
    4) COMMAND="node" ;;
    5) COMMAND=$(prompt "Enter custom command") ;;
    *) COMMAND="npx" ;;
esac

# Arguments
echo ""
echo -e "${CYAN}Command arguments (space-separated):${NC}"
if [[ "$COMMAND" == "npx" ]]; then
    echo "  Example: -y @package/name"
elif [[ "$COMMAND" == "uvx" ]]; then
    echo "  Example: --from git+https://github.com/user/repo package-name"
fi
ARGS=$(prompt "Arguments")

# Convert args string to JSON array
if [[ -n "$ARGS" ]]; then
    # Split args by space and convert to JSON array
    IFS=' ' read -ra ARG_ARRAY <<< "$ARGS"
    ARGS_JSON=$(printf '%s\n' "${ARG_ARRAY[@]}" | jq -R . | jq -s .)
else
    ARGS_JSON="[]"
fi

# Description
echo ""
DESCRIPTION=$(prompt "Server description (what does it do?)")

# Type
echo ""
TYPE=$(prompt "Server type" "stdio")

# Environment variables
echo ""
echo -e "${CYAN}Environment variables (optional):${NC}"
echo "  Format: KEY=value"
echo "  Enter blank line when done"
echo ""

ENV_VARS="{}"
while true; do
    ENV_VAR=$(prompt "Environment variable" "")

    if [[ -z "$ENV_VAR" ]]; then
        break
    fi

    if [[ ! "$ENV_VAR" =~ ^[A-Za-z_][A-Za-z0-9_]*=.+$ ]]; then
        echo -e "${RED}Invalid format. Use: KEY=value${NC}"
        continue
    fi

    KEY="${ENV_VAR%%=*}"
    VALUE="${ENV_VAR#*=}"

    ENV_VARS=$(echo "$ENV_VARS" | jq --arg k "$KEY" --arg v "$VALUE" '. + {($k): $v}')
done

# Auto-restart option
echo ""
if confirm "Enable auto-restart for development?"; then
    ENV_VARS=$(echo "$ENV_VARS" | jq '. + {"MCPDEV_PROXY_AUTO_RESTART": "true"}')

    # Wrap command with reloaderoo if not already
    if [[ "$COMMAND" != *"reloaderoo"* ]]; then
        ORIGINAL_COMMAND="$COMMAND"
        ORIGINAL_ARGS="$ARGS"

        COMMAND="npx"
        # Build new args array: ["reloaderoo", "proxy", "--", original_command, ...original_args]
        ARGS_JSON=$(jq -n --arg cmd "$ORIGINAL_COMMAND" --argjson args "$ARGS_JSON" '["reloaderoo", "proxy", "--", $cmd] + $args')

        echo -e "${GREEN}✓ Auto-restart enabled with reloaderoo${NC}"
    fi
fi

# Build server JSON
SERVER_JSON=$(jq -n \
    --arg cmd "$COMMAND" \
    --argjson args "$ARGS_JSON" \
    --arg type "$TYPE" \
    --arg desc "$DESCRIPTION" \
    --argjson env "$ENV_VARS" \
    '{
        command: $cmd,
        args: $args,
        type: $type,
        description: $desc,
        env: $env
    }')

# Preview
echo ""
echo -e "${BLUE}═══ Configuration Preview ═══${NC}"
echo ""
echo -e "${CYAN}Server name:${NC} $SERVER_NAME"
echo -e "${CYAN}Scope:${NC} $SCOPE_NAME"
echo -e "${CYAN}Configuration:${NC}"
echo "$SERVER_JSON" | jq .
echo ""

# Confirm
if ! confirm "Add this server configuration?"; then
    echo -e "${YELLOW}Cancelled${NC}"
    exit 0
fi

# Add to config
jq --arg name "$SERVER_NAME" --argjson config "$SERVER_JSON" \
    '.mcpServers[$name] = $config' \
    "$MCP_FILE" > "${MCP_FILE}.tmp"

mv "${MCP_FILE}.tmp" "$MCP_FILE"

echo ""
echo -e "${GREEN}✓ Server '$SERVER_NAME' added successfully${NC}"
echo ""
echo -e "${YELLOW}Important next steps:${NC}"
echo "  1. Add tool permissions to settings.json:"
echo "     Format: mcp__${SERVER_NAME}__<tool-name>"
echo ""
echo "  2. Restart Claude Code to load the new server"
echo ""
echo "  3. Test the server:"
echo "     - Check that it appears in available MCP servers"
echo "     - Try using its tools"
echo ""

if [[ "$SCOPE_NAME" == "user" ]]; then
    echo "  4. Sync to dotfiles (optional):"
    echo "     ~/dotfiles/claude/.claude/skills/mcp-manager/scripts/sync-mcp-to-dotfiles.sh"
    echo ""
fi

# Show server location
echo -e "${CYAN}Configuration saved to:${NC} $MCP_FILE"
