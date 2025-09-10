#!/usr/bin/env bash
# Pass Password Store Manager
# Manages pass password store setup, structure, and sync

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
PASS_STORE_DIR="${PASSWORD_STORE_DIR:-$HOME/.password-store}"
PASS_REPO_URL="${PASS_REPO_URL:-git@github.com:smian0/pass.git}"

# Parse command line arguments
ACTION=""
GPG_KEY_ID=""
DRY_RUN=false
VERBOSE=false
FORCE=false

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            init)
                ACTION="init"
                shift
                ;;
            setup)
                ACTION="setup"
                shift
                ;;
            sync)
                ACTION="sync"
                shift
                ;;
            status)
                ACTION="status"
                shift
                ;;
            backup)
                ACTION="backup"
                shift
                ;;
            clone)
                ACTION="clone"
                shift
                ;;
            --gpg-key)
                GPG_KEY_ID="$2"
                shift 2
                ;;
            --force)
                FORCE=true
                shift
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
Pass Password Store Manager

Usage: $(basename "$0") ACTION [OPTIONS]

ACTIONS:
    init            Initialize new pass store with GPG key
    setup           Set up directory structure and Git repo
    sync            Sync with remote Git repository
    status          Show pass store status
    backup          Create backup of pass store
    clone           Clone existing pass store from Git

OPTIONS:
    --gpg-key ID    GPG key ID to use for pass
    --force         Force action even if conflicts
    --dry-run       Show what would be done
    --verbose       Show detailed output
    --help          Show this help

EXAMPLES:
    $(basename "$0") init --gpg-key ABC123          # Initialize with specific key
    $(basename "$0") setup                          # Set up directory structure
    $(basename "$0") sync                           # Sync with Git remote
    $(basename "$0") status                         # Show current status
    $(basename "$0") clone                          # Clone from existing repo

DIRECTORY STRUCTURE:
    ~/.password-store/
    ├── api/                    # API keys (anthropic, github, etc.)
    ├── services/               # Service accounts
    ├── personal/               # Personal credentials
    └── .git/                   # Git repository

EOF
}

# Check dependencies
check_dependencies() {
    local missing=()
    
    if ! command -v pass >/dev/null 2>&1; then
        missing+=("pass")
    fi
    
    if ! command -v gpg >/dev/null 2>&1; then
        missing+=("gpg")
    fi
    
    if ! command -v git >/dev/null 2>&1; then
        missing+=("git")
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing[*]}"
        info "Install with: brew install ${missing[*]}"
        return 1
    fi
    
    [[ "$VERBOSE" == true ]] && info "All dependencies available"
}

# Get available GPG keys
get_gpg_keys() {
    gpg --list-secret-keys --keyid-format LONG 2>/dev/null | \
    grep "sec" | awk '{print $2}' | cut -d'/' -f2
}

# Prompt for GPG key if not specified
select_gpg_key() {
    if [[ -n "$GPG_KEY_ID" ]]; then
        return 0
    fi
    
    local keys
    keys=($(get_gpg_keys))
    
    if [[ ${#keys[@]} -eq 0 ]]; then
        error "No GPG keys found. Generate one first with: gpg --full-generate-key"
    fi
    
    if [[ ${#keys[@]} -eq 1 ]]; then
        GPG_KEY_ID="${keys[0]}"
        info "Using GPG key: $GPG_KEY_ID"
        return 0
    fi
    
    info "Multiple GPG keys found:"
    for i in "${!keys[@]}"; do
        local key="${keys[$i]}"
        local name
        name=$(gpg --list-keys --keyid-format LONG "$key" 2>/dev/null | grep "uid" | head -1 | sed 's/.*] //')
        echo "  $((i+1))) $key ($name)"
    done
    
    echo ""
    read -p "Select key (1-${#keys[@]}): " -r choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#keys[@]} ]]; then
        GPG_KEY_ID="${keys[$((choice-1))]}"
        info "Selected GPG key: $GPG_KEY_ID"
    else
        error "Invalid selection"
    fi
}

# Initialize pass store
init_pass() {
    log "Initializing pass password store..."
    
    if [[ -f "$PASS_STORE_DIR/.gpg-id" ]] && [[ "$FORCE" == false ]]; then
        warn "Pass store already initialized"
        return 0
    fi
    
    select_gpg_key
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would initialize pass with key: $GPG_KEY_ID"
        return 0
    fi
    
    # Initialize pass
    pass init "$GPG_KEY_ID"
    success "Pass store initialized with GPG key: $GPG_KEY_ID"
}

# Set up directory structure
setup_structure() {
    log "Setting up pass store directory structure..."
    
    local directories=(
        "api"
        "services" 
        "personal"
        "personal/banking"
        "personal/social"
        "services/cloud"
        "services/dev"
    )
    
    for dir in "${directories[@]}"; do
        local full_path="$PASS_STORE_DIR/$dir"
        
        if [[ "$DRY_RUN" == true ]]; then
            info "[DRY RUN] Would create directory: $dir"
            continue
        fi
        
        if [[ ! -d "$full_path" ]]; then
            mkdir -p "$full_path"
            
            # Create .gitkeep to ensure directory is tracked
            touch "$full_path/.gitkeep"
            success "Created directory: $dir"
        else
            [[ "$VERBOSE" == true ]] && info "Directory exists: $dir"
        fi
    done
    
    # Create README
    if [[ "$DRY_RUN" == false ]]; then
        create_readme
    fi
}

# Create README file
create_readme() {
    local readme_file="$PASS_STORE_DIR/README.md"
    
    if [[ -f "$readme_file" ]] && [[ "$FORCE" == false ]]; then
        [[ "$VERBOSE" == true ]] && info "README already exists"
        return 0
    fi
    
    cat > "$readme_file" << 'EOF'
# Password Store

This repository contains encrypted passwords and API keys using `pass`.

## Structure

- `api/` - API keys for services (anthropic, github, openai, etc.)
- `services/` - Service account credentials
  - `cloud/` - Cloud service accounts  
  - `dev/` - Development tools and services
- `personal/` - Personal accounts
  - `banking/` - Financial accounts
  - `social/` - Social media accounts

## Usage

```bash
# List all passwords
pass

# Show specific password
pass show api/anthropic

# Add new password
pass insert api/new-service

# Generate random password
pass generate services/cloud/aws 32

# Copy to clipboard
pass -c api/anthropic
```

## Git Sync

This store is synchronized with Git for backup and multi-machine access.

```bash
# Pull latest changes
pass git pull

# Push changes
pass git push
```

## Security

- All passwords are encrypted with GPG
- Only authorized GPG keys can decrypt
- Git repository can be safely stored anywhere
- Always verify GPG key before adding new machines

EOF
    
    success "Created README.md"
}

# Set up Git repository
setup_git() {
    log "Setting up Git repository for pass store..."
    
    cd "$PASS_STORE_DIR"
    
    if [[ ! -d ".git" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            info "[DRY RUN] Would initialize Git repository"
        else
            git init
            success "Initialized Git repository"
        fi
    fi
    
    # Configure Git settings
    if [[ "$DRY_RUN" == false ]]; then
        git config user.name "$(git config --global user.name 2>/dev/null || echo 'Pass Store')"
        git config user.email "$(git config --global user.email 2>/dev/null || echo 'pass@localhost')"
        
        # Add remote if it doesn't exist
        if ! git remote get-url origin >/dev/null 2>&1; then
            if [[ -n "$PASS_REPO_URL" ]]; then
                git remote add origin "$PASS_REPO_URL"
                success "Added remote: $PASS_REPO_URL"
            fi
        fi
    fi
    
    cd - >/dev/null
}

# Sync with remote repository
sync_pass() {
    log "Syncing pass store with Git remote..."
    
    if [[ ! -d "$PASS_STORE_DIR/.git" ]]; then
        error "Pass store is not a Git repository. Run setup first."
    fi
    
    cd "$PASS_STORE_DIR"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would sync with Git remote"
        cd - >/dev/null
        return 0
    fi
    
    # Check if we have uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        info "Committing local changes..."
        git add .
        git commit -m "Update passwords $(date '+%Y-%m-%d %H:%M:%S')" || true
    fi
    
    # Pull changes
    if git remote get-url origin >/dev/null 2>&1; then
        info "Pulling from remote..."
        git pull origin main --rebase || {
            warn "Pull failed, continuing..."
        }
        
        info "Pushing to remote..."
        git push origin main || {
            warn "Push failed, manual intervention may be needed"
        }
        
        success "Sync completed"
    else
        warn "No remote configured, skipping sync"
    fi
    
    cd - >/dev/null
}

# Show pass store status
show_status() {
    log "Pass store status:"
    echo ""
    
    # Check if pass is initialized
    if [[ -f "$PASS_STORE_DIR/.gpg-id" ]]; then
        local gpg_id
        gpg_id=$(cat "$PASS_STORE_DIR/.gpg-id")
        success "Pass initialized with GPG key: $gpg_id"
        
        # Show key details
        local key_info
        key_info=$(gpg --list-keys --keyid-format LONG "$gpg_id" 2>/dev/null | grep "uid" | head -1 | sed 's/.*] //' || echo "Key details not available")
        info "Key owner: $key_info"
    else
        warn "Pass not initialized"
    fi
    
    # Check directory structure
    if [[ -d "$PASS_STORE_DIR" ]]; then
        info "Store location: $PASS_STORE_DIR"
        
        local count
        count=$(find "$PASS_STORE_DIR" -name "*.gpg" 2>/dev/null | wc -l | tr -d ' ')
        info "Stored passwords: $count"
        
        # Git status
        if [[ -d "$PASS_STORE_DIR/.git" ]]; then
            cd "$PASS_STORE_DIR"
            if git remote get-url origin >/dev/null 2>&1; then
                local remote
                remote=$(git remote get-url origin)
                success "Git remote: $remote"
                
                local status
                status=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
                if [[ "$status" -eq 0 ]]; then
                    success "Git: Clean working directory"
                else
                    warn "Git: $status uncommitted changes"
                fi
            else
                warn "Git: No remote configured"
            fi
            cd - >/dev/null
        else
            warn "Not a Git repository"
        fi
    else
        warn "Pass store directory does not exist"
    fi
}

# Clone existing pass store
clone_pass() {
    log "Cloning pass store from Git repository..."
    
    if [[ -d "$PASS_STORE_DIR" ]] && [[ "$FORCE" == false ]]; then
        error "Pass store directory already exists. Use --force to overwrite."
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would clone from: $PASS_REPO_URL"
        return 0
    fi
    
    if [[ "$FORCE" == true ]] && [[ -d "$PASS_STORE_DIR" ]]; then
        warn "Removing existing pass store directory"
        rm -rf "$PASS_STORE_DIR"
    fi
    
    git clone "$PASS_REPO_URL" "$PASS_STORE_DIR"
    success "Cloned pass store from $PASS_REPO_URL"
    
    # Verify GPG key is available
    if [[ -f "$PASS_STORE_DIR/.gpg-id" ]]; then
        local gpg_id
        gpg_id=$(cat "$PASS_STORE_DIR/.gpg-id")
        
        if gpg --list-secret-keys "$gpg_id" >/dev/null 2>&1; then
            success "GPG key $gpg_id is available"
        else
            warn "GPG key $gpg_id not found in local keyring"
            info "Import the key with: gpg --import your-key.asc"
        fi
    fi
}

# Create backup
create_backup() {
    local backup_file="pass-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
    
    log "Creating pass store backup: $backup_file"
    
    if [[ ! -d "$PASS_STORE_DIR" ]]; then
        error "Pass store directory does not exist"
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would create backup: $backup_file"
        return 0
    fi
    
    tar -czf "$backup_file" -C "$(dirname "$PASS_STORE_DIR")" "$(basename "$PASS_STORE_DIR")"
    success "Backup created: $backup_file"
    
    local size
    size=$(du -h "$backup_file" | cut -f1)
    info "Backup size: $size"
}

# Main function
main() {
    parse_args "$@"
    
    if [[ -z "$ACTION" ]]; then
        error "No action specified"
        show_help
        exit 1
    fi
    
    check_dependencies
    
    case "$ACTION" in
        init)
            init_pass
            ;;
        setup)
            setup_structure
            setup_git
            ;;
        sync)
            sync_pass
            ;;
        status)
            show_status
            ;;
        backup)
            create_backup
            ;;
        clone)
            clone_pass
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