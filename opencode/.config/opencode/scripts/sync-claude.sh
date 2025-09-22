#!/bin/bash

# Sync Claude configurations to OpenCode format

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRANSFORM_SCRIPT="$SCRIPT_DIR/transform-claude-to-opencode.sh"
MCP_TRANSFORM_SCRIPT="$SCRIPT_DIR/transform-mcp-to-opencode.sh"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[SYNC]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[SYNC]${NC} $1"
}

# Sync function
sync_configs() {
    local scope="$1"
    local source_dir="$2"
    local dest_dir="$3"
    
    if [[ ! -d "$source_dir" ]]; then
        log_info "No $scope Claude configuration found"
        return 0
    fi
    
    log_info "Syncing $scope configurations..."
    
    # Create destination directories
    mkdir -p "$dest_dir/agent" "$dest_dir/command"
    
    # Sync and transform agents
    if [[ -d "$source_dir/agents" ]]; then
        log_info "Copying agents..."
        find "$source_dir/agents" -name "*.md" -type f | while read -r agent; do
            local rel_path="${agent#$source_dir/agents/}"
            local dest_file="$dest_dir/agent/$rel_path"
            mkdir -p "$(dirname "$dest_file")"
            cp "$agent" "$dest_file"
            "$TRANSFORM_SCRIPT" "$dest_file" 2>/dev/null || true
        done
    fi
    
    # Sync and transform commands
    if [[ -d "$source_dir/commands" ]]; then
        log_info "Copying commands..."
        find "$source_dir/commands" -name "*.md" -type f | while read -r cmd; do
            local rel_path="${cmd#$source_dir/commands/}"
            local dest_file="$dest_dir/command/$rel_path"
            mkdir -p "$(dirname "$dest_file")"
            cp "$cmd" "$dest_file"
            "$TRANSFORM_SCRIPT" "$dest_file" 2>/dev/null || true
        done
    fi
    
    log_info "✅ $scope sync complete"
}

# Main
log_info "Starting Claude to OpenCode sync..."

# Sync global configurations
# Check for dotfiles-managed Claude config first
if [[ -d "$HOME/dotfiles/claude/.claude" ]]; then
    sync_configs "global" "$HOME/dotfiles/claude/.claude" "$HOME/.config/opencode"
elif [[ -d "$HOME/.claude" ]]; then
    sync_configs "global" "$HOME/.claude" "$HOME/.config/opencode"
fi

# Always sync MCP servers from main Claude config (has correct mcpServers structure)
if [[ -f "$HOME/.claude.json" ]] && [[ -f "$HOME/.config/opencode/opencode.json" ]]; then
    log_info "Syncing MCP servers from main Claude config..."
    "$MCP_TRANSFORM_SCRIPT" "$HOME/.claude.json" "$HOME/.config/opencode/opencode.json"
fi

# Sync project configurations
if [[ -d ".claude" ]]; then
    sync_configs "project" ".claude" ".opencode"
    # Also sync project MCP servers from .claude/.mcp.json
    if [[ -f ".claude/.mcp.json" ]] && [[ -f ".opencode/opencode.json" ]]; then
        log_info "Syncing project MCP servers from .claude/.mcp.json..."
        "$MCP_TRANSFORM_SCRIPT" ".claude/.mcp.json" ".opencode/opencode.json"
    fi
fi

# Also check for root-level .mcp.json (outside .claude directory)
if [[ -f ".mcp.json" ]] && [[ -f ".opencode/opencode.json" ]]; then
    log_info "Syncing root-level MCP servers from .mcp.json..."
    "$MCP_TRANSFORM_SCRIPT" ".mcp.json" ".opencode/opencode.json"
elif [[ -f ".mcp.json" ]] && [[ ! -f ".opencode/opencode.json" ]]; then
    # Create .opencode directory and basic opencode.json if needed
    mkdir -p ".opencode"
    echo '{"$schema":"https://opencode.ai/config.json"}' > ".opencode/opencode.json"
    log_info "Created .opencode/opencode.json and syncing root-level MCP servers..."
    "$MCP_TRANSFORM_SCRIPT" ".mcp.json" ".opencode/opencode.json"
fi

log_info "🎉 Sync complete!"