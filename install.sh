#!/usr/bin/env bash
# Dotfiles installation script
# Supports macOS and Ubuntu Linux

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            if [[ "$ID" == "ubuntu" ]]; then
                echo "ubuntu"
            else
                echo "linux"
            fi
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
log "Detected OS: $OS"

# Check if running from dotfiles directory
if [[ ! -f ".stow-global-ignore" ]]; then
    error "Must run from dotfiles repository root directory"
fi

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    if [[ "$OS" == "macos" ]]; then
        # Check if Homebrew is installed
        if ! command -v brew >/dev/null 2>&1; then
            warn "Homebrew not installed. Installing..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install required packages
        brew install stow pass gnupg pinentry-mac git
        
    elif [[ "$OS" == "ubuntu" ]]; then
        # Update package list
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y stow pass gnupg2 git curl
        
    else
        warn "Unknown OS. Please install manually: stow, pass, gpg, git"
    fi
}

# Check for required tools
check_requirements() {
    local missing_tools=()
    
    for tool in git stow; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        warn "Missing required tools: ${missing_tools[*]}"
        read -p "Install missing dependencies? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            error "Required tools not installed. Exiting."
        fi
    fi
}

# Core packages to install
CORE_PACKAGES=("git" "zsh" "vim")
CLAUDE_PACKAGE="claude-default"

# Parse command line arguments
PACKAGES=()
INSTALL_ALL=false
CLAUDE_PROFILE="default"
DRY_RUN=false
PROFILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            INSTALL_ALL=true
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --claude-profile)
            CLAUDE_PROFILE="$2"
            CLAUDE_PACKAGE="claude-$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options] [packages...]"
            echo "Options:"
            echo "  --all              Install all available packages"
            echo "  --profile NAME     Install specific profile (minimal, development, full, work, personal)"
            echo "  --claude-profile   Select Claude profile (default, experimental)"
            echo "  --dry-run          Show what would be installed without making changes"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Install core packages"
            echo "  $0 --all           # Install everything"
            echo "  $0 --profile development  # Install development profile"
            echo "  $0 git zsh         # Install specific packages"
            exit 0
            ;;
        *)
            PACKAGES+=("$1")
            shift
            ;;
    esac
done

# Check requirements
check_requirements

# Determine what to install
if [[ -n "$PROFILE" ]]; then
    # Load packages from profile
    PROFILE_FILE="profiles/${PROFILE}.txt"
    if [[ -f "$PROFILE_FILE" ]]; then
        log "Installing profile: $PROFILE"
        PACKAGES=()
        while IFS= read -r package; do
            [[ -n "$package" ]] && PACKAGES+=("$package")
        done < "$PROFILE_FILE"
    else
        error "Profile not found: $PROFILE"
    fi
elif [[ $INSTALL_ALL == true ]]; then
    log "Installing all packages..."
    PACKAGES=($(find . -maxdepth 1 -type d -not -path '.' -not -path './.git' -not -path './scripts' -not -path './profiles' | sed 's|^\./||'))
elif [[ ${#PACKAGES[@]} -eq 0 ]]; then
    log "Installing core packages and Claude profile: $CLAUDE_PROFILE..."
    PACKAGES=("${CORE_PACKAGES[@]}" "$CLAUDE_PACKAGE")
fi

# Handle dry run mode
if [[ $DRY_RUN == true ]]; then
    log "DRY RUN MODE - No changes will be made"
    log "Would install packages: ${PACKAGES[*]}"
    exit 0
fi

# Backup existing configurations
backup_existing() {
    local target="$1"
    if [[ -e "$HOME/$target" ]] && [[ ! -L "$HOME/$target" ]]; then
        warn "Backing up existing $target to $target.backup"
        mv "$HOME/$target" "$HOME/$target.backup"
    fi
}

# Install packages with Stow
log "Installing packages: ${PACKAGES[*]}"
for package in "${PACKAGES[@]}"; do
    if [[ -d "$package" ]]; then
        log "Stowing $package..."
        
        # Handle special cases
        if [[ "$package" == claude-* ]]; then
            backup_existing ".claude"
            backup_existing ".claude.json"
        elif [[ "$package" == "zsh" ]]; then
            backup_existing ".zshrc"
        elif [[ "$package" == "git" ]]; then
            backup_existing ".gitconfig"
        elif [[ "$package" == "vim" ]]; then
            backup_existing ".vimrc"
        fi
        
        stow -v "$package"
    else
        warn "Package $package not found, skipping"
    fi
done

# Special setup for Claude
if [[ " ${PACKAGES[@]} " =~ " $CLAUDE_PACKAGE " ]]; then
    if [[ -x "$HOME/.claude/anthropic_key_helper.sh" ]]; then
        log "API key helper is executable"
    else
        warn "Making API key helper executable..."
        chmod +x "$HOME/.claude/anthropic_key_helper.sh"
    fi
fi

# Clone pass-store repository if it doesn't exist
if [[ ! -d "$HOME/.password-store" ]]; then
    log "Pass store not found. Would you like to clone it?"
    read -p "Clone pass-store repository? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git clone git@github.com:smian0/pass-store.git "$HOME/.password-store"
        log "Pass store cloned to ~/.password-store"
    fi
fi

log "✅ Dotfiles installation completed!"
log ""
log "Next steps:"
log "1. Configure GPG key for pass (if not already done)"
log "2. Add API keys to pass: pass insert api/anthropic"
log "3. Restart your shell or run: source ~/.zshrc"
log "4. Run 'stow <package>' to add more configurations"

if command -v claude >/dev/null 2>&1; then
    log ""
    log "🤖 Claude Code detected. Run 'claude doctor' to verify configuration"
fi