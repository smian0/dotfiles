#!/usr/bin/env bash

# Deploy Claude project-level configuration to a specific project
# Usage: ./deploy-claude-project.sh /path/to/project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo -e "${GREEN}Claude Project Settings Deployment${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""

# Check if target directory is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No target project directory provided${NC}"
    echo ""
    echo "Usage: $0 /path/to/project"
    echo ""
    echo "Example:"
    echo "  $0 ~/workspaces/my-project"
    exit 1
fi

TARGET_DIR="$1"

# Resolve absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
    echo -e "${RED}Error: Target directory does not exist: $1${NC}"
    exit 1
}

# Check if stow is installed
if ! command -v stow &> /dev/null; then
    echo -e "${RED}Error: GNU Stow is not installed${NC}"
    echo "Please install stow first:"
    echo "  macOS: brew install stow"
    echo "  Linux: apt-get install stow"
    exit 1
fi

# Check if claude-project package exists
if [ ! -d "$DOTFILES_DIR/claude-project" ]; then
    echo -e "${RED}Error: claude-project package not found${NC}"
    echo "Expected location: $DOTFILES_DIR/claude-project"
    exit 1
fi

echo -e "${BLUE}Target project: $TARGET_DIR${NC}"
echo ""

# Check if .claude already exists in target
if [ -e "$TARGET_DIR/.claude" ]; then
    if [ -L "$TARGET_DIR/.claude" ]; then
        echo -e "${YELLOW}Warning: .claude is already a symlink in target directory${NC}"
        echo "It will be replaced with the new configuration."
        # Unstow any existing claude configuration
        cd "$DOTFILES_DIR"
        stow -D -t "$TARGET_DIR" claude-project 2>/dev/null || true
    else
        # Backup existing .claude directory
        BACKUP_DIR="$TARGET_DIR/.claude.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Backing up existing .claude to $(basename $BACKUP_DIR)${NC}"
        mv "$TARGET_DIR/.claude" "$BACKUP_DIR"
    fi
fi

# Check if CLAUDE.md already exists in target
if [ -e "$TARGET_DIR/CLAUDE.md" ] && [ ! -L "$TARGET_DIR/CLAUDE.md" ]; then
    BACKUP_FILE="$TARGET_DIR/CLAUDE.md.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Backing up existing CLAUDE.md to $(basename $BACKUP_FILE)${NC}"
    mv "$TARGET_DIR/CLAUDE.md" "$BACKUP_FILE"
fi

# Deploy using stow
echo -e "${GREEN}Deploying claude-project to $TARGET_DIR...${NC}"
cd "$DOTFILES_DIR"
stow -v -t "$TARGET_DIR" claude-project

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Claude project settings deployed successfully!${NC}"
    echo ""
    echo "Deployed files:"
    echo "  .claude/settings.json - Project configuration"
    echo "  .claude/settings.local.json - Personal project overrides"
    echo "  .claude/agents/ - Project-specific agents"
    echo "  .claude/commands/ - Project-specific commands"
    echo "  CLAUDE.md - Project guidance file"
    echo ""
    echo "Next steps:"
    echo "  1. cd $TARGET_DIR"
    echo "  2. Customize CLAUDE.md for your project"
    echo "  3. Modify .claude/settings.json as needed"
    echo "  4. Run '/init' in Claude Code to initialize memory bank"
    
    # Create .gitignore entry for settings.local.json if git repo
    if [ -d "$TARGET_DIR/.git" ]; then
        if ! grep -q "^.claude/settings.local.json" "$TARGET_DIR/.gitignore" 2>/dev/null; then
            echo ""
            echo -e "${YELLOW}Adding .claude/settings.local.json to .gitignore${NC}"
            echo ".claude/settings.local.json" >> "$TARGET_DIR/.gitignore"
        fi
    fi
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi