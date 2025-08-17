#!/usr/bin/env bash
# Master Installation Script for Mac Dotfiles & Secrets
# Orchestrates complete setup of dotfiles and pass-store repositories
# Target: 5-minute installation on fresh system

set -euo pipefail

# Script version
VERSION="1.0.0"
SCRIPT_START_TIME=$(date +%s)

# Repository URLs
DOTFILES_REPO="https://github.com/smian0/dotfiles.git"
PASS_STORE_REPO="https://github.com/smian0/pass-store.git"
MASTER_REPO="https://github.com/smian0/mac-dotfiles-secrets.git"

# Installation directories
INSTALL_ROOT="${HOME}/.dotfiles-master"
DOTFILES_DIR="${INSTALL_ROOT}/dotfiles"
PASS_STORE_DIR="${HOME}/.password-store"
SCRIPTS_DIR="${DOTFILES_DIR}/scripts"

# Configuration
CLAUDE_PROFILE="${CLAUDE_PROFILE:-default}"
DOTFILES_PROFILE="${DOTFILES_PROFILE:-development}"  # minimal, development, full, work, personal
INSTALL_MODE="${INSTALL_MODE:-interactive}"  # interactive, automatic, minimal
DRY_RUN="${DRY_RUN:-false}"
VERBOSE="${VERBOSE:-false}"

# Progress tracking
TOTAL_STEPS=10
CURRENT_STEP=0

# Rollback tracking
declare -a ROLLBACK_ACTIONS=()

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local percent=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    echo -e "${CYAN}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} ${BOLD}$1${NC} (${percent}%)"
}

# Error handling with rollback
cleanup_on_error() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]] && [[ $exit_code -ne 130 ]]; then  # 130 is Ctrl+C
        error "Installation failed with exit code $exit_code"
        
        if [[ ${#ROLLBACK_ACTIONS[@]} -gt 0 ]]; then
            warn "Performing rollback..."
            for action in "${ROLLBACK_ACTIONS[@]}"; do
                info "Rollback: $action"
                eval "$action" || true
            done
        fi
        
        error "Installation aborted. System has been restored to previous state."
    fi
}

cleanup_on_success() {
    ROLLBACK_ACTIONS=()
}

trap 'cleanup_on_error' ERR

# Show banner
show_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║     Mac Dotfiles & Secrets Installation       ║"
    echo "║                Version $VERSION                   ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --automatic|-a)
                INSTALL_MODE="automatic"
                shift
                ;;
            --minimal|-m)
                INSTALL_MODE="minimal"
                shift
                ;;
            --claude-profile)
                CLAUDE_PROFILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                set -x
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --version)
                echo "Mac Dotfiles Installation Script v$VERSION"
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

Master installation script for Mac dotfiles and secrets management.

OPTIONS:
    -a, --automatic      Run in automatic mode (no prompts)
    -m, --minimal        Minimal installation (core packages only)
    --claude-profile     Select Claude profile (default, experimental)
    --dry-run           Show what would be done without making changes
    -v, --verbose       Show detailed output
    -h, --help          Show this help message
    --version           Show script version

EXAMPLES:
    $(basename "$0")                    # Interactive installation
    $(basename "$0") --automatic        # Automatic installation
    $(basename "$0") --minimal          # Minimal setup
    $(basename "$0") --claude-profile experimental

INSTALLATION MODES:
    interactive  - Prompts for all options (default)
    automatic    - Uses defaults, no prompts
    minimal      - Core packages only (git, zsh, vim)

EOF
}

# Check system requirements
check_system() {
    progress "Checking system requirements"
    
    # Check OS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        error "This script is designed for macOS. Detected: $OSTYPE"
        exit 1
    fi
    
    # Check for required commands
    local required_commands=("curl" "git")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            error "Required command not found: $cmd"
            exit 1
        fi
    done
    
    # Check disk space (need at least 500MB)
    local free_space
    free_space=$(df -k "$HOME" | awk 'NR==2 {print $4}')
    if [[ $free_space -lt 512000 ]]; then
        warn "Low disk space: less than 500MB available"
        if [[ "$INSTALL_MODE" == "interactive" ]]; then
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
        fi
    fi
    
    # Check internet connectivity
    if ! ping -c 1 github.com &>/dev/null; then
        error "No internet connection. Cannot download repositories."
        exit 1
    fi
    
    success "System requirements met"
}

# Install Homebrew if needed
install_homebrew() {
    if ! command -v brew >/dev/null 2>&1; then
        progress "Installing Homebrew"
        
        if [[ "$DRY_RUN" == true ]]; then
            info "[DRY RUN] Would install Homebrew"
            return 0
        fi
        
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        
        ROLLBACK_ACTIONS+=("warn 'Homebrew was installed - manual removal may be needed'")
        success "Homebrew installed"
    else
        info "Homebrew already installed"
    fi
}

# Clone repositories
clone_repositories() {
    progress "Cloning repositories"
    
    # Create installation directory
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would create directory: $INSTALL_ROOT"
    else
        mkdir -p "$INSTALL_ROOT"
        ROLLBACK_ACTIONS+=("rm -rf '$INSTALL_ROOT'")
    fi
    
    # Clone master repository (for reference and scripts)
    if [[ ! -d "$INSTALL_ROOT/.git" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            info "[DRY RUN] Would clone master repository"
        else
            log "Cloning master repository..."
            git clone --recursive "$MASTER_REPO" "$INSTALL_ROOT"
            ROLLBACK_ACTIONS+=("rm -rf '$INSTALL_ROOT'")
        fi
    else
        info "Master repository already exists"
    fi
    
    # Ensure submodules are initialized
    if [[ "$DRY_RUN" == false ]]; then
        cd "$INSTALL_ROOT"
        git submodule update --init --recursive
        cd - >/dev/null
    fi
    
    # Clone pass-store if not exists
    if [[ ! -d "$PASS_STORE_DIR" ]]; then
        if [[ "$INSTALL_MODE" == "interactive" ]]; then
            echo ""
            read -p "Clone pass-store repository? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                CLONE_PASS=true
            else
                CLONE_PASS=false
            fi
        else
            CLONE_PASS=true
        fi
        
        if [[ "$CLONE_PASS" == true ]]; then
            if [[ "$DRY_RUN" == true ]]; then
                info "[DRY RUN] Would clone pass-store repository"
            else
                log "Cloning pass-store repository..."
                git clone "$PASS_STORE_REPO" "$PASS_STORE_DIR"
                ROLLBACK_ACTIONS+=("rm -rf '$PASS_STORE_DIR'")
            fi
        fi
    else
        info "Pass store already exists"
    fi
    
    success "Repositories cloned"
}

# Install dependencies using os-detect.sh
install_dependencies() {
    progress "Installing dependencies"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would install dependencies"
        return 0
    fi
    
    # Source os-detect.sh if available
    if [[ -f "$SCRIPTS_DIR/os-detect.sh" ]]; then
        log "Using os-detect.sh for dependency installation..."
        cd "$DOTFILES_DIR"
        
        # Run in automatic mode if not interactive
        if [[ "$INSTALL_MODE" == "automatic" ]]; then
            echo "y" | bash "$SCRIPTS_DIR/os-detect.sh"
        else
            bash "$SCRIPTS_DIR/os-detect.sh"
        fi
        
        cd - >/dev/null
    else
        # Fallback to basic installation
        warn "os-detect.sh not found, using basic installation"
        
        # Install required packages with Homebrew
        local packages=("stow" "gnupg" "pass" "pinentry-mac" "zsh" "node")
        
        for package in "${packages[@]}"; do
            if ! brew list "$package" &>/dev/null; then
                log "Installing $package..."
                brew install "$package"
            fi
        done
    fi
    
    success "Dependencies installed"
}

# Install global npm packages
install_npm_packages() {
    progress "Installing global npm packages"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would install npm packages"
        return 0
    fi
    
    # Check if npm is available
    if ! command -v npm >/dev/null 2>&1; then
        warn "npm not found. Install Node.js first via Homebrew."
        return 0
    fi
    
    # Use npm packages script if available
    if [[ -f "$SCRIPTS_DIR/npm-packages.sh" ]]; then
        log "Using npm-packages.sh for package installation..."
        cd "$DOTFILES_DIR"
        bash "$SCRIPTS_DIR/npm-packages.sh" install
        cd - >/dev/null
    else
        # Fallback to basic package installation
        warn "npm-packages.sh not found, installing basic packages"
        
        local packages=("ccstatusline" "@anthropic-ai/claude-cli")
        
        for package in "${packages[@]}"; do
            if npm list -g "$package" >/dev/null 2>&1; then
                success "$package already installed"
            else
                log "Installing $package..."
                npm install -g "$package"
                success "$package installed"
            fi
        done
    fi
    
    success "Global npm packages installed"
}

# Setup GPG
setup_gpg() {
    progress "Setting up GPG"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would configure GPG"
        return 0
    fi
    
    # Use GPG manager script if available
    if [[ -f "$SCRIPTS_DIR/gpg-manager.sh" ]]; then
        log "Using GPG manager for setup..."
        cd "$DOTFILES_DIR"
        bash "$SCRIPTS_DIR/gpg-manager.sh" setup
        cd - >/dev/null
    else
        # Fallback to basic GPG setup
        warn "GPG manager not found, using basic setup"
        
        # Check if GPG key exists
        if gpg --list-secret-keys 2>/dev/null | grep -q "sec"; then
            info "GPG key already exists"
        else
            if [[ "$INSTALL_MODE" == "interactive" ]]; then
                warn "No GPG key found"
                echo "Options:"
                echo "  1) Generate new GPG key"
                echo "  2) Import existing GPG key"
                echo "  3) Skip GPG setup"
                read -p "Select option (1-3): " -n 1 -r
                echo
                
                case $REPLY in
                    1)
                        log "Generating new GPG key..."
                        gpg --full-generate-key
                        ;;
                    2)
                        read -p "Enter path to GPG key file: " key_file
                        if [[ -f "$key_file" ]]; then
                            gpg --import "$key_file"
                        else
                            warn "File not found: $key_file"
                        fi
                        ;;
                    3)
                        warn "Skipping GPG setup"
                        ;;
                esac
            else
                warn "No GPG key found. Skipping GPG setup."
            fi
        fi
        
        # Configure pinentry for macOS
        if [[ ! -f "$HOME/.gnupg/gpg-agent.conf" ]]; then
            mkdir -p "$HOME/.gnupg"
            echo "pinentry-program /opt/homebrew/bin/pinentry-mac" > "$HOME/.gnupg/gpg-agent.conf"
            gpgconf --kill gpg-agent
        fi
    fi
    
    success "GPG configured"
}

# Initialize pass
initialize_pass() {
    progress "Initializing password store"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would initialize pass"
        return 0
    fi
    
    # Use pass manager script if available
    if [[ -f "$SCRIPTS_DIR/pass-manager.sh" ]]; then
        log "Using pass manager for setup..."
        cd "$DOTFILES_DIR"
        
        # Initialize pass store
        bash "$SCRIPTS_DIR/pass-manager.sh" init
        
        # Set up directory structure and Git
        bash "$SCRIPTS_DIR/pass-manager.sh" setup
        
        cd - >/dev/null
    else
        # Fallback to basic pass setup
        warn "Pass manager not found, using basic setup"
        
        # Check if pass is already initialized
        if [[ -f "$PASS_STORE_DIR/.gpg-id" ]]; then
            info "Pass already initialized"
        else
            # Get GPG key ID
            local gpg_id
            gpg_id=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep "sec" | head -1 | awk '{print $2}' | cut -d'/' -f2)
            
            if [[ -n "$gpg_id" ]]; then
                log "Initializing pass with GPG key: $gpg_id"
                pass init "$gpg_id"
            else
                warn "No GPG key found. Cannot initialize pass."
                warn "Run 'pass init <gpg-key-id>' manually after setting up GPG."
            fi
        fi
    fi
    
    success "Pass initialized"
}

# Backup existing configurations
backup_configurations() {
    progress "Backing up existing configurations"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would backup existing configurations"
        return 0
    fi
    
    # Use backup.sh if available
    if [[ -f "$SCRIPTS_DIR/backup.sh" ]]; then
        log "Using backup.sh for configuration backup..."
        cd "$DOTFILES_DIR"
        
        if [[ "$INSTALL_MODE" == "automatic" ]]; then
            bash "$SCRIPTS_DIR/backup.sh" --dry-run=false
        else
            bash "$SCRIPTS_DIR/backup.sh"
        fi
        
        cd - >/dev/null
    else
        # Fallback to basic backup
        warn "backup.sh not found, using basic backup"
        
        local backup_dir="$HOME/.dotfiles-backup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        local files_to_backup=(".zshrc" ".vimrc" ".gitconfig" ".claude" ".claude.json")
        for file in "${files_to_backup[@]}"; do
            if [[ -e "$HOME/$file" ]] && [[ ! -L "$HOME/$file" ]]; then
                cp -R "$HOME/$file" "$backup_dir/"
                info "Backed up $file"
            fi
        done
    fi
    
    success "Configurations backed up"
}

# Deploy dotfiles with Stow
deploy_dotfiles() {
    progress "Deploying dotfiles with GNU Stow"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would deploy dotfiles"
        return 0
    fi
    
    cd "$DOTFILES_DIR"
    
    # Use profile manager if available
    if [[ -f "scripts/profile-manager.sh" ]]; then
        log "Using profile manager to deploy: $DOTFILES_PROFILE"
        bash "scripts/profile-manager.sh" install "$DOTFILES_PROFILE"
        success "Profile $DOTFILES_PROFILE deployed"
        cd - >/dev/null
        return 0
    fi
    
    # Fallback to legacy package selection
    local packages=()
    
    if [[ "$INSTALL_MODE" == "minimal" ]]; then
        packages=("git" "zsh" "vim")
    elif [[ "$INSTALL_MODE" == "automatic" ]]; then
        packages=("git" "zsh" "vim" "claude-${CLAUDE_PROFILE}")
    else
        # Interactive mode - let user choose
        log "Available packages:"
        local available_packages=($(find . -maxdepth 1 -type d -not -path '.' -not -path './.git' -not -path './scripts' | sed 's|^\./||' | sort))
        
        for i in "${!available_packages[@]}"; do
            echo "  $((i+1))) ${available_packages[$i]}"
        done
        
        echo ""
        read -p "Enter package numbers to install (space-separated, or 'all'): " -r
        
        if [[ "$REPLY" == "all" ]]; then
            packages=("${available_packages[@]}")
        else
            for num in $REPLY; do
                if [[ $num -gt 0 ]] && [[ $num -le ${#available_packages[@]} ]]; then
                    packages+=("${available_packages[$((num-1))]}")
                fi
            done
        fi
    fi
    
    # Deploy selected packages
    for package in "${packages[@]}"; do
        if [[ -d "$package" ]]; then
            log "Stowing $package..."
            
            # Remove existing files if they're not symlinks
            case "$package" in
                claude-*)
                    [[ -e "$HOME/.claude" ]] && [[ ! -L "$HOME/.claude" ]] && rm -rf "$HOME/.claude"
                    [[ -e "$HOME/.claude.json" ]] && [[ ! -L "$HOME/.claude.json" ]] && rm -f "$HOME/.claude.json"
                    ;;
                zsh)
                    [[ -e "$HOME/.zshrc" ]] && [[ ! -L "$HOME/.zshrc" ]] && rm -f "$HOME/.zshrc"
                    ;;
                git)
                    [[ -e "$HOME/.gitconfig" ]] && [[ ! -L "$HOME/.gitconfig" ]] && rm -f "$HOME/.gitconfig"
                    ;;
                vim)
                    [[ -e "$HOME/.vimrc" ]] && [[ ! -L "$HOME/.vimrc" ]] && rm -f "$HOME/.vimrc"
                    ;;
            esac
            
            stow -v "$package"
            ROLLBACK_ACTIONS+=("cd '$DOTFILES_DIR' && stow -D '$package'")
            success "Stowed $package"
        else
            warn "Package $package not found"
        fi
    done
    
    cd - >/dev/null
    success "Dotfiles deployed"
}

# Validate installation
validate_installation() {
    progress "Validating installation"
    
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would validate installation"
        return 0
    fi
    
    # Use validate-config.sh if available
    if [[ -f "$SCRIPTS_DIR/validate-config.sh" ]]; then
        log "Running configuration validation..."
        cd "$DOTFILES_DIR"
        bash "$SCRIPTS_DIR/validate-config.sh" || warn "Some validation checks failed"
        cd - >/dev/null
    else
        # Basic validation
        local validation_passed=true
        
        # Check for symlinks
        if [[ -L "$HOME/.zshrc" ]]; then
            success ".zshrc is properly linked"
        else
            warn ".zshrc is not a symlink"
            validation_passed=false
        fi
        
        # Check for pass initialization
        if [[ -f "$PASS_STORE_DIR/.gpg-id" ]]; then
            success "Pass is initialized"
        else
            warn "Pass is not initialized"
            validation_passed=false
        fi
        
        if [[ "$validation_passed" == true ]]; then
            success "Basic validation passed"
        else
            warn "Some validation checks failed"
        fi
    fi
}

# Post-installation setup
post_installation() {
    progress "Completing installation"
    
    # Set executable permissions for Claude helper
    if [[ -f "$HOME/.claude/anthropic_key_helper.sh" ]]; then
        chmod +x "$HOME/.claude/anthropic_key_helper.sh"
        success "Claude API helper configured"
    fi
    
    # Calculate installation time
    local end_time=$(date +%s)
    local duration=$((end_time - SCRIPT_START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    echo ""
    echo "═══════════════════════════════════════════════════"
    success "Installation completed in ${minutes}m ${seconds}s!"
    echo "═══════════════════════════════════════════════════"
    echo ""
    
    # Show next steps
    log "Next steps:"
    echo ""
    echo "  1. Restart your terminal or run:"
    echo "     ${CYAN}source ~/.zshrc${NC}"
    echo ""
    echo "  2. Configure GPG and pass (if not done):"
    echo "     ${CYAN}gpg --full-generate-key${NC}"
    echo "     ${CYAN}pass init <your-gpg-key-id>${NC}"
    echo ""
    echo "  3. Add API keys to pass:"
    echo "     ${CYAN}pass insert api/anthropic${NC}"
    echo ""
    echo "  4. Verify Claude Code configuration:"
    echo "     ${CYAN}claude doctor${NC}"
    echo ""
    echo "  5. Review installed packages:"
    echo "     ${CYAN}cd $DOTFILES_DIR && stow -n -v *${NC}"
    echo ""
    
    if [[ "$VERBOSE" == true ]]; then
        echo "Installation details:"
        echo "  - Installation root: $INSTALL_ROOT"
        echo "  - Dotfiles: $DOTFILES_DIR"
        echo "  - Pass store: $PASS_STORE_DIR"
        echo "  - Claude profile: $CLAUDE_PROFILE"
    fi
    
    # Check if we met the 5-minute target
    if [[ $duration -le 300 ]]; then
        success "✨ Target met: Installation completed in under 5 minutes!"
    else
        info "Installation took longer than 5 minutes. Consider using --automatic mode for faster setup."
    fi
}

# Main installation flow
main() {
    show_banner
    parse_args "$@"
    
    # Confirm installation in interactive mode
    if [[ "$INSTALL_MODE" == "interactive" ]] && [[ "$DRY_RUN" == false ]]; then
        echo "This will install and configure:"
        echo "  • Homebrew package manager (if needed)"
        echo "  • Dotfiles from GitHub"
        echo "  • Pass password store"
        echo "  • GNU Stow for symlink management"
        echo "  • GPG for encryption"
        echo "  • Global npm packages (ccstatusline, claude-cli, etc.)"
        echo "  • Claude Code configuration"
        echo ""
        read -p "Continue with installation? (y/n) " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
    fi
    
    # Run installation steps
    check_system
    install_homebrew
    clone_repositories
    install_dependencies
    install_npm_packages
    setup_gpg
    initialize_pass
    backup_configurations
    deploy_dotfiles
    validate_installation
    post_installation
    
    # Clear rollback actions on success
    cleanup_on_success
    
    exit 0
}

# Run main function
main "$@"