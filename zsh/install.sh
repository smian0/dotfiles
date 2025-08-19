#!/usr/bin/env bash
# Zsh Package Installation Script
# Installs and configures Zsh with Oh My Zsh and Powerlevel10k

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

# Install Zsh if not present
install_zsh() {
    if command_exists zsh; then
        success "Zsh is already installed"
        return 0
    fi
    
    log "Installing Zsh..."
    
    case "$OS_TYPE" in
        macos)
            if command_exists brew; then
                brew install zsh
            else
                error "Homebrew required to install Zsh on macOS"
            fi
            ;;
        linux)
            if command_exists apt-get; then
                sudo apt-get update && sudo apt-get install -y zsh
            elif command_exists dnf; then
                sudo dnf install -y zsh
            elif command_exists pacman; then
                sudo pacman -S --noconfirm zsh
            else
                error "Unsupported package manager for Zsh installation"
            fi
            ;;
        *)
            error "Unsupported OS for automatic Zsh installation"
            ;;
    esac
    
    success "Zsh installed successfully"
}

# Install Oh My Zsh
install_oh_my_zsh() {
    local omz_dir="$HOME/.oh-my-zsh"
    
    if [[ -d "$omz_dir" ]]; then
        success "Oh My Zsh is already installed"
        return 0
    fi
    
    log "Installing Oh My Zsh..."
    
    # Download and install Oh My Zsh
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    
    success "Oh My Zsh installed successfully"
}

# Note: Powerlevel10k theme removed - using robbyrussell default theme

# Install Zsh plugins
install_zsh_plugins() {
    local custom_plugins_dir="$HOME/.oh-my-zsh/custom/plugins"
    
    # zsh-autosuggestions
    local autosuggestions_dir="$custom_plugins_dir/zsh-autosuggestions"
    if [[ ! -d "$autosuggestions_dir" ]]; then
        log "Installing zsh-autosuggestions..."
        git clone https://github.com/zsh-users/zsh-autosuggestions "$autosuggestions_dir"
        success "zsh-autosuggestions installed"
    else
        success "zsh-autosuggestions already installed"
    fi
    
    # zsh-syntax-highlighting
    local syntax_highlighting_dir="$custom_plugins_dir/zsh-syntax-highlighting"
    if [[ ! -d "$syntax_highlighting_dir" ]]; then
        log "Installing zsh-syntax-highlighting..."
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$syntax_highlighting_dir"
        success "zsh-syntax-highlighting installed"
    else
        success "zsh-syntax-highlighting already installed"
    fi
}

# Set Zsh as default shell
set_default_shell() {
    local zsh_path
    zsh_path=$(command -v zsh)
    
    if [[ "$SHELL" == "$zsh_path" ]]; then
        success "Zsh is already the default shell"
        return 0
    fi
    
    log "Setting Zsh as default shell..."
    
    # Add Zsh to /etc/shells if not present
    if ! grep -q "$zsh_path" /etc/shells; then
        echo "$zsh_path" | sudo tee -a /etc/shells
    fi
    
    # Change default shell
    chsh -s "$zsh_path"
    
    success "Zsh set as default shell (restart terminal to take effect)"
}

# Note: Font installation removed - no longer needed without Powerlevel10k

# Install AI tools dependencies
install_ai_dependencies() {
    log "Installing AI tools dependencies..."
    
    case "$OS_TYPE" in
        macos)
            if command_exists brew; then
                local tools=("jq" "curl")
                for tool in "${tools[@]}"; do
                    if ! command_exists "$tool"; then
                        log "Installing $tool for AI tools..."
                        brew install "$tool"
                        success "$tool installed"
                    else
                        success "$tool already available"
                    fi
                done
            fi
            ;;
        linux)
            if command_exists apt-get; then
                sudo apt-get install -y jq curl
            elif command_exists dnf; then
                sudo dnf install -y jq curl
            elif command_exists pacman; then
                sudo pacman -S --noconfirm jq curl
            fi
            success "AI dependencies installed"
            ;;
    esac
}

# Backup existing .zshrc
backup_existing_zshrc() {
    if [[ -f "$HOME/.zshrc" ]] && [[ ! -L "$HOME/.zshrc" ]]; then
        local backup_file="$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"
        log "Backing up existing .zshrc to $backup_file"
        cp "$HOME/.zshrc" "$backup_file"
        success "Existing .zshrc backed up"
    fi
}

# Main installation function
main() {
    echo "====================================="
    echo "   Zsh Package Installation"
    echo "====================================="
    echo ""
    
    # Install components
    install_zsh
    install_oh_my_zsh
    install_zsh_plugins
    install_ai_dependencies
    
    # Backup existing configuration
    backup_existing_zshrc
    
    # Set as default shell automatically if not already set
    if [[ "$SHELL" != "$(command -v zsh)" ]]; then
        echo ""
        echo "Setting Zsh as default shell automatically..."
        set_default_shell
    fi
    
    echo ""
    success "Zsh package installation completed!"
    echo ""
    info "Next steps:"
    echo "  1. Use stow to deploy: stow --target=\$HOME zsh"
    echo "  2. Restart your terminal"
    echo "  3. Run 'ai-setup' to configure AI assistants (Kimi & GLM)"
    echo "  4. Enjoy your enhanced shell with AI tools!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi