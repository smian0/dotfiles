# Serena Configuration Package

This package manages Serena MCP server configuration using GNU Stow.

## What's Included
- **serena_config.yml** - Main Serena configuration file

## Installation
```bash
cd ~/dotfiles
stow serena
```

## Configuration Location
- **Source:** `~/dotfiles/serena/.serena/serena_config.yml`  
- **Target:** `~/.serena/serena_config.yml` (symlink)

## Current Settings
- Web dashboard: Enabled
- Auto-open dashboard: Enabled
- Log level: INFO (20)
- Tool timeout: 240 seconds

## Verification
```bash
# Check symlink
ls -la ~/.serena/serena_config.yml

# Should show:
# ~/.serena/serena_config.yml -> ../dotfiles/serena/.serena/serena_config.yml
```

---
Created: 2025-01-18