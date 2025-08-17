#!/usr/bin/env bash
# Global npm packages management for dotfiles
# Installs and manages npm packages across machines

set -euo pipefail

# Source OS detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$DOTFILES_ROOT/scripts/os-detect.sh" ]]; then
    source "$DOTFILES_ROOT/scripts/os-detect.sh"
    detect_os
    export_environment
fi

# Logging functions
log() { echo "[INFO] $1"; }
info() { echo "[INFO] $1"; }
warn() { echo "[WARN] $1"; }
error() { echo "[ERROR] $1"; return 1; }
success() { echo "✓ $1"; }

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Global npm packages list
GLOBAL_PACKAGES=(
    "ccstatusline"  # sirmalloc/ccstatusline for Claude Code status lines
    "npm-check-updates"  # Check for package updates
    "http-server"  # Simple HTTP server for development
    "nodemon"  # Auto-restart server on file changes
    # Add more packages here as needed
)

# Install global npm packages
install_global_packages() {
    if ! command_exists npm; then
        error "npm not found. Install Node.js first."
    fi
    
    log "Installing global npm packages..."
    
    for package in "${GLOBAL_PACKAGES[@]}"; do
        if npm list -g "$package" >/dev/null 2>&1; then
            success "$package already installed"
        else
            log "Installing $package..."
            npm install -g "$package"
            success "$package installed"
        fi
    done
}

# List installed global packages
list_global_packages() {
    log "Currently installed global packages:"
    npm list -g --depth=0 2>/dev/null | grep -E "$(IFS='|'; echo "${GLOBAL_PACKAGES[*]}")" || true
}

# Update global packages
update_global_packages() {
    log "Updating global npm packages..."
    
    for package in "${GLOBAL_PACKAGES[@]}"; do
        if npm list -g "$package" >/dev/null 2>&1; then
            log "Updating $package..."
            npm update -g "$package"
            success "$package updated"
        else
            warn "$package not installed, skipping update"
        fi
    done
}

# Backup global package list
backup_global_packages() {
    local backup_file="$DOTFILES_ROOT/npm-global-packages.json"
    log "Backing up global packages to $backup_file..."
    npm list -g --json --depth=0 > "$backup_file"
    success "Global packages backed up"
}

# Restore from backup
restore_global_packages() {
    local backup_file="$DOTFILES_ROOT/npm-global-packages.json"
    
    if [[ ! -f "$backup_file" ]]; then
        warn "No backup file found at $backup_file"
        return 1
    fi
    
    log "Restoring global packages from backup..."
    
    # Extract package names from backup and install
    jq -r '.dependencies | keys[]' "$backup_file" | while read -r package; do
        if ! npm list -g "$package" >/dev/null 2>&1; then
            log "Installing $package from backup..."
            npm install -g "$package"
        fi
    done
    
    success "Global packages restored from backup"
}

# Show help
show_help() {
    cat << EOF
Global npm packages management script

USAGE: $0 [COMMAND]

COMMANDS:
    install     Install all global packages
    list        List installed global packages  
    update      Update all global packages
    backup      Backup current global packages to JSON
    restore     Restore global packages from backup
    help        Show this help message

EXAMPLES:
    $0 install              # Install all packages
    $0 update               # Update all packages
    $0 backup               # Create backup file
    
Global packages managed:
$(printf "  - %s\n" "${GLOBAL_PACKAGES[@]}")
EOF
}

# Main function
main() {
    case "${1:-help}" in
        install)
            install_global_packages
            ;;
        list)
            list_global_packages
            ;;
        update)
            update_global_packages
            ;;
        backup)
            backup_global_packages
            ;;
        restore)
            restore_global_packages
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $1. Run '$0 help' for usage."
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi