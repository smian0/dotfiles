#!/usr/bin/env bash
# OS Detection and Environment Setup
# Provides cross-platform compatibility layer for dotfiles installation

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; return 1; }
success() { echo -e "${GREEN}✓${NC} $1"; }

# Global variables
OS_TYPE=""
DISTRO=""
PKG_MANAGER=""
PKG_INSTALL_CMD=""
PKG_UPDATE_CMD=""
PKG_SEARCH_CMD=""

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        DISTRO="macOS"
        PKG_MANAGER="brew"
        PKG_INSTALL_CMD="brew install"
        PKG_UPDATE_CMD="brew update"
        PKG_SEARCH_CMD="brew list"
        
        # Check macOS version
        local macos_version
        macos_version=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
        [[ "${QUIET_MODE:-false}" != "true" ]] && info "Detected macOS version: $macos_version"
        
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
        
        # Detect specific Linux distribution
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            DISTRO="$NAME"
            
            case "$ID" in
                ubuntu|debian)
                    PKG_MANAGER="apt"
                    PKG_INSTALL_CMD="sudo apt-get install -y"
                    PKG_UPDATE_CMD="sudo apt-get update"
                    PKG_SEARCH_CMD="dpkg -l"
                    ;;
                fedora|rhel|centos)
                    PKG_MANAGER="dnf"
                    PKG_INSTALL_CMD="sudo dnf install -y"
                    PKG_UPDATE_CMD="sudo dnf update"
                    PKG_SEARCH_CMD="rpm -qa"
                    ;;
                arch|manjaro)
                    PKG_MANAGER="pacman"
                    PKG_INSTALL_CMD="sudo pacman -S --noconfirm"
                    PKG_UPDATE_CMD="sudo pacman -Syu"
                    PKG_SEARCH_CMD="pacman -Q"
                    ;;
                *)
                    warn "Unknown Linux distribution: $ID"
                    PKG_MANAGER="unknown"
                    ;;
            esac
        else
            DISTRO="Unknown Linux"
            PKG_MANAGER="unknown"
        fi
    else
        OS_TYPE="unknown"
        DISTRO="Unknown OS"
        PKG_MANAGER="unknown"
        warn "Unknown operating system: $OSTYPE"
    fi
    
    [[ "${QUIET_MODE:-false}" != "true" ]] && log "Detected OS: $DISTRO ($OS_TYPE)"
    [[ "${QUIET_MODE:-false}" != "true" ]] && log "Package manager: $PKG_MANAGER"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Homebrew on macOS
check_homebrew() {
    if [[ "$OS_TYPE" == "macos" ]]; then
        if ! command_exists brew; then
            warn "Homebrew is not installed"
            echo "Install Homebrew? (y/n)"
            read -r response
            if [[ "$response" == "y" ]]; then
                install_homebrew
            else
                error "Homebrew is required on macOS. Please install it manually."
            fi
        else
            success "Homebrew is installed"
            # Update Homebrew
            info "Updating Homebrew..."
            brew update >/dev/null 2>&1 || warn "Failed to update Homebrew"
        fi
    fi
}

# Install Homebrew
install_homebrew() {
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    success "Homebrew installed successfully"
}

# Generic package installation function
install_package() {
    local package=$1
    local package_name=${2:-$package}  # Display name (optional)
    
    log "Installing $package_name..."
    
    case "$PKG_MANAGER" in
        brew)
            brew install "$package" || return 1
            ;;
        apt)
            sudo apt-get install -y "$package" || return 1
            ;;
        dnf)
            sudo dnf install -y "$package" || return 1
            ;;
        pacman)
            sudo pacman -S --noconfirm "$package" || return 1
            ;;
        *)
            error "Unsupported package manager: $PKG_MANAGER"
            return 1
            ;;
    esac
    
    success "$package_name installed successfully"
}

# Check if a package is installed
is_package_installed() {
    local package=$1
    
    case "$PKG_MANAGER" in
        brew)
            brew list "$package" &>/dev/null
            ;;
        apt)
            dpkg -l "$package" 2>/dev/null | grep -q "^ii"
            ;;
        dnf)
            rpm -qa | grep -q "^$package"
            ;;
        pacman)
            pacman -Q "$package" &>/dev/null
            ;;
        *)
            return 1
            ;;
    esac
}

# Map generic package names to OS-specific names
get_package_name() {
    local generic_name=$1
    
    case "$generic_name" in
        "gpg")
            case "$OS_TYPE" in
                macos) echo "gnupg" ;;
                linux) echo "gnupg" ;;
            esac
            ;;
        "node")
            case "$OS_TYPE" in
                macos) echo "node" ;;
                linux) echo "nodejs" ;;
            esac
            ;;
        "pass")
            case "$OS_TYPE" in
                macos) echo "pass" ;;
                linux) echo "pass" ;;
            esac
            ;;
        *)
            echo "$generic_name"
            ;;
    esac
}

# Check for required dependencies
check_dependencies() {
    log "Checking required dependencies..."
    
    local dependencies=(
        "git:Git version control"
        "stow:GNU Stow for symlink management"
        "gpg:GPG for encryption"
        "pass:Password store"
        "zsh:Z shell"
        "node:Node.js runtime"
    )
    
    local missing_deps=()
    
    for dep_info in "${dependencies[@]}"; do
        IFS=':' read -r dep description <<< "$dep_info"
        
        # Get OS-specific package name
        local package_name
        package_name=$(get_package_name "$dep")
        
        if command_exists "$dep"; then
            success "$description is installed"
        else
            warn "$description is not installed"
            missing_deps+=("$package_name:$description")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo ""
        warn "The following dependencies are missing:"
        for dep_info in "${missing_deps[@]}"; do
            IFS=':' read -r dep description <<< "$dep_info"
            echo "  - $description"
        done
        
        echo ""
        echo "Would you like to install missing dependencies? (y/n)"
        read -r response
        
        if [[ "$response" == "y" ]]; then
            install_missing_dependencies "${missing_deps[@]}"
        else
            warn "Some dependencies are missing. Installation may not work correctly."
        fi
    else
        success "All required dependencies are installed!"
    fi
}

# Install missing dependencies
install_missing_dependencies() {
    local deps=("$@")
    
    # Update package manager first
    log "Updating package manager..."
    case "$PKG_MANAGER" in
        brew)
            brew update || warn "Failed to update Homebrew"
            ;;
        apt)
            sudo apt-get update || warn "Failed to update APT"
            ;;
        dnf)
            sudo dnf check-update || true  # Returns non-zero if updates available
            ;;
        pacman)
            sudo pacman -Sy || warn "Failed to update Pacman"
            ;;
    esac
    
    # Install each missing dependency
    for dep_info in "${deps[@]}"; do
        IFS=':' read -r package description <<< "$dep_info"
        
        if install_package "$package" "$description"; then
            success "$description installed successfully"
        else
            error "Failed to install $description"
        fi
    done
}

# Check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check disk space (need at least 100MB free)
    local free_space
    if [[ "$OS_TYPE" == "macos" ]]; then
        free_space=$(df -k . | awk 'NR==2 {print $4}')
    else
        free_space=$(df -k . | awk 'NR==2 {print $4}')
    fi
    
    if [[ $free_space -lt 102400 ]]; then
        warn "Low disk space: less than 100MB available"
    else
        success "Sufficient disk space available"
    fi
    
    # Check internet connectivity
    if ping -c 1 github.com &>/dev/null; then
        success "Internet connection available"
    else
        warn "No internet connection detected. Some features may not work."
    fi
    
    # Check if running with appropriate permissions
    if [[ "$OS_TYPE" == "linux" ]] && [[ $EUID -eq 0 ]]; then
        warn "Running as root. It's recommended to run as a normal user."
    fi
}

# Export environment variables
export_environment() {
    export DOTFILES_OS="$OS_TYPE"
    export DOTFILES_DISTRO="$DISTRO"
    export DOTFILES_PKG_MANAGER="$PKG_MANAGER"
    
    info "Environment variables set:"
    echo "  DOTFILES_OS=$DOTFILES_OS"
    echo "  DOTFILES_DISTRO=$DOTFILES_DISTRO"
    echo "  DOTFILES_PKG_MANAGER=$DOTFILES_PKG_MANAGER"
}

# Main function
main() {
    echo "==================================="
    echo "   OS Detection & Dependency Check"
    echo "==================================="
    echo ""
    
    detect_os
    
    if [[ "$OS_TYPE" == "unknown" ]]; then
        error "Unable to detect operating system. Manual configuration required."
    fi
    
    if [[ "$OS_TYPE" == "macos" ]]; then
        check_homebrew
    fi
    
    check_system_requirements
    check_dependencies
    export_environment
    
    echo ""
    success "OS detection and dependency check complete!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi