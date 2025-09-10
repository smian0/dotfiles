#!/bin/bash

# Quick MCP sync wrapper for dotfiles
# This ensures the .mcp.json file in dotfiles stays in sync with claude.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Run the sync with default settings
"$SCRIPT_DIR/sync-mcp-config.sh" "$@"