# .zshenv - Environment variables for all zsh shells
# This file is sourced for ALL zsh shells (interactive, non-interactive, login, SSH)
# Perfect for PATH and other environment variables that should always be available

# PATH deduplication helper
# Prevents duplicate entries when .zshenv is sourced multiple times
add_to_path() {
    if [[ -d "$1" ]] && [[ ":$PATH:" != *":$1:"* ]]; then
        export PATH="$1:$PATH"
    fi
}

# Homebrew PATH (Apple Silicon and Intel)
# CRITICAL: This ensures homebrew binaries are available in SSH sessions
# Required for tools like mosh-server to work over SSH
if [[ -d "/opt/homebrew/bin" ]]; then
    # Apple Silicon (M1/M2/M3)
    add_to_path "/opt/homebrew/bin"
    add_to_path "/opt/homebrew/sbin"
elif [[ -d "/usr/local/bin" ]]; then
    # Intel Macs
    add_to_path "/usr/local/bin"
    add_to_path "/usr/local/sbin"
fi

# Local bin directory
add_to_path "$HOME/.local/bin"

# NPM global bin directory (for trash-cli and other global npm packages)
add_to_path "$HOME/.npm-global/bin"

# User-specific exports (add your own here)
# export EDITOR=vim
# export VISUAL=vim

# Safe deletion protection with trash-cli
# Only configure if trash-cli is actually installed
if [[ -x "$HOME/.npm-global/bin/trash" ]]; then
    # Trash configuration flag
    # Signals that rm is aliased to trash (using trash-cli)
    # Used by pre-tool-use hooks to enforce safe deletion
    export TRASH_CONFIGURED=1

    # Safe deletion: Always use trash-cli instead of rm
    # trash-cli accepts all rm flags (but ignores them) for compatibility
    # This works in ALL shells (interactive and non-interactive)
    # Use absolute path to ensure trash-cli is used (not native /usr/bin/trash)
    alias rm="$HOME/.npm-global/bin/trash"
else
    # Fallback: trash-cli not installed
    # Print warning once per session (use a flag to prevent spam)
    if [[ -z "$_TRASH_WARNING_SHOWN" ]]; then
        echo "⚠️  trash-cli not found. Install with: npm install -g trash-cli" >&2
        echo "   Until then, rm will work normally (permanent deletion)" >&2
        export _TRASH_WARNING_SHOWN=1
    fi
    # Don't set TRASH_CONFIGURED, allowing hook to warn appropriately
fi

# Cargo (Rust) environment
# This is typically added by rustup installation
[[ -f "$HOME/.cargo/env" ]] && . "$HOME/.cargo/env"
