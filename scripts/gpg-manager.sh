#!/usr/bin/env bash
# GPG Key Management Script
# Handles GPG key import/export, backup, and multi-machine sync

set -euo pipefail

# Source OS detection for environment setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/os-detect.sh" ]]; then
    source "$SCRIPT_DIR/os-detect.sh"
else
    # Fallback logging functions
    log() { echo "[INFO] $1"; }
    info() { echo "[INFO] $1"; }
    warn() { echo "[WARN] $1"; }
    error() { echo "[ERROR] $1"; return 1; }
    success() { echo "✓ $1"; }
fi

# Configuration
GPG_BACKUP_DIR="${GPG_BACKUP_DIR:-$HOME/.gnupg-backup}"
PASS_STORE_DIR="${PASSWORD_STORE_DIR:-$HOME/.password-store}"

# Parse command line arguments
ACTION=""
KEY_ID=""
BACKUP_FILE=""
DRY_RUN=false
VERBOSE=false

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            export)
                ACTION="export"
                shift
                ;;
            import)
                ACTION="import"
                shift
                ;;
            backup)
                ACTION="backup"
                shift
                ;;
            restore)
                ACTION="restore"
                shift
                ;;
            list)
                ACTION="list"
                shift
                ;;
            setup)
                ACTION="setup"
                shift
                ;;
            --key-id)
                KEY_ID="$2"
                shift 2
                ;;
            --file)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
GPG Key Management Script

Usage: $(basename "$0") ACTION [OPTIONS]

ACTIONS:
    export          Export GPG key to backup file
    import          Import GPG key from backup file  
    backup          Create complete GPG backup
    restore         Restore GPG from backup
    list            List available GPG keys
    setup           Initial GPG setup and configuration

OPTIONS:
    --key-id ID     GPG key ID to work with
    --file PATH     Backup file path
    --dry-run       Show what would be done
    --verbose       Show detailed output
    --help          Show this help

EXAMPLES:
    $(basename "$0") setup                                    # Initial GPG setup
    $(basename "$0") list                                     # List available keys
    $(basename "$0") export --key-id ABC123 --file backup.asc # Export specific key
    $(basename "$0") import --file backup.asc                 # Import key from file
    $(basename "$0") backup                                   # Full GPG backup
    $(basename "$0") restore --file gpg-backup.tar.gz         # Restore from backup

EOF
}

# Check GPG availability
check_gpg() {
    if ! command -v gpg >/dev/null 2>&1; then
        error "GPG not found. Install with: brew install gnupg"
    fi
    
    [[ "$VERBOSE" == true ]] && info "GPG version: $(gpg --version | head -1)"
}

# List available GPG keys
list_keys() {
    log "Available GPG keys:"
    echo ""
    
    if gpg --list-secret-keys >/dev/null 2>&1; then
        echo "Secret keys:"
        gpg --list-secret-keys --keyid-format LONG
        echo ""
    else
        warn "No secret keys found"
    fi
    
    if gpg --list-keys >/dev/null 2>&1; then
        echo "Public keys:"
        gpg --list-keys --keyid-format LONG
    else
        warn "No public keys found"
    fi
}

# Export GPG key
export_key() {
    local key_id="$1"
    local output_file="$2"
    
    if [[ -z "$key_id" ]]; then
        error "Key ID required for export"
    fi
    
    if [[ -z "$output_file" ]]; then
        output_file="gpg-key-${key_id}.asc"
    fi
    
    log "Exporting GPG key $key_id to $output_file"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would export key $key_id to $output_file"
        return 0
    fi
    
    # Export both public and private keys
    gpg --armor --export "$key_id" > "$output_file"
    gpg --armor --export-secret-keys "$key_id" >> "$output_file"
    
    success "Key exported to $output_file"
    warn "Keep this file secure - it contains your private key!"
}

# Import GPG key
import_key() {
    local input_file="$1"
    
    if [[ -z "$input_file" ]]; then
        error "Input file required for import"
    fi
    
    if [[ ! -f "$input_file" ]]; then
        error "File not found: $input_file"
    fi
    
    log "Importing GPG key from $input_file"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would import key from $input_file"
        return 0
    fi
    
    gpg --import "$input_file"
    success "Key imported from $input_file"
    
    # Set trust level
    echo "Setting trust level for imported key..."
    local key_id
    key_id=$(gpg --list-keys --keyid-format LONG "$input_file" 2>/dev/null | grep "pub" | awk '{print $2}' | cut -d'/' -f2 | head -1)
    
    if [[ -n "$key_id" ]]; then
        info "Set trust level for key $key_id? (requires manual input)"
        gpg --edit-key "$key_id" trust || true
    fi
}

# Create complete backup
create_backup() {
    local backup_file="$1"
    
    if [[ -z "$backup_file" ]]; then
        backup_file="gpg-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
    fi
    
    log "Creating complete GPG backup: $backup_file"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would create backup: $backup_file"
        return 0
    fi
    
    # Create backup directory
    mkdir -p "$GPG_BACKUP_DIR"
    
    # Copy entire GPG directory
    cp -R "$HOME/.gnupg" "$GPG_BACKUP_DIR/gnupg-$(date +%Y%m%d_%H%M%S)"
    
    # Create compressed archive
    tar -czf "$backup_file" -C "$HOME" .gnupg
    
    success "Backup created: $backup_file"
    info "Backup size: $(du -h "$backup_file" | cut -f1)"
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [[ -z "$backup_file" ]]; then
        error "Backup file required for restore"
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
    fi
    
    warn "This will replace your current GPG configuration!"
    if [[ "$DRY_RUN" == false ]]; then
        read -p "Continue? (y/n) " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
    fi
    
    log "Restoring GPG from backup: $backup_file"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would restore from: $backup_file"
        return 0
    fi
    
    # Backup current config
    if [[ -d "$HOME/.gnupg" ]]; then
        mv "$HOME/.gnupg" "$HOME/.gnupg.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Extract backup
    tar -xzf "$backup_file" -C "$HOME"
    
    # Fix permissions
    chmod 700 "$HOME/.gnupg"
    chmod 600 "$HOME/.gnupg"/*
    
    success "GPG restored from backup"
}

# Initial GPG setup
setup_gpg() {
    log "Setting up GPG configuration..."
    
    # Check if keys already exist
    if gpg --list-secret-keys >/dev/null 2>&1; then
        warn "GPG keys already exist"
        list_keys
        return 0
    fi
    
    info "No GPG keys found. You'll need to:"
    echo ""
    echo "1. Generate a new key:"
    echo "   gpg --full-generate-key"
    echo ""
    echo "2. Or import an existing key:"
    echo "   $(basename "$0") import --file your-key.asc"
    echo ""
    
    # Configure GPG for macOS
    if [[ "$DOTFILES_OS" == "macos" ]]; then
        log "Configuring GPG for macOS..."
        
        if [[ "$DRY_RUN" == false ]]; then
            mkdir -p "$HOME/.gnupg"
            
            # Configure pinentry for macOS
            if command -v pinentry-mac >/dev/null 2>&1; then
                echo "pinentry-program $(which pinentry-mac)" > "$HOME/.gnupg/gpg-agent.conf"
                success "Configured pinentry-mac for GPG agent"
            else
                warn "pinentry-mac not found. Install with: brew install pinentry-mac"
            fi
            
            # Set proper permissions
            chmod 700 "$HOME/.gnupg"
            chmod 600 "$HOME/.gnupg/gpg-agent.conf" 2>/dev/null || true
            
            # Restart GPG agent
            gpgconf --kill gpg-agent
        fi
    fi
    
    success "GPG setup completed"
}

# Main function
main() {
    parse_args "$@"
    
    if [[ -z "$ACTION" ]]; then
        error "No action specified"
        show_help
        exit 1
    fi
    
    check_gpg
    
    case "$ACTION" in
        export)
            export_key "$KEY_ID" "$BACKUP_FILE"
            ;;
        import)
            import_key "$BACKUP_FILE"
            ;;
        backup)
            create_backup "$BACKUP_FILE"
            ;;
        restore)
            restore_backup "$BACKUP_FILE"
            ;;
        list)
            list_keys
            ;;
        setup)
            setup_gpg
            ;;
        *)
            error "Unknown action: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi