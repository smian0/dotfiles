#!/bin/bash

# Sync user MCP configuration to dotfiles for version control
# Usage: sync-mcp-to-dotfiles.sh [--dry-run] [--backup]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default paths
USER_MCP="${HOME}/.claude/.mcp.json"
DOTFILES_MCP="${HOME}/dotfiles/claude/.claude/.mcp.json"

# Options
DRY_RUN=false
BACKUP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --backup)
            BACKUP=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check if source exists
if [[ ! -f "$USER_MCP" ]]; then
    echo -e "${RED}✗ Source file not found: $USER_MCP${NC}"
    exit 1
fi

# Check if destination directory exists
DOTFILES_DIR=$(dirname "$DOTFILES_MCP")
if [[ ! -d "$DOTFILES_DIR" ]]; then
    echo -e "${RED}✗ Dotfiles directory not found: $DOTFILES_DIR${NC}"
    exit 1
fi

# Validate JSON syntax
if ! jq empty "$USER_MCP" 2>/dev/null; then
    echo -e "${RED}✗ Invalid JSON syntax in $USER_MCP${NC}"
    exit 1
fi

# Check if files are different
if [[ -f "$DOTFILES_MCP" ]]; then
    if diff -q "$USER_MCP" "$DOTFILES_MCP" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Files are already in sync${NC}"
        exit 0
    fi
fi

# Show differences
if [[ -f "$DOTFILES_MCP" ]]; then
    echo -e "${BLUE}Changes to be synced:${NC}"
    echo ""

    # Show server differences
    USER_SERVERS=$(jq -r '.mcpServers | keys[]' "$USER_MCP" | sort)
    DOTFILES_SERVERS=$(jq -r '.mcpServers | keys[]' "$DOTFILES_MCP" | sort)

    # Servers added in user config
    ADDED=$(comm -23 <(echo "$USER_SERVERS") <(echo "$DOTFILES_SERVERS"))
    if [[ -n "$ADDED" ]]; then
        echo -e "${GREEN}Added servers:${NC}"
        echo "$ADDED" | while read -r server; do
            echo "  + $server"
        done
        echo ""
    fi

    # Servers removed from user config
    REMOVED=$(comm -13 <(echo "$USER_SERVERS") <(echo "$DOTFILES_SERVERS"))
    if [[ -n "$REMOVED" ]]; then
        echo -e "${RED}Removed servers:${NC}"
        echo "$REMOVED" | while read -r server; do
            echo "  - $server"
        done
        echo ""
    fi

    # Servers with modified configs
    COMMON=$(comm -12 <(echo "$USER_SERVERS") <(echo "$DOTFILES_SERVERS"))
    MODIFIED=""
    for server in $COMMON; do
        USER_CONFIG=$(jq -S ".mcpServers[\"$server\"]" "$USER_MCP")
        DOTFILES_CONFIG=$(jq -S ".mcpServers[\"$server\"]" "$DOTFILES_MCP")
        if [[ "$USER_CONFIG" != "$DOTFILES_CONFIG" ]]; then
            MODIFIED="$MODIFIED $server"
        fi
    done

    if [[ -n "$MODIFIED" ]]; then
        echo -e "${YELLOW}Modified servers:${NC}"
        for server in $MODIFIED; do
            echo "  ~ $server"
        done
        echo ""
    fi
fi

# Dry run mode
if [[ "$DRY_RUN" = true ]]; then
    echo -e "${YELLOW}[DRY RUN] Would copy:${NC}"
    echo "  From: $USER_MCP"
    echo "  To:   $DOTFILES_MCP"
    exit 0
fi

# Create backup if requested
if [[ "$BACKUP" = true ]] && [[ -f "$DOTFILES_MCP" ]]; then
    BACKUP_FILE="${DOTFILES_MCP}.backup-$(date +%Y%m%d_%H%M%S)"
    cp "$DOTFILES_MCP" "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
fi

# Perform sync
cp "$USER_MCP" "$DOTFILES_MCP"

# Verify sync
if diff -q "$USER_MCP" "$DOTFILES_MCP" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Successfully synced MCP configuration to dotfiles${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git diff $DOTFILES_MCP"
    echo "  2. Commit changes: git add $DOTFILES_MCP && git commit -m 'feat: update MCP config'"
    echo "  3. Push changes: git push"
else
    echo -e "${RED}✗ Sync verification failed${NC}"
    exit 1
fi
