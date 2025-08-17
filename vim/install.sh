#!/usr/bin/env bash
# Vim Package Installation Script
# Installs and configures Vim with basic plugins

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
    OS_TYPE="unknown"
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

# Install Vim if not present
install_vim() {
    if command_exists vim; then
        success "Vim is already installed"
        local vim_version
        vim_version=$(vim --version | head -1)
        info "Version: $vim_version"
        return 0
    fi
    
    log "Installing Vim..."
    
    case "$OS_TYPE" in
        macos)
            if command_exists brew; then
                brew install vim
            else
                error "Homebrew required to install Vim on macOS"
            fi
            ;;
        linux)
            if command_exists apt-get; then
                sudo apt-get update && sudo apt-get install -y vim
            elif command_exists dnf; then
                sudo dnf install -y vim
            elif command_exists pacman; then
                sudo pacman -S --noconfirm vim
            else
                error "Unsupported package manager for Vim installation"
            fi
            ;;
        *)
            error "Unsupported OS for automatic Vim installation"
            ;;
    esac
    
    success "Vim installed successfully"
}

# Create Vim directories
create_vim_directories() {
    log "Creating Vim directories..."
    
    local vim_dirs=(
        "$HOME/.vim"
        "$HOME/.vim/backup"
        "$HOME/.vim/swap"
        "$HOME/.vim/undo"
        "$HOME/.vim/pack"
        "$HOME/.vim/pack/plugins/start"
        "$HOME/.vim/pack/plugins/opt"
    )
    
    for dir in "${vim_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            success "Created directory: $dir"
        else
            info "Directory already exists: $dir"
        fi
    done
}

# Install basic Vim plugins
install_vim_plugins() {
    local pack_dir="$HOME/.vim/pack/plugins/start"
    
    log "Installing basic Vim plugins..."
    
    # vim-sensible (better defaults)
    if [[ ! -d "$pack_dir/vim-sensible" ]]; then
        log "Installing vim-sensible..."
        git clone https://github.com/tpope/vim-sensible.git "$pack_dir/vim-sensible"
        success "vim-sensible installed"
    else
        success "vim-sensible already installed"
    fi
    
    # vim-commentary (commenting)
    if [[ ! -d "$pack_dir/vim-commentary" ]]; then
        log "Installing vim-commentary..."
        git clone https://github.com/tpope/vim-commentary.git "$pack_dir/vim-commentary"
        success "vim-commentary installed"
    else
        success "vim-commentary already installed"
    fi
    
    # vim-surround (surround text objects)
    if [[ ! -d "$pack_dir/vim-surround" ]]; then
        log "Installing vim-surround..."
        git clone https://github.com/tpope/vim-surround.git "$pack_dir/vim-surround"
        success "vim-surround installed"
    else
        success "vim-surround already installed"
    fi
    
    # Generate help tags
    log "Generating help tags..."
    vim -u NONE -c "helptags ALL" -c q
    success "Help tags generated"
}

# Backup existing .vimrc
backup_existing_vimrc() {
    if [[ -f "$HOME/.vimrc" ]] && [[ ! -L "$HOME/.vimrc" ]]; then
        local backup_file="$HOME/.vimrc.backup.$(date +%Y%m%d_%H%M%S)"
        log "Backing up existing .vimrc to $backup_file"
        cp "$HOME/.vimrc" "$backup_file"
        success "Existing .vimrc backed up"
    fi
}

# Install additional development tools
install_dev_tools() {
    log "Installing additional development tools..."
    
    case "$OS_TYPE" in
        macos)
            if command_exists brew; then
                # Install tools that enhance Vim experience
                local tools=("ripgrep" "fd" "bat")
                for tool in "${tools[@]}"; do
                    if ! command_exists "$tool"; then
                        log "Installing $tool..."
                        brew install "$tool"
                        success "$tool installed"
                    else
                        success "$tool already installed"
                    fi
                done
            fi
            ;;
        linux)
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y ripgrep fd-find bat
            elif command_exists dnf; then
                sudo dnf install -y ripgrep fd-find bat
            elif command_exists pacman; then
                sudo pacman -S --noconfirm ripgrep fd bat
            fi
            ;;
    esac
}

# Test Vim configuration
test_vim_config() {
    log "Testing Vim configuration..."
    
    # Test basic Vim startup
    if vim -c "echo 'Vim test successful'" -c q >/dev/null 2>&1; then
        success "Vim configuration test passed"
    else
        warn "Vim configuration test failed"
        return 1
    fi
    
    # Test plugin loading
    if vim -c "echo 'Plugins loaded: ' . len(globpath(&rtp, 'plugin/**/*.vim', 0, 1))" -c q 2>/dev/null | grep -q "Plugins loaded:"; then
        success "Vim plugins loaded successfully"
    else
        warn "Vim plugin loading test failed"
    fi
}

# Main installation function
main() {
    echo "====================================="
    echo "   Vim Package Installation"
    echo "====================================="
    echo ""
    
    # Install components
    install_vim
    create_vim_directories
    install_vim_plugins
    install_dev_tools
    
    # Backup existing configuration
    backup_existing_vimrc
    
    # Test configuration
    test_vim_config
    
    echo ""
    success "Vim package installation completed!"
    echo ""
    info "Next steps:"
    echo "  1. Use stow to deploy: stow --target=\$HOME vim"
    echo "  2. Open vim and run :helptags ALL to ensure help is available"
    echo "  3. Consider running 'vim +PlugInstall +qall' if using vim-plug"
    echo "  4. Customize ~/.vimrc.local for machine-specific settings"
    echo ""
    info "Installed plugins:"
    echo "  • vim-sensible - Better default settings"
    echo "  • vim-commentary - Easy commenting with gcc"
    echo "  • vim-surround - Surround text objects"
    echo ""
    info "Key mappings (see .vimrc for full list):"
    echo "  • ,w - Save file"
    echo "  • ,q - Quit"
    echo "  • ,/ - Clear search highlight"
    echo "  • ,n - Toggle line numbers"
    echo "  • ,ss - Strip trailing whitespace"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi