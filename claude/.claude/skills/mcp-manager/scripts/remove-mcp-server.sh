#!/bin/bash

# Safely remove an MCP server from configuration
# Usage: remove-mcp-server.sh <server-name> [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Options
KEEP_PERMISSIONS=false
FORCE=false
SCOPE="user"

# Usage
usage() {
    echo "Usage: $0 <server-name> [options]"
    echo ""
    echo "Options:"
    echo "  --project          Remove from project config instead of user"
    echo "  --keep-permissions Keep permissions in settings.json"
    echo "  --force            Skip confirmation prompts"
    echo "  -h, --help         Show this help"
    exit 1
}

# Parse arguments
if [[ $# -eq 0 ]]; then
    usage
fi

SERVER_NAME="$1"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            SCOPE="project"
            shift
            ;;
        --keep-permissions)
            KEEP_PERMISSIONS=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Determine file paths
if [[ "$SCOPE" == "project" ]]; then
    MCP_FILE="./.claude/.mcp.json"
    SETTINGS_FILE="./.claude/settings.json"
else
    MCP_FILE="${HOME}/.claude/.mcp.json"
    SETTINGS_FILE="${HOME}/.claude/settings.json"
fi

# Check if files exist
if [[ ! -f "$MCP_FILE" ]]; then
    echo -e "${RED}✗ Configuration file not found: $MCP_FILE${NC}"
    exit 1
fi

# Check if server exists
if ! jq -e ".mcpServers[\"$SERVER_NAME\"]" "$MCP_FILE" >/dev/null 2>&1; then
    echo -e "${RED}✗ Server '$SERVER_NAME' not found in $MCP_FILE${NC}"
    echo ""
    echo "Available servers:"
    jq -r '.mcpServers | keys[]' "$MCP_FILE" | sort | sed 's/^/  - /'
    exit 1
fi

# Show what will be removed
echo -e "${BLUE}═══ Server Removal Preview ═══${NC}"
echo ""
echo -e "${CYAN}Server name:${NC} $SERVER_NAME"
echo -e "${CYAN}Scope:${NC} $SCOPE"
echo ""
echo -e "${CYAN}Current configuration:${NC}"
jq ".mcpServers[\"$SERVER_NAME\"]" "$MCP_FILE"
echo ""

# Find related permissions
if [[ -f "$SETTINGS_FILE" ]]; then
    PERMISSIONS=$(jq -r ".permissions.allow[] | select(startswith(\"mcp__${SERVER_NAME}__\"))" "$SETTINGS_FILE" 2>/dev/null || echo "")

    if [[ -n "$PERMISSIONS" ]]; then
        echo -e "${CYAN}Related permissions (will be removed):${NC}"
        echo "$PERMISSIONS" | sed 's/^/  - /'
        echo ""
    fi
else
    echo -e "${YELLOW}⚠ Settings file not found: $SETTINGS_FILE${NC}"
    echo ""
fi

# Confirm removal
if [[ "$FORCE" != true ]]; then
    echo -en "${YELLOW}Remove server '$SERVER_NAME'? (y/n): ${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cancelled${NC}"
        exit 0
    fi
fi

# Create backup
BACKUP_MCP="${MCP_FILE}.backup-$(date +%Y%m%d_%H%M%S)"
cp "$MCP_FILE" "$BACKUP_MCP"
echo -e "${GREEN}✓ Backup created: $BACKUP_MCP${NC}"

if [[ -f "$SETTINGS_FILE" ]] && [[ "$KEEP_PERMISSIONS" != true ]]; then
    BACKUP_SETTINGS="${SETTINGS_FILE}.backup-$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$BACKUP_SETTINGS"
    echo -e "${GREEN}✓ Backup created: $BACKUP_SETTINGS${NC}"
fi

echo ""

# Remove server from .mcp.json
jq "del(.mcpServers[\"$SERVER_NAME\"])" "$MCP_FILE" > "${MCP_FILE}.tmp"
mv "${MCP_FILE}.tmp" "$MCP_FILE"
echo -e "${GREEN}✓ Removed server from $MCP_FILE${NC}"

# Remove permissions from settings.json
if [[ -f "$SETTINGS_FILE" ]] && [[ "$KEEP_PERMISSIONS" != true ]]; then
    if [[ -n "$PERMISSIONS" ]]; then
        # Build jq filter to remove each permission
        JQ_FILTER=".permissions.allow |= map(select(startswith(\"mcp__${SERVER_NAME}__\") | not))"

        jq "$JQ_FILTER" "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp"
        mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"

        REMOVED_COUNT=$(echo "$PERMISSIONS" | wc -l | tr -d ' ')
        echo -e "${GREEN}✓ Removed $REMOVED_COUNT permissions from $SETTINGS_FILE${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✓ Successfully removed server '$SERVER_NAME'${NC}"
echo ""

# Validate final state
echo -e "${CYAN}Validating configuration...${NC}"

# Check JSON syntax
if ! jq empty "$MCP_FILE" 2>/dev/null; then
    echo -e "${RED}✗ Invalid JSON in $MCP_FILE after removal${NC}"
    echo -e "${YELLOW}Restoring from backup...${NC}"
    cp "$BACKUP_MCP" "$MCP_FILE"
    exit 1
fi

if [[ -f "$SETTINGS_FILE" ]]; then
    if ! jq empty "$SETTINGS_FILE" 2>/dev/null; then
        echo -e "${RED}✗ Invalid JSON in $SETTINGS_FILE after removal${NC}"
        echo -e "${YELLOW}Restoring from backup...${NC}"
        cp "$BACKUP_SETTINGS" "$SETTINGS_FILE"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Configuration is valid${NC}"
echo ""

# Show remaining servers
REMAINING_COUNT=$(jq '.mcpServers | length' "$MCP_FILE")
echo -e "${CYAN}Remaining servers: $REMAINING_COUNT${NC}"
if [[ $REMAINING_COUNT -gt 0 ]]; then
    jq -r '.mcpServers | keys[]' "$MCP_FILE" | sort | sed 's/^/  - /'
fi

echo ""
echo -e "${YELLOW}Important next steps:${NC}"
echo "  1. Restart Claude Code to unload the removed server"
echo ""

if [[ "$KEEP_PERMISSIONS" == true ]]; then
    echo "  2. Note: Permissions were kept (--keep-permissions flag)"
    echo "     Remove manually if needed from: $SETTINGS_FILE"
    echo ""
fi

if [[ "$SCOPE" == "user" ]]; then
    echo "  2. Sync to dotfiles (optional):"
    echo "     ~/dotfiles/claude/.claude/skills/mcp-manager/scripts/sync-mcp-to-dotfiles.sh"
    echo ""
fi

echo -e "${CYAN}Backups saved:${NC}"
echo "  - $BACKUP_MCP"
if [[ -f "$BACKUP_SETTINGS" ]]; then
    echo "  - $BACKUP_SETTINGS"
fi
