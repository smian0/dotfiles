#!/bin/bash

# Claude Stow Verification Script
# Verifies that the claude package is properly stowed

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== Claude Stow Verification ==="
echo "Checking ~/dotfiles/claude stow status..."
echo

# Check if dotfiles directory exists
if [ ! -d ~/dotfiles/claude ]; then
    echo -e "${RED}✗ ~/dotfiles/claude directory not found${NC}"
    exit 1
fi

# Critical files that must be symlinked
critical_files=(
    "settings.json"
    "CLAUDE.md"
    ".mcp.json"
    "scripts"
    "hooks"
    "profiles"
    "output-styles"
    "commands"
)

# Track overall status
all_good=true

# Check each critical file
echo "Critical Files/Directories:"
for item in "${critical_files[@]}"; do
    if [ -L ~/.claude/"$item" ]; then
        target=$(readlink ~/.claude/"$item")
        echo -e "${GREEN}✓${NC} $item -> $target"
    elif [ -e ~/.claude/"$item" ]; then
        echo -e "${YELLOW}⚠${NC}  $item exists but is NOT a symlink"
        all_good=false
    else
        echo -e "${RED}✗${NC} $item is MISSING"
        all_good=false
    fi
done

echo

# Check tree-folded directories (should be directories, not symlinks)
echo "Tree-folded Directories (should contain symlinked files):"
for dir in agents mcp_servers; do
    if [ -d ~/.claude/"$dir" ] && [ ! -L ~/.claude/"$dir" ]; then
        # Count symlinks inside
        symlink_count=$(find ~/.claude/"$dir" -maxdepth 1 -type l | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} $dir/ (contains $symlink_count symlinked items)"
    elif [ -L ~/.claude/"$dir" ]; then
        echo -e "${YELLOW}⚠${NC}  $dir is a symlink (should be tree-folded directory)"
    else
        echo -e "${RED}✗${NC} $dir is missing or incorrectly configured"
        all_good=false
    fi
done

echo

# Check statusline specifically
echo "Statusline Configuration:"
if [ -x ~/.claude/scripts/statusline.sh ]; then
    echo -e "${GREEN}✓${NC} Statusline script is executable"
    
    # Check if statusline is configured in settings.json
    if grep -q '"statusLine"' ~/.claude/settings.json 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Statusline configured in settings.json"
    else
        echo -e "${YELLOW}⚠${NC}  Statusline not configured in settings.json"
        all_good=false
    fi
else
    echo -e "${RED}✗${NC} Statusline script missing or not executable"
    all_good=false
fi

echo

# Test statusline functionality
echo "=== Statusline Test ==="
if [ -x ~/.claude/scripts/statusline.sh ]; then
    test_output=$(echo '{"workspace": {"current_dir": "'$(pwd)'"}, "model": {"display_name": "claude-3.5"}, "session_id": "test"}' | ~/.claude/scripts/statusline.sh 2>/dev/null || echo "Failed")
    if [ "$test_output" != "Failed" ] && [ -n "$test_output" ]; then
        echo -e "${GREEN}✓${NC} Statusline script executes successfully"
        echo "Output: $test_output"
    else
        echo -e "${RED}✗${NC} Statusline script failed to execute"
        all_good=false
    fi
else
    echo -e "${YELLOW}⚠${NC}  Skipping test - script not executable"
fi

echo

# Check for stow conflicts
echo "=== Checking for Stow Conflicts ==="
cd ~/dotfiles
stow_output=$(stow --no --verbose claude 2>&1)
# Filter out the simulation mode warning which is expected
conflicts=$(echo "$stow_output" | grep "WARNING" | grep -v "simulation mode" || true)
if [ -n "$conflicts" ]; then
    echo -e "${YELLOW}⚠${NC}  Stow reports conflicts:"
    echo "$conflicts" | sed 's/^/  /'
    all_good=false
else
    echo -e "${GREEN}✓${NC} No stow conflicts detected"
fi

echo

# Final status
if [ "$all_good" = true ]; then
    echo -e "${GREEN}✅ All checks passed! Claude stow package is properly configured.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some issues detected. Run the following to fix:${NC}"
    echo
    echo "  cd ~/dotfiles"
    echo "  stow -D claude  # Unstow first"
    echo "  stow claude     # Re-stow"
    echo
    echo "If conflicts persist, see ~/dotfiles/claude/STOW-SETUP.md for troubleshooting."
    exit 1
fi