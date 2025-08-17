#!/usr/bin/env bash
# direnv installation and setup script

set -euo pipefail

# Source OS detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/os-detect.sh"

# Configuration
DIRENV_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/direnv"

install_direnv() {
    log "Installing direnv..."
    
    if command -v direnv &> /dev/null; then
        success "direnv is already installed"
        return 0
    fi
    
    if [[ "$OS" == "macos" ]]; then
        brew install direnv
    elif [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "linux" ]]; then
        sudo apt-get update
        sudo apt-get install -y direnv
    else
        error "Unsupported OS for direnv installation"
    fi
    
    success "direnv installed successfully"
}

setup_direnv() {
    log "Setting up direnv configuration..."
    
    # Create config directory
    mkdir -p "$DIRENV_CONFIG_DIR"
    
    # Link global direnvrc
    if [[ -f "$SCRIPT_DIR/.direnvrc" ]]; then
        ln -sf "$SCRIPT_DIR/.direnvrc" "$DIRENV_CONFIG_DIR/direnvrc"
        success "Linked global direnvrc"
    fi
    
    # Copy example .envrc to config dir for reference
    if [[ -f "$SCRIPT_DIR/.envrc.example" ]]; then
        cp "$SCRIPT_DIR/.envrc.example" "$DIRENV_CONFIG_DIR/envrc.example"
        success "Copied example .envrc for reference"
    fi
    
    # Add direnv hook to shells
    setup_shell_hooks
}

setup_shell_hooks() {
    log "Setting up shell hooks..."
    
    # Zsh
    if [[ -f "$HOME/.zshrc" ]]; then
        if ! grep -q 'eval "$(direnv hook zsh)"' "$HOME/.zshrc"; then
            echo '' >> "$HOME/.zshrc"
            echo '# direnv hook' >> "$HOME/.zshrc"
            echo 'eval "$(direnv hook zsh)"' >> "$HOME/.zshrc"
            success "Added direnv hook to .zshrc"
        else
            info "direnv hook already in .zshrc"
        fi
    fi
    
    # Bash
    if [[ -f "$HOME/.bashrc" ]]; then
        if ! grep -q 'eval "$(direnv hook bash)"' "$HOME/.bashrc"; then
            echo '' >> "$HOME/.bashrc"
            echo '# direnv hook' >> "$HOME/.bashrc"
            echo 'eval "$(direnv hook bash)"' >> "$HOME/.bashrc"
            success "Added direnv hook to .bashrc"
        else
            info "direnv hook already in .bashrc"
        fi
    fi
    
    # Fish
    if [[ -d "$HOME/.config/fish" ]]; then
        local fish_config="$HOME/.config/fish/config.fish"
        if [[ -f "$fish_config" ]]; then
            if ! grep -q 'direnv hook fish | source' "$fish_config"; then
                echo '' >> "$fish_config"
                echo '# direnv hook' >> "$fish_config"
                echo 'direnv hook fish | source' >> "$fish_config"
                success "Added direnv hook to fish config"
            else
                info "direnv hook already in fish config"
            fi
        fi
    fi
}

show_usage() {
    cat << EOF
direnv has been set up! Here's how to use it:

1. Create an .envrc file in your project directory:
   echo 'export MY_VAR="value"' > .envrc

2. Allow direnv to load the file:
   direnv allow

3. Example .envrc templates are available at:
   $DIRENV_CONFIG_DIR/envrc.example

4. Global direnv functions are configured at:
   $DIRENV_CONFIG_DIR/direnvrc

For more information: https://direnv.net/
EOF
}

main() {
    log "Setting up direnv..."
    
    install_direnv
    setup_direnv
    
    success "direnv setup complete!"
    echo
    show_usage
}

main "$@"