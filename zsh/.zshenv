# .zshenv - Environment variables for all zsh shells
# This file is sourced for ALL zsh shells (interactive, non-interactive, login, SSH)
# Perfect for PATH and other environment variables that should always be available

# Homebrew PATH (Apple Silicon and Intel)
# CRITICAL: This ensures homebrew binaries are available in SSH sessions
# Required for tools like mosh-server to work over SSH
if [[ -d "/opt/homebrew/bin" ]]; then
    # Apple Silicon (M1/M2/M3)
    export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
elif [[ -d "/usr/local/bin" ]]; then
    # Intel Macs
    export PATH="/usr/local/bin:/usr/local/sbin:$PATH"
fi

# Local bin directory
if [[ -d "$HOME/.local/bin" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# User-specific exports (add your own here)
# export EDITOR=vim
# export VISUAL=vim
