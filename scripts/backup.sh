#!/usr/bin/env bash
# Backup Script for Dotfiles
# Creates backups of existing configuration files before stowing

set -euo pipefail

# Source OS detection for environment setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/os-detect.sh" ]]; then
    source "$SCRIPT_DIR/os-detect.sh"
else
    # Fallback if os-detect.sh is not available
    OS_TYPE="unknown"
    DOTFILES_OS="unknown"
    DOTFILES_DISTRO="unknown"
    DOTFILES_PKG_MANAGER="unknown"
    
    # Define missing functions
    log() { echo "[INFO] $1"; }
    info() { echo "[INFO] $1"; }
    warn() { echo "[WARN] $1"; }
    error() { echo "[ERROR] $1"; return 1; }
    success() { echo "✓ $1"; }
    
    detect_os() {
        if [[ "$OSTYPE" == "darwin"* ]]; then
            OS_TYPE="macos"
            DOTFILES_OS="macos"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            OS_TYPE="linux"
            DOTFILES_OS="linux"
        fi
    }
    
    export_environment() {
        export DOTFILES_OS
        export DOTFILES_DISTRO
        export DOTFILES_PKG_MANAGER
    }
fi

# Backup configuration
BACKUP_DIR="${DOTFILES_BACKUP_DIR:-$HOME/.dotfiles-backup}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_BACKUP_DIR="$BACKUP_DIR/$TIMESTAMP"
BACKUP_LOG="$CURRENT_BACKUP_DIR/backup.log"
DRY_RUN=false
VERBOSE=false

# Files and directories to backup
declare -a FILES_TO_BACKUP=(
    ".bashrc"
    ".zshrc"
    ".vimrc"
    ".gitconfig"
    ".gitignore_global"
    ".claude"
    ".claude.json"
    ".mcp.json"
    ".ssh/config"
    ".gnupg"
)

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                warn "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Backup existing dotfiles before installing new configurations.

OPTIONS:
    -d, --dry-run    Show what would be backed up without actually doing it
    -v, --verbose    Show detailed output
    -h, --help       Show this help message

EXAMPLES:
    $(basename "$0")              # Create backup
    $(basename "$0") --dry-run    # Preview what will be backed up
    $(basename "$0") --verbose    # Show detailed backup progress

BACKUP LOCATION:
    Backups are stored in: $BACKUP_DIR
    Each backup is timestamped: YYYYMMDD_HHMMSS

EOF
}

# Initialize backup directory
init_backup() {
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would create backup directory: $CURRENT_BACKUP_DIR"
        return 0
    fi
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
    
    log "Creating backup in: $CURRENT_BACKUP_DIR"
    mkdir -p "$CURRENT_BACKUP_DIR"
    
    # Create backup log
    cat > "$BACKUP_LOG" << EOF
Dotfiles Backup Log
==================
Date: $(date)
Host: $(hostname)
User: $(whoami)
OS: $DOTFILES_OS
Distro: $DOTFILES_DISTRO

Files Backed Up:
---------------
EOF
}

# Check if file/directory exists and needs backup
needs_backup() {
    local file=$1
    local full_path="$HOME/$file"
    
    # Check if file/directory exists
    if [[ ! -e "$full_path" ]] && [[ ! -L "$full_path" ]]; then
        [[ "$VERBOSE" == true ]] && info "Skipping $file (does not exist)"
        return 1
    fi
    
    # Check if it's already a symlink to our dotfiles
    if [[ -L "$full_path" ]]; then
        local target
        target=$(readlink "$full_path")
        if [[ "$target" == *"/.dotfiles/"* ]] || [[ "$target" == *"/dotfiles/"* ]]; then
            [[ "$VERBOSE" == true ]] && info "Skipping $file (already a dotfiles symlink)"
            return 1
        fi
    fi
    
    return 0
}

# Backup a single file or directory
backup_file() {
    local file=$1
    local source="$HOME/$file"
    local dest="$CURRENT_BACKUP_DIR/$file"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would backup: $file"
        return 0
    fi
    
    # Create parent directory if needed
    local parent_dir
    parent_dir=$(dirname "$dest")
    if [[ ! -d "$parent_dir" ]]; then
        mkdir -p "$parent_dir"
    fi
    
    # Backup the file/directory
    if [[ -d "$source" ]]; then
        [[ "$VERBOSE" == true ]] && info "Backing up directory: $file"
        cp -R "$source" "$dest"
    else
        [[ "$VERBOSE" == true ]] && info "Backing up file: $file"
        cp -P "$source" "$dest"  # -P preserves symlinks
    fi
    
    # Log the backup
    echo "$file" >> "$BACKUP_LOG"
    
    success "Backed up: $file"
}

# Scan for additional dotfiles
scan_for_dotfiles() {
    log "Scanning for additional dotfiles..."
    
    local found_files=()
    
    # Find all dotfiles in home directory (excluding common system files)
    while IFS= read -r file; do
        local basename
        basename=$(basename "$file")
        
        # Skip system files and directories
        case "$basename" in
            .Trash|.cache|.local|.config|.npm|.node*|.docker|.kube|.aws|.azure)
                continue
                ;;
        esac
        
        # Skip if already in backup list
        local in_list=false
        for item in "${FILES_TO_BACKUP[@]}"; do
            if [[ "$basename" == "$item" ]]; then
                in_list=true
                break
            fi
        done
        
        if [[ "$in_list" == false ]]; then
            found_files+=("$basename")
        fi
    done < <(find "$HOME" -maxdepth 1 -name ".*" -type f -o -name ".*" -type l 2>/dev/null)
    
    if [[ ${#found_files[@]} -gt 0 ]]; then
        warn "Found additional dotfiles not in backup list:"
        for file in "${found_files[@]}"; do
            echo "  - $file"
        done
        
        echo ""
        echo "Would you like to backup these files as well? (y/n)"
        read -r response
        
        if [[ "$response" == "y" ]]; then
            FILES_TO_BACKUP+=("${found_files[@]}")
            success "Added ${#found_files[@]} additional files to backup"
        fi
    else
        [[ "$VERBOSE" == true ]] && info "No additional dotfiles found"
    fi
}

# Create backup summary
create_summary() {
    if [[ "$DRY_RUN" == true ]]; then
        return 0
    fi
    
    local summary_file="$CURRENT_BACKUP_DIR/SUMMARY.txt"
    local file_count=0
    local total_size=0
    
    # Count files and calculate size
    if [[ -d "$CURRENT_BACKUP_DIR" ]]; then
        file_count=$(find "$CURRENT_BACKUP_DIR" -type f | wc -l)
        
        # Calculate total size (macOS and Linux compatible)
        if [[ "$OS_TYPE" == "macos" ]]; then
            total_size=$(du -sk "$CURRENT_BACKUP_DIR" | cut -f1)
        else
            total_size=$(du -sk "$CURRENT_BACKUP_DIR" | cut -f1)
        fi
    fi
    
    cat > "$summary_file" << EOF
Dotfiles Backup Summary
=======================
Date: $(date)
Location: $CURRENT_BACKUP_DIR
Files Backed Up: $file_count
Total Size: ${total_size}KB

To restore this backup:
-----------------------
1. Remove current dotfiles:
   rm -rf ~/.bashrc ~/.zshrc ~/.vimrc ~/.gitconfig

2. Copy backup files back:
   cp -R $CURRENT_BACKUP_DIR/* ~/

3. Verify restoration:
   ls -la ~/.*

Notes:
------
- This backup includes all configuration files that existed before dotfiles installation
- Symlinks are preserved as symlinks
- Directory structures are maintained
- Original permissions are preserved

EOF
    
    success "Backup summary created: $summary_file"
}

# List existing backups
list_backups() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        warn "No backups found (backup directory does not exist)"
        return 1
    fi
    
    local backups
    backups=$(ls -1d "$BACKUP_DIR"/*/ 2>/dev/null | wc -l)
    
    if [[ $backups -eq 0 ]]; then
        warn "No backups found"
        return 1
    fi
    
    log "Existing backups in $BACKUP_DIR:"
    echo ""
    
    for backup in "$BACKUP_DIR"/*/; do
        if [[ -d "$backup" ]]; then
            local backup_name
            backup_name=$(basename "$backup")
            local summary="$backup/SUMMARY.txt"
            
            echo "  📁 $backup_name"
            
            if [[ -f "$summary" ]]; then
                local file_count
                file_count=$(grep "Files Backed Up:" "$summary" | cut -d: -f2 | tr -d ' ')
                local size
                size=$(grep "Total Size:" "$summary" | cut -d: -f2 | tr -d ' ')
                echo "     Files: $file_count, Size: $size"
            fi
        fi
    done
    echo ""
}

# Clean old backups (keep last N backups)
clean_old_backups() {
    local keep_count=${1:-5}
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        return 0
    fi
    
    local backup_count
    backup_count=$(ls -1d "$BACKUP_DIR"/*/ 2>/dev/null | wc -l)
    
    if [[ $backup_count -le $keep_count ]]; then
        [[ "$VERBOSE" == true ]] && info "No old backups to clean (keeping last $keep_count)"
        return 0
    fi
    
    log "Cleaning old backups (keeping last $keep_count)..."
    
    # Get list of backups sorted by date (oldest first)
    local backups_to_delete
    backups_to_delete=$(ls -1dt "$BACKUP_DIR"/*/ | tail -n +$((keep_count + 1)))
    
    for backup in $backups_to_delete; do
        if [[ -d "$backup" ]]; then
            local backup_name
            backup_name=$(basename "$backup")
            warn "Removing old backup: $backup_name"
            rm -rf "$backup"
        fi
    done
    
    success "Old backups cleaned"
}

# Main backup function
perform_backup() {
    local backed_up_count=0
    local skipped_count=0
    
    for file in "${FILES_TO_BACKUP[@]}"; do
        if needs_backup "$file"; then
            backup_file "$file"
            ((backed_up_count++))
        else
            ((skipped_count++))
        fi
    done
    
    echo ""
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would backup $backed_up_count file(s)"
        info "[DRY RUN] Would skip $skipped_count file(s)"
    else
        success "Backup complete!"
        info "Backed up: $backed_up_count file(s)"
        info "Skipped: $skipped_count file(s)"
        info "Backup location: $CURRENT_BACKUP_DIR"
    fi
}

# Main function
main() {
    echo "==================================="
    echo "      Dotfiles Backup Utility"
    echo "==================================="
    echo ""
    
    # Parse arguments
    parse_args "$@"
    
    # Initialize environment
    detect_os
    export_environment
    
    # Initialize backup
    init_backup
    
    if [[ "$DRY_RUN" == false ]]; then
        # Scan for additional dotfiles
        scan_for_dotfiles
    fi
    
    # Perform backup
    perform_backup
    
    if [[ "$DRY_RUN" == false ]]; then
        # Create summary
        create_summary
        
        # List existing backups
        echo ""
        list_backups
        
        # Clean old backups
        clean_old_backups 5
    fi
    
    echo ""
    success "Backup process completed!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi