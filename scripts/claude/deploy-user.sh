#!/usr/bin/env bash

# Deploy Claude user-level configuration
# Usage: ./deploy-claude-user.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo -e "${GREEN}Claude User Settings Deployment${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if stow is installed
if ! command -v stow &> /dev/null; then
    echo -e "${RED}Error: GNU Stow is not installed${NC}"
    echo "Please install stow first:"
    echo "  macOS: brew install stow"
    echo "  Linux: apt-get install stow"
    exit 1
fi

# Check if claude-user package exists
if [ ! -d "$DOTFILES_DIR/claude-user" ]; then
    echo -e "${RED}Error: claude-user package not found${NC}"
    echo "Expected location: $DOTFILES_DIR/claude-user"
    exit 1
fi

# Backup existing ~/.claude if it exists and is not a symlink
if [ -e "$HOME/.claude" ] && [ ! -L "$HOME/.claude" ]; then
    BACKUP_DIR="$HOME/.claude.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Backing up existing ~/.claude to $BACKUP_DIR${NC}"
    mv "$HOME/.claude" "$BACKUP_DIR"
fi

# Deploy using stow
echo -e "${GREEN}Deploying claude-user to home directory...${NC}"
cd "$DOTFILES_DIR"
stow -v -t "$HOME" claude-user

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Claude user settings deployed successfully!${NC}"
    echo ""
    echo "Deployed files:"
    echo "  ~/.claude/settings.json - Global user preferences"
    echo "  ~/.claude/commands/ - Personal commands"
    echo ""
    echo "These settings will apply to all Claude Code sessions"
    echo "unless overridden by project-specific settings."
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi