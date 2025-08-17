#!/usr/bin/env bash
# Config package installation script
# Deploys various application configuration files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source OS detection
if [[ -f "$DOTFILES_ROOT/scripts/os-detect.sh" ]]; then
    source "$DOTFILES_ROOT/scripts/os-detect.sh"
    detect_os
    export_environment
else
    echo "Warning: OS detection script not found"
fi

# Logging functions
log() { echo "[INFO] $1"; }
info() { echo "[INFO] $1"; }
warn() { echo "[WARN] $1"; }
error() { echo "[ERROR] $1"; return 1; }
success() { echo "✓ $1"; }

# Deploy configuration files
deploy_configs() {
    log "Deploying configuration files..."
    
    # Create necessary directories
    mkdir -p "$HOME/.config"
    
    # Deploy ccstatusline configuration
    if [[ -f "$SCRIPT_DIR/.config/ccstatusline/settings.json" ]]; then
        mkdir -p "$HOME/.config/ccstatusline"
        cp "$SCRIPT_DIR/.config/ccstatusline/settings.json" "$HOME/.config/ccstatusline/"
        success "ccstatusline configuration deployed"
    else
        warn "ccstatusline configuration not found"
    fi
    
    success "Configuration deployment completed"
}

# Backup existing configurations
backup_configs() {
    log "Backing up existing configurations..."
    
    local backup_dir="$HOME/.config-backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup ccstatusline if it exists
    if [[ -d "$HOME/.config/ccstatusline" ]]; then
        cp -r "$HOME/.config/ccstatusline" "$backup_dir/"
        info "Backed up ccstatusline to $backup_dir"
    fi
    
    success "Configurations backed up to $backup_dir"
}

# Main installation function
main() {
    echo "======================================"
    echo "   Configuration Package Installation"
    echo "======================================"
    echo ""
    
    backup_configs
    deploy_configs
    
    echo ""
    info "Configuration files deployed successfully!"
    echo ""
    info "Applications configured:"
    echo "  • ccstatusline - Claude Code status line tool"
    echo ""
    info "To use ccstatusline:"
    echo "  1. Ensure ccstatusline is installed: npm install -g ccstatusline"
    echo "  2. Run: npx ccstatusline@latest to configure"
    echo "  3. Your saved settings will be automatically loaded"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi