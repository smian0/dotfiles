#!/usr/bin/env bash
# Cursor package installation script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log "Installing Cursor configuration..."

# Check if Cursor configuration directory exists
if [[ ! -d "$HOME/.cursor" ]]; then
    log "Creating ~/.cursor directory"
    mkdir -p "$HOME/.cursor"
fi

# Check if mcp.json already exists and is different
if [[ -f "$HOME/.cursor/mcp.json" ]]; then
    if [[ -f "$SCRIPT_DIR/.cursor/mcp.json" ]]; then
        if ! diff -q "$HOME/.cursor/mcp.json" "$SCRIPT_DIR/.cursor/mcp.json" >/dev/null; then
            warn "Existing ~/.cursor/mcp.json differs from package version"
            warn "Consider backing up existing configuration before stowing"
        else
            success "MCP configuration is already up to date"
        fi
    fi
fi

success "Cursor configuration installed successfully"

log "MCP configuration includes the following servers:"
if [[ -f "$SCRIPT_DIR/.cursor/mcp.json" ]]; then
    # Extract server names from the JSON
    grep -o '"[^"]*"[[:space:]]*:' "$SCRIPT_DIR/.cursor/mcp.json" | grep -v '"mcpServers"' | sed 's/"//g' | sed 's/://g' | while read -r server; do
        echo "  - $server"
    done
fi

log "Use 'stow cursor' from dotfiles directory to symlink configuration"
