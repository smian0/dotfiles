#!/bin/bash

# Check if MCP configurations are in sync
# This script compares ~/.claude.json with .mcp.json and reports differences

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Default paths
SOURCE="${HOME}/.claude.json"
TARGET="${DOTFILES_DIR}/claude/.claude/.mcp.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if files exist
if [[ ! -f "$SOURCE" ]]; then
    echo -e "${RED}Source file not found: $SOURCE${NC}"
    exit 1
fi

if [[ ! -f "$TARGET" ]]; then
    echo -e "${YELLOW}Target file not found: $TARGET${NC}"
    echo -e "${YELLOW}Run 'mcp-sync.sh' to create it${NC}"
    exit 1
fi

# Extract and compare MCP servers
SOURCE_SERVERS=$(jq -S '.mcpServers' "$SOURCE" 2>/dev/null || echo "{}")
TARGET_SERVERS=$(jq -S '.mcpServers' "$TARGET" 2>/dev/null || echo "{}")

if [[ "$SOURCE_SERVERS" == "$TARGET_SERVERS" ]]; then
    echo -e "${GREEN}✓ MCP configurations are in sync${NC}"
    
    # Show server count
    SERVER_COUNT=$(jq '.mcpServers | length' "$TARGET")
    echo -e "${GREEN}  Total servers: $SERVER_COUNT${NC}"
    
    exit 0
else
    echo -e "${YELLOW}⚠ MCP configurations are out of sync${NC}"
    echo ""
    
    # Show which servers differ
    SOURCE_KEYS=$(jq -r '.mcpServers | keys[]' "$SOURCE" 2>/dev/null | sort)
    TARGET_KEYS=$(jq -r '.mcpServers | keys[]' "$TARGET" 2>/dev/null | sort)
    
    # Find servers only in source
    ONLY_SOURCE=$(comm -23 <(echo "$SOURCE_KEYS") <(echo "$TARGET_KEYS"))
    if [[ -n "$ONLY_SOURCE" ]]; then
        echo -e "${YELLOW}Servers only in ~/.claude.json:${NC}"
        echo "$ONLY_SOURCE" | while read -r server; do
            echo "  + $server"
        done
        echo ""
    fi
    
    # Find servers only in target
    ONLY_TARGET=$(comm -13 <(echo "$SOURCE_KEYS") <(echo "$TARGET_KEYS"))
    if [[ -n "$ONLY_TARGET" ]]; then
        echo -e "${YELLOW}Servers only in .mcp.json:${NC}"
        echo "$ONLY_TARGET" | while read -r server; do
            echo "  - $server"
        done
        echo ""
    fi
    
    # Check for configuration differences in common servers
    COMMON=$(comm -12 <(echo "$SOURCE_KEYS") <(echo "$TARGET_KEYS"))
    DIFFER=""
    for server in $COMMON; do
        SOURCE_CONFIG=$(jq -S ".mcpServers[\"$server\"]" "$SOURCE")
        TARGET_CONFIG=$(jq -S ".mcpServers[\"$server\"]" "$TARGET")
        if [[ "$SOURCE_CONFIG" != "$TARGET_CONFIG" ]]; then
            DIFFER="$DIFFER $server"
        fi
    done
    
    if [[ -n "$DIFFER" ]]; then
        echo -e "${YELLOW}Servers with different configurations:${NC}"
        for server in $DIFFER; do
            echo "  ≠ $server"
        done
        echo ""
    fi
    
    echo -e "${YELLOW}Run 'mcp-sync.sh' to synchronize${NC}"
    exit 1
fi