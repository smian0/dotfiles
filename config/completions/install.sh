#!/usr/bin/env bash
# Install shell completions for dotfiles scripts

set -euo pipefail

# Source OS detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/os-detect.sh"

# Completion directories
BASH_COMPLETION_DIR="/usr/local/etc/bash_completion.d"
ZSH_COMPLETION_DIR="/usr/local/share/zsh/site-functions"
USER_BASH_COMPLETION_DIR="$HOME/.local/share/bash-completion/completions"
USER_ZSH_COMPLETION_DIR="$HOME/.config/zsh/completions"

install_bash_completions() {
    log "Installing bash completions..."
    
    # Try system directory first, fall back to user directory
    local target_dir=""
    if [[ -w "$BASH_COMPLETION_DIR" ]]; then
        target_dir="$BASH_COMPLETION_DIR"
    else
        target_dir="$USER_BASH_COMPLETION_DIR"
        mkdir -p "$target_dir"
    fi
    
    # Install completion file
    if [[ -f "$SCRIPT_DIR/dotfiles.bash" ]]; then
        cp "$SCRIPT_DIR/dotfiles.bash" "$target_dir/dotfiles"
        success "Installed bash completions to $target_dir"
    else
        error "Bash completion file not found"
    fi
    
    # Add to bashrc if using user directory
    if [[ "$target_dir" == "$USER_BASH_COMPLETION_DIR" ]]; then
        local bashrc="$HOME/.bashrc"
        if [[ -f "$bashrc" ]]; then
            if ! grep -q "bash-completion/completions" "$bashrc"; then
                echo '' >> "$bashrc"
                echo '# Load user bash completions' >> "$bashrc"
                echo '[[ -d ~/.local/share/bash-completion/completions ]] && for f in ~/.local/share/bash-completion/completions/*; do source "$f"; done' >> "$bashrc"
                info "Added completion loading to .bashrc"
            fi
        fi
    fi
}

install_zsh_completions() {
    log "Installing zsh completions..."
    
    # Try system directory first, fall back to user directory
    local target_dir=""
    if [[ -w "$ZSH_COMPLETION_DIR" ]]; then
        target_dir="$ZSH_COMPLETION_DIR"
    else
        target_dir="$USER_ZSH_COMPLETION_DIR"
        mkdir -p "$target_dir"
    fi
    
    # Install completion file
    if [[ -f "$SCRIPT_DIR/dotfiles.zsh" ]]; then
        cp "$SCRIPT_DIR/dotfiles.zsh" "$target_dir/_dotfiles"
        success "Installed zsh completions to $target_dir"
    else
        error "Zsh completion file not found"
    fi
    
    # Add to zshrc if using user directory
    if [[ "$target_dir" == "$USER_ZSH_COMPLETION_DIR" ]]; then
        local zshrc="$HOME/.zshrc"
        if [[ -f "$zshrc" ]]; then
            if ! grep -q "fpath.*zsh/completions" "$zshrc"; then
                # Add before compinit
                local temp_file=$(mktemp)
                awk '
                    /^autoload -U compinit/ {
                        print "# Add user completions to fpath"
                        print "[[ -d ~/.config/zsh/completions ]] && fpath=(~/.config/zsh/completions $fpath)"
                        print ""
                    }
                    { print }
                ' "$zshrc" > "$temp_file"
                mv "$temp_file" "$zshrc"
                info "Added completion path to .zshrc"
            fi
        fi
    fi
}

show_usage() {
    cat << EOF
Shell completions installed! 

To use them:

Bash:
  - Restart your terminal or run: source ~/.bashrc
  - Try: ./install.sh <TAB><TAB>

Zsh:
  - Restart your terminal or run: source ~/.zshrc
  - Try: ./install.sh <TAB><TAB>

Available completions:
  - install.sh / install-master.sh
  - backup-restore.sh
  - profile-manager.sh
  - api-key-manager.sh
  - gpg-manager.sh
  - pass-manager.sh

EOF
}

main() {
    log "Installing shell completions for dotfiles scripts..."
    
    # Check if we have bash completion support
    if command -v bash &> /dev/null; then
        install_bash_completions
    else
        warn "Bash not found, skipping bash completions"
    fi
    
    # Check if we have zsh completion support
    if command -v zsh &> /dev/null; then
        install_zsh_completions
    else
        warn "Zsh not found, skipping zsh completions"
    fi
    
    success "Shell completions setup complete!"
    echo
    show_usage
}

main "$@"