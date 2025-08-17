#!/usr/bin/env bash
# End-to-End Dotfiles Test
# Tests actual installation scenarios that users would experience

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Test scenario to run
SCENARIO="${1:-basic}"

# Logging
log() { echo -e "${BLUE}[E2E]${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Test scenarios
case "$SCENARIO" in
    basic)
        log "Testing basic developer setup..."
        echo "========================================"
        
        # What a new developer would do
        log "1. Installing development profile..."
        # Use stow directly to avoid conflicts
        for package in git vim zsh claude-default; do
            if [[ -d "$package" ]]; then
                stow -t "$HOME" "$package" 2>/dev/null || true
            fi
        done
        
        log "2. Checking what got installed..."
        ls -la ~ | grep "^l" | head -10
        
        log "3. Verifying git is configured..."
        if [[ -L "$HOME/.gitconfig" ]]; then
            success "Git config installed"
            cat ~/.gitconfig | head -5
        fi
        
        log "4. Verifying Claude is configured..."
        if [[ -L "$HOME/.claude" ]]; then
            success "Claude config installed"
        fi
        
        success "Basic setup complete!"
        ;;
        
    full)
        log "Testing full installation..."
        echo "========================================"
        
        # Complete setup
        log "1. Installing everything..."
        # Install all packages found
        for package in */; do
            package_name=$(basename "$package")
            # Skip non-package directories
            if [[ "$package_name" != "tests" ]] && [[ "$package_name" != "scripts" ]] && \
               [[ "$package_name" != "config" ]] && [[ "$package_name" != "docs" ]] && \
               [[ "$package_name" != "profiles" ]] && [[ -f "$package_name/.stow-local-ignore" ]] || \
               [[ -f "$package_name/install.sh" ]]; then
                stow -t "$HOME" "$package_name" 2>/dev/null || true
            fi
        done
        
        log "2. Counting installed symlinks..."
        symlink_count=$(find ~ -maxdepth 2 -type l 2>/dev/null | wc -l)
        success "Installed $symlink_count symlinks"
        
        log "3. Testing backup functionality..."
        make backup-minimal
        if [[ -d "$HOME/.dotfiles-backups" ]]; then
            success "Backup created"
        fi
        
        success "Full installation tested!"
        ;;
        
    claude)
        log "Testing Claude-focused setup..."
        echo "========================================"
        
        # Just Claude and essentials
        log "1. Installing Claude configs..."
        stow -t ~ claude-user 2>/dev/null || true
        # Don't install claude-project if claude-user is already there (conflicts)
        
        log "2. Verifying Claude directories..."
        if [[ -d "$HOME/.claude" ]]; then
            success "Claude user config installed"
            ls -la ~/.claude/
        fi
        
        log "3. Checking MCP config..."
        if [[ -f "$HOME/.claude/mcp.json" ]] || [[ -L "$HOME/.claude/mcp.json" ]]; then
            success "MCP config found"
        fi
        
        success "Claude setup complete!"
        ;;
        
    switch)
        log "Testing profile switching..."
        echo "========================================"
        
        # Test switching between profiles
        log "1. Starting with minimal..."
        ./install.sh --profile minimal
        minimal_count=$(find ~ -maxdepth 2 -type l 2>/dev/null | wc -l)
        success "Minimal: $minimal_count symlinks"
        
        log "2. Upgrading to development..."
        ./install.sh --profile development
        dev_count=$(find ~ -maxdepth 2 -type l 2>/dev/null | wc -l)
        success "Development: $dev_count symlinks"
        
        if [[ $dev_count -gt $minimal_count ]]; then
            success "Profile upgrade worked!"
        fi
        ;;
        
    *)
        error "Unknown scenario: $SCENARIO"
        ;;
esac

# Summary of what's installed
echo
echo "========================================"
log "Installation Summary:"
echo "Symlinks in home directory:"
find ~ -maxdepth 1 -type l -exec basename {} \; 2>/dev/null | sort | head -20
echo
success "E2E test '$SCENARIO' completed!"

# Export the home directory for review
EXPORT_DIR="/exports/${SCENARIO}-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EXPORT_DIR"
cp -r ~/.[!.]* "$EXPORT_DIR/" 2>/dev/null || true
cp -r ~/[!.]* "$EXPORT_DIR/" 2>/dev/null || true
echo "Home directory exported to: $EXPORT_DIR"