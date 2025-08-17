#!/usr/bin/env bash
# Dotfiles Backup and Restore Script
# Handles complete backup and restoration of dotfiles and configurations

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/.dotfiles-backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Logging functions
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
success() { echo -e "${GREEN}✓${NC} $1"; }

# Files and directories to backup
BACKUP_ITEMS=(
    "$HOME/.zshrc"
    "$HOME/.bashrc"
    "$HOME/.vimrc"
    "$HOME/.gitconfig"
    "$HOME/.gitignore_global"
    "$HOME/.ssh/config"
    "$HOME/.gnupg"
    "$HOME/.password-store"
    "$HOME/.claude"
    "$HOME/.config"
    "$HOME/.local/share"
)

# Parse command line arguments
ACTION=""
RESTORE_FROM=""
EXCLUDE_SECRETS=false
INCLUDE_HOMEBREW=false
DRY_RUN=false
VERBOSE=false

show_help() {
    cat << EOF
${BOLD}Dotfiles Backup and Restore Tool${NC}

Usage: $0 [OPTIONS] COMMAND

COMMANDS:
    backup              Create a new backup
    restore [PATH]      Restore from backup (latest or specified)
    list               List available backups
    clean              Remove old backups (keep last 5)
    verify [PATH]      Verify backup integrity

OPTIONS:
    -h, --help         Show this help message
    -v, --verbose      Enable verbose output
    -n, --dry-run      Show what would be done without doing it
    --exclude-secrets  Exclude GPG and password store from backup
    --include-brew     Include Homebrew packages list
    --backup-dir DIR   Custom backup directory (default: ~/.dotfiles-backups)

EXAMPLES:
    $0 backup                    # Create a new backup
    $0 restore                   # Restore from latest backup
    $0 restore 20240117_120000   # Restore specific backup
    $0 list                      # Show all backups
    $0 clean --dry-run          # Preview cleanup

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            backup)
                ACTION="backup"
                shift
                ;;
            restore)
                ACTION="restore"
                shift
                [[ $# -gt 0 && ! "$1" =~ ^- ]] && { RESTORE_FROM="$1"; shift; }
                ;;
            list)
                ACTION="list"
                shift
                ;;
            clean)
                ACTION="clean"
                shift
                ;;
            verify)
                ACTION="verify"
                shift
                [[ $# -gt 0 && ! "$1" =~ ^- ]] && { RESTORE_FROM="$1"; shift; }
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            --exclude-secrets)
                EXCLUDE_SECRETS=true
                shift
                ;;
            --include-brew)
                INCLUDE_HOMEBREW=true
                shift
                ;;
            --backup-dir)
                shift
                BACKUP_ROOT="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
}

# Create backup
create_backup() {
    log "Creating backup in $BACKUP_DIR"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would create backup directory: $BACKUP_DIR"
    else
        mkdir -p "$BACKUP_DIR"
    fi
    
    # Create metadata file
    if [[ "$DRY_RUN" == false ]]; then
        cat > "$BACKUP_DIR/metadata.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "hostname": "$(hostname)",
    "username": "$USER",
    "os": "$(uname -s)",
    "os_version": "$(uname -r)",
    "dotfiles_version": "$(cd "$SCRIPT_DIR/.." && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "exclude_secrets": $([[ "$EXCLUDE_SECRETS" == true ]] && echo "true" || echo "false")
}
EOF
    fi
    
    # Backup each item
    for item in "${BACKUP_ITEMS[@]}"; do
        if [[ ! -e "$item" ]]; then
            [[ "$VERBOSE" == true ]] && warn "Skipping non-existent: $item"
            continue
        fi
        
        # Skip secrets if requested
        if [[ "$EXCLUDE_SECRETS" == true ]]; then
            if [[ "$item" == *".gnupg"* ]] || [[ "$item" == *".password-store"* ]]; then
                info "Skipping secrets: $item"
                continue
            fi
        fi
        
        # Calculate relative path for backup
        rel_path="${item#$HOME/}"
        backup_path="$BACKUP_DIR/home/$rel_path"
        
        if [[ "$DRY_RUN" == true ]]; then
            info "DRY RUN: Would backup $item to $backup_path"
        else
            mkdir -p "$(dirname "$backup_path")"
            if [[ -d "$item" ]]; then
                cp -R "$item" "$backup_path"
            else
                cp "$item" "$backup_path" 2>/dev/null || true
            fi
            [[ "$VERBOSE" == true ]] && success "Backed up: $rel_path"
        fi
    done
    
    # Backup Homebrew packages if requested
    if [[ "$INCLUDE_HOMEBREW" == true ]] && command -v brew &> /dev/null; then
        if [[ "$DRY_RUN" == true ]]; then
            info "DRY RUN: Would backup Homebrew packages list"
        else
            brew list --formula > "$BACKUP_DIR/homebrew-formulas.txt"
            brew list --cask > "$BACKUP_DIR/homebrew-casks.txt"
            brew tap > "$BACKUP_DIR/homebrew-taps.txt"
            success "Backed up Homebrew packages"
        fi
    fi
    
    # Create tarball
    if [[ "$DRY_RUN" == false ]]; then
        log "Creating compressed archive..."
        cd "$BACKUP_ROOT"
        tar -czf "${TIMESTAMP}.tar.gz" "$TIMESTAMP"
        rm -rf "$TIMESTAMP"
        success "Backup created: ${BACKUP_ROOT}/${TIMESTAMP}.tar.gz"
        
        # Show backup size
        size=$(du -h "${BACKUP_ROOT}/${TIMESTAMP}.tar.gz" | cut -f1)
        info "Backup size: $size"
    fi
}

# Restore from backup
restore_backup() {
    local backup_archive=""
    
    # Find backup to restore
    if [[ -z "$RESTORE_FROM" ]]; then
        # Use latest backup
        backup_archive=$(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | head -1)
        if [[ -z "$backup_archive" ]]; then
            error "No backups found in $BACKUP_ROOT"
        fi
    else
        # Use specified backup
        if [[ -f "$BACKUP_ROOT/${RESTORE_FROM}.tar.gz" ]]; then
            backup_archive="$BACKUP_ROOT/${RESTORE_FROM}.tar.gz"
        elif [[ -f "$RESTORE_FROM" ]]; then
            backup_archive="$RESTORE_FROM"
        else
            error "Backup not found: $RESTORE_FROM"
        fi
    fi
    
    log "Restoring from: $backup_archive"
    
    # Extract backup
    temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN: Would extract backup to $temp_dir"
    else
        tar -xzf "$backup_archive" -C "$temp_dir"
        backup_dir=$(ls -d "$temp_dir"/*/)
        
        # Show metadata
        if [[ -f "$backup_dir/metadata.json" ]]; then
            info "Backup metadata:"
            cat "$backup_dir/metadata.json"
            echo
        fi
        
        # Confirm restoration
        if [[ "$DRY_RUN" == false ]]; then
            read -p "Continue with restoration? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                warn "Restoration cancelled"
                exit 0
            fi
        fi
        
        # Create safety backup of current configs
        safety_backup="$BACKUP_ROOT/pre-restore-${TIMESTAMP}"
        mkdir -p "$safety_backup"
        log "Creating safety backup of current configs..."
        
        # Restore files
        if [[ -d "$backup_dir/home" ]]; then
            cd "$backup_dir/home"
            find . -type f | while read -r file; do
                source_file="$backup_dir/home/$file"
                target_file="$HOME/$file"
                
                # Backup existing file
                if [[ -f "$target_file" ]]; then
                    mkdir -p "$(dirname "$safety_backup/$file")"
                    cp "$target_file" "$safety_backup/$file"
                fi
                
                # Restore file
                mkdir -p "$(dirname "$target_file")"
                cp "$source_file" "$target_file"
                [[ "$VERBOSE" == true ]] && success "Restored: $file"
            done
        fi
        
        success "Restoration complete!"
        info "Safety backup created at: $safety_backup"
    fi
}

# List available backups
list_backups() {
    log "Available backups in $BACKUP_ROOT:"
    echo
    
    if [[ ! -d "$BACKUP_ROOT" ]] || [[ -z $(ls -A "$BACKUP_ROOT" 2>/dev/null) ]]; then
        warn "No backups found"
        return
    fi
    
    # List backups with details
    ls -lh "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | while read -r line; do
        size=$(echo "$line" | awk '{print $5}')
        date=$(echo "$line" | awk '{print $6, $7, $8}')
        file=$(echo "$line" | awk '{print $9}')
        name=$(basename "$file" .tar.gz)
        
        echo -e "${BOLD}$name${NC}"
        echo "  Size: $size"
        echo "  Date: $date"
        
        # Try to show metadata if possible
        temp_dir=$(mktemp -d)
        if tar -xzf "$file" -C "$temp_dir" "*/metadata.json" 2>/dev/null; then
            metadata=$(find "$temp_dir" -name metadata.json -type f 2>/dev/null | head -1)
            if [[ -f "$metadata" ]]; then
                hostname=$(grep '"hostname"' "$metadata" | cut -d'"' -f4)
                os=$(grep '"os"' "$metadata" | cut -d'"' -f4)
                echo "  Host: $hostname ($os)"
            fi
        fi
        rm -rf "$temp_dir"
        echo
    done
}

# Clean old backups
clean_backups() {
    log "Cleaning old backups (keeping last 5)..."
    
    if [[ ! -d "$BACKUP_ROOT" ]]; then
        warn "Backup directory doesn't exist"
        return
    fi
    
    # Get list of backups sorted by date
    backups=($(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null))
    
    if [[ ${#backups[@]} -le 5 ]]; then
        info "No cleanup needed (${#backups[@]} backups found)"
        return
    fi
    
    # Remove old backups
    for ((i=5; i<${#backups[@]}; i++)); do
        backup="${backups[$i]}"
        if [[ "$DRY_RUN" == true ]]; then
            info "DRY RUN: Would remove $backup"
        else
            rm -f "$backup"
            success "Removed: $(basename "$backup")"
        fi
    done
    
    info "Cleanup complete"
}

# Verify backup integrity
verify_backup() {
    local backup_archive=""
    
    if [[ -z "$RESTORE_FROM" ]]; then
        backup_archive=$(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | head -1)
    else
        if [[ -f "$BACKUP_ROOT/${RESTORE_FROM}.tar.gz" ]]; then
            backup_archive="$BACKUP_ROOT/${RESTORE_FROM}.tar.gz"
        elif [[ -f "$RESTORE_FROM" ]]; then
            backup_archive="$RESTORE_FROM"
        else
            error "Backup not found: $RESTORE_FROM"
        fi
    fi
    
    log "Verifying backup: $backup_archive"
    
    # Test archive integrity
    if tar -tzf "$backup_archive" > /dev/null 2>&1; then
        success "Archive integrity: OK"
    else
        error "Archive integrity: FAILED"
    fi
    
    # Extract and check contents
    temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT
    
    tar -xzf "$backup_archive" -C "$temp_dir"
    backup_dir=$(ls -d "$temp_dir"/*/)
    
    # Check metadata
    if [[ -f "$backup_dir/metadata.json" ]]; then
        success "Metadata: Found"
        cat "$backup_dir/metadata.json"
    else
        warn "Metadata: Not found"
    fi
    
    # Count files
    file_count=$(find "$backup_dir/home" -type f 2>/dev/null | wc -l)
    info "Files in backup: $file_count"
    
    # Check for important files
    important_files=(".zshrc" ".gitconfig" ".vimrc")
    for file in "${important_files[@]}"; do
        if [[ -f "$backup_dir/home/$file" ]]; then
            success "Found: $file"
        else
            warn "Missing: $file"
        fi
    done
    
    success "Verification complete"
}

# Main execution
main() {
    parse_args "$@"
    
    if [[ -z "$ACTION" ]]; then
        error "No command specified. Use -h for help."
    fi
    
    case "$ACTION" in
        backup)
            create_backup
            ;;
        restore)
            restore_backup
            ;;
        list)
            list_backups
            ;;
        clean)
            clean_backups
            ;;
        verify)
            verify_backup
            ;;
        *)
            error "Unknown action: $ACTION"
            ;;
    esac
}

main "$@"