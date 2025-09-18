# Claude Stow Setup Documentation

## Overview
This document maintains the setup and verification procedures for the `claude` GNU Stow package, which manages Claude Code configuration files through symlinks.

## Package Structure
```
claude/
└── .claude/                    # Target: ~/.claude/
    ├── .mcp.json              # MCP server configuration
    ├── settings.json          # Main Claude settings (includes statusline config)
    ├── CLAUDE.md              # Claude-specific instructions
    ├── agents/                # Custom agents (tree-folded)
    ├── commands/              # Custom commands
    ├── hooks/                 # Event hooks (SessionStart, UserPromptSubmit)
    ├── mcp_servers/           # MCP server implementations (tree-folded)
    ├── output-styles/         # Output formatting styles
    ├── profiles/              # Configuration profiles (minimal, backend, full)
    ├── scripts/               # Helper scripts (includes statusline.sh)
    └── *.md                   # Documentation files
```

## Installation

### Initial Setup
```bash
cd ~/dotfiles
stow claude
```

### Clean Installation (if conflicts exist)
```bash
# Remove conflicting files
rm -f ~/.claude/settings.json ~/.claude/CLAUDE.md

# Remove directories that might conflict
rm -rf ~/.claude/agents ~/.claude/mcp_servers ~/.claude/scripts

# Re-stow the package
cd ~/dotfiles
stow claude
```

## Verification Commands

### Quick Status Check
```bash
# Check if package is properly stowed
cd ~/dotfiles && stow --no --verbose claude 2>&1 | grep -E "WARNING|ERROR"
```

### Comprehensive Verification Script
```bash
#!/bin/bash
# Save as ~/dotfiles/scripts/verify-claude-stow.sh

echo "=== Claude Stow Verification ==="
echo

# Critical files that must be symlinked
critical_files=(
    "settings.json"
    "CLAUDE.md"
    ".mcp.json"
    "scripts"
    "hooks"
)

# Check each critical file
for item in "${critical_files[@]}"; do
    if [ -L ~/.claude/"$item" ]; then
        target=$(readlink ~/.claude/"$item")
        echo "✓ $item -> $target"
    elif [ -e ~/.claude/"$item" ]; then
        echo "✗ $item exists but is NOT a symlink"
    else
        echo "✗ $item is MISSING"
    fi
done

# Check statusline specifically
if [ -x ~/.claude/scripts/statusline.sh ]; then
    echo "✓ Statusline script is executable"
else
    echo "✗ Statusline script missing or not executable"
fi

# Test statusline
echo -e "\n=== Statusline Test ==="
echo '{"workspace": {"current_dir": "'$(pwd)'"}, "model": {"display_name": "test"}}' | ~/.claude/scripts/statusline.sh
```

### Individual Item Check
```bash
# List all symlinks in ~/.claude
ls -la ~/.claude/ | grep "^l"

# Check specific item
ls -la ~/.claude/settings.json
readlink ~/.claude/settings.json
```

## Stow Behavior Notes

### Tree Folding
Stow uses "tree folding" for directories. When a directory needs to contain items from multiple sources:
- Stow creates the directory (not a symlink)
- Individual files within are symlinked

This occurs with:
- `~/.claude/agents/` - Contains individual symlinks to agent files
- `~/.claude/mcp_servers/` - Contains individual symlinks to server files

### Symlink Structure
Most items create direct symlinks:
```
~/.claude/settings.json -> ../dotfiles/claude/.claude/settings.json
~/.claude/scripts -> ../dotfiles/claude/.claude/scripts
```

## Common Issues & Solutions

### Issue: "cannot stow over existing target"
**Cause:** Regular files exist where symlinks should be
**Solution:**
```bash
# Backup and remove conflicting files
mv ~/.claude/settings.json ~/.claude/settings.json.backup
rm ~/.claude/CLAUDE.md
cd ~/dotfiles && stow claude
```

### Issue: Statusline not showing
**Symptoms:** Statusline configuration exists but doesn't appear in Claude Code
**Verification:**
```bash
# Check if settings.json is symlinked
ls -la ~/.claude/settings.json

# Verify statusline configuration
grep -A2 "statusLine" ~/.claude/settings.json

# Test script directly
echo '{"workspace": {"current_dir": "."}, "model": {"display_name": "test"}}' | ~/.claude/scripts/statusline.sh
```

### Issue: "existing target is not owned by stow"
**Cause:** Directories created outside of stow
**Solution:**
```bash
# Remove the non-stow directory
rm -rf ~/.claude/mcp_servers
# Re-stow
cd ~/dotfiles && stow claude
```

## Maintenance Tasks

### Adding New Files
1. Add file to `~/dotfiles/claude/.claude/`
2. Re-run stow: `cd ~/dotfiles && stow claude`
3. Verify: `ls -la ~/.claude/new-file`

### Updating Existing Files
- Edit directly in `~/dotfiles/claude/.claude/`
- Changes immediately reflect (symlinks point to source)

### Removing the Package
```bash
cd ~/dotfiles
stow -D claude  # Unstow (remove all symlinks)
```

### Restowing (refresh all symlinks)
```bash
cd ~/dotfiles
stow -R claude  # Restow (remove then recreate)
```

## Critical Files Reference

### settings.json
- **Purpose:** Main configuration file
- **Key sections:**
  - `statusLine`: Status bar configuration
  - `hooks`: Event hooks
  - `permissions`: Tool permissions
  - `env`: Environment variables

### scripts/statusline.sh
- **Purpose:** Generates status line display
- **Requirements:** 
  - Must be executable (`chmod +x`)
  - Requires `jq` for JSON parsing
  - Uses ANSI color codes for formatting

### .mcp.json
- **Purpose:** MCP server configurations
- **Location:** Profile-specific versions in `profiles/*/`

## Automated Verification

### Quick Verification Script
A comprehensive verification script is available at:
```bash
~/dotfiles/scripts/verify-claude-stow.sh
```

Run it anytime to check the stow status:
```bash
bash ~/dotfiles/scripts/verify-claude-stow.sh
```

### Shell Startup Check
Add to your `.zshrc` or shell startup:
```bash
# Verify claude stow on shell start
if [ -d ~/dotfiles/claude ]; then
    if ! [ -L ~/.claude/settings.json ]; then
        echo "⚠️  Claude configuration not properly stowed. Run: cd ~/dotfiles && stow claude"
    fi
fi
```

## Testing After Setup

1. **Verify symlinks:** `ls -la ~/.claude/`
2. **Test statusline:** Restart Claude Code and check for status bar
3. **Check hooks:** Create a new session and verify hooks execute
4. **Validate settings:** `jq . ~/.claude/settings.json` (should parse without errors)

---
Last Updated: 2025-01-18
Version: 1.0.0