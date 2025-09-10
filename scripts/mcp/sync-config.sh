#!/bin/bash

# Sync MCP configuration from ~/.claude.json to .mcp.json files
# This script extracts MCP server configurations from Claude's main config
# and syncs them to the appropriate .mcp.json files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/extract-mcp-config.py"
DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Sync MCP server configurations from ~/.claude.json to .mcp.json

Options:
    -t, --target PATH    Target .mcp.json file (default: ~/dotfiles/claude/.claude/.mcp.json)
    -s, --source PATH    Source claude.json file (default: ~/.claude.json)
    -l, --list           List available MCP servers
    -v, --verbose        Enable verbose output
    -h, --help           Show this help

Examples:
    $(basename "$0")                    # Sync to default location
    $(basename "$0") -v                 # Sync with verbose output
    $(basename "$0") -l                 # List available servers
    $(basename "$0") -t /path/to/.mcp.json  # Sync to custom location

EOF
}

# Default values
TARGET="$DOTFILES_DIR/claude/.claude/.mcp.json"
SOURCE="$HOME/.claude.json"
VERBOSE=false
LIST_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -s|--source)
            SOURCE="$2"
            shift 2
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Check if source file exists
if [[ ! -f "$SOURCE" ]]; then
    echo -e "${RED}Error: Source file not found: $SOURCE${NC}"
    exit 1
fi

# Check if Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}Error: Python script not found: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# List servers if requested
if [[ "$LIST_ONLY" == "true" ]]; then
    python3 "$PYTHON_SCRIPT" --claude-config "$SOURCE" --list-only
    exit 0
fi

# Perform sync
echo -e "${YELLOW}Syncing MCP configuration...${NC}"
echo "Source: $SOURCE"
echo "Target: $TARGET"

if [[ "$VERBOSE" == "true" ]]; then
    python3 "$PYTHON_SCRIPT" --sync --claude-config "$SOURCE" --output "$TARGET" --verbose
else
    python3 "$PYTHON_SCRIPT" --sync --claude-config "$SOURCE" --output "$TARGET"
fi

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓ MCP configuration synced successfully${NC}"
    
    # Show summary
    if command -v jq &> /dev/null && [[ -f "$TARGET" ]]; then
        SERVER_COUNT=$(jq '.mcpServers | length' "$TARGET")
        echo -e "${GREEN}Total MCP servers: $SERVER_COUNT${NC}"
        
        if [[ "$VERBOSE" == "true" ]]; then
            echo -e "\n${YELLOW}Configured servers:${NC}"
            jq -r '.mcpServers | keys[]' "$TARGET" | while read -r server; do
                echo "  • $server"
            done
        fi
    fi
else
    echo -e "${RED}✗ Failed to sync MCP configuration${NC}"
    exit 1
fi