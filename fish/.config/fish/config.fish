# Fish Configuration for Dotfiles Management
# Auto-managed by dotfiles system

# =============================================================================
# Environment Configuration
# =============================================================================

# XDG Base Directory Specification
set -gx XDG_CONFIG_HOME "$HOME/.config"
set -gx XDG_DATA_HOME "$HOME/.local/share"
set -gx XDG_STATE_HOME "$HOME/.local/state"
set -gx XDG_CACHE_HOME "$HOME/.cache"

# Terminal Configuration
set -gx CLICOLOR 1
set -gx LSCOLORS ExFxBxDxCxegedabagacad
set -gx FORCE_COLOR 1
set -gx TERM xterm-256color

# Editor and pager
set -gx EDITOR vim
set -gx VISUAL vim
set -gx PAGER less

# Language and locale
set -gx LANG en_US.UTF-8
set -gx LC_ALL en_US.UTF-8

# Browser forwarding configuration for VS Code Remote SSH
set -gx BROWSER open
set -gx DISPLAY :0
set -gx XAUTHORITY "$HOME/.Xauthority"
set -gx BROWSER_FORWARDING_ENABLED 1

# Claude Code OAuth Token (for SSH sessions only)
if set -q SSH_CLIENT; or set -q SSH_TTY; or set -q SSH_CONNECTION
    set -gx CLAUDE_CODE_OAUTH_TOKEN "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"
end

# =============================================================================
# PATH Management
# =============================================================================

# Fish has better PATH management with fish_add_path
# Paths are added in reverse priority order (last added = highest priority)

# Homebrew paths (macOS)
if test -d /opt/homebrew/bin
    fish_add_path /opt/homebrew/bin
    fish_add_path /opt/homebrew/sbin
end

# Local bin directories
fish_add_path $HOME/.local/bin
fish_add_path $HOME/bin

# Dotfiles bin directory
if test -d $HOME/dotfiles/bin
    fish_add_path $HOME/dotfiles/bin
end

# Development tools
if test -d $HOME/.cargo/bin
    fish_add_path $HOME/.cargo/bin
end

if test -d $HOME/go/bin
    fish_add_path $HOME/go/bin
end

# Node.js tools
if test -d $HOME/.npm-global/bin
    fish_add_path $HOME/.npm-global/bin
end

# Bun
if test -d $HOME/.bun/bin
    set -gx BUN_INSTALL "$HOME/.bun"
    fish_add_path $BUN_INSTALL/bin
end

# Flutter
if test -d $HOME/development/flutter/bin
    fish_add_path $HOME/development/flutter/bin
end

# LM Studio
if test -d $HOME/.cache/lm-studio/bin
    fish_add_path $HOME/.cache/lm-studio/bin
end

# Windsurf
if test -d /Users/smian/.codeium/windsurf/bin
    fish_add_path /Users/smian/.codeium/windsurf/bin
end

# PostgreSQL
if test -d /opt/homebrew/opt/postgresql@16/bin
    fish_add_path /opt/homebrew/opt/postgresql@16/bin
end

# Ruby (Homebrew version)
if test -d /opt/homebrew/opt/ruby/bin
    fish_add_path /opt/homebrew/opt/ruby/bin
end

# TCL/TK
if test -d /opt/homebrew/opt/tcl-tk@8/bin
    fish_add_path /opt/homebrew/opt/tcl-tk@8/bin
    set -gx LDFLAGS "-L/opt/homebrew/opt/tcl-tk@8/lib"
    set -gx CPPFLAGS "-I/opt/homebrew/opt/tcl-tk@8/include"
    set -gx PKG_CONFIG_PATH "/opt/homebrew/opt/tcl-tk@8/lib/pkgconfig"
end

# =============================================================================
# Aliases
# =============================================================================

# Core command improvements
alias ls='ls -G'
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Grep with color support
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Python development tools
alias pyt='pytest'

# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
# Note: ~ already works natively in fish, no alias needed

# Git shortcuts
alias g='git'
alias ga='git add'
alias gc='git commit'
alias gco='git checkout'
alias gst='git status'
alias gd='git diff'
alias gl='git log --oneline --graph --decorate'
alias gp='git push'
alias gpl='git pull'

# Docker shortcuts
alias d='docker'
alias dc='docker-compose'
alias dps='docker ps'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'

# System monitoring
alias top='top -o cpu'
alias df='df -h'
alias du='du -h'
alias free='vm_stat'

# Network utilities
alias ping='ping -c 5'
alias myip='curl -s https://ipinfo.io/ip'
alias localip='ipconfig getifaddr en0'

# Package management (macOS)
if command -v brew >/dev/null 2>&1
    alias brewup='brew update && brew upgrade && brew cleanup'
    alias brewinfo='brew list --versions'
end

# Pass Integration
alias pls='pass ls'
alias pshow='pass show'
alias pgen='pass generate'
alias pedit='pass edit'
alias pgit='pass git'

# Environment debugging aliases
alias envdebug='env-debug'
alias envsync='env-sync'
alias envcheck='env-check'

# Dotfiles aliases
alias dotfiles='cd ~/dotfiles'
alias dots='dotfiles'

# Python configuration
if command -v python3 >/dev/null 2>&1
    alias python='python3'
    alias py='python3'
    alias pip='pip3'
end

# Chrome Keeper Management Aliases
alias chrome-status="/Users/smian/chrome_commands.sh status"
alias chrome-start="/Users/smian/chrome_commands.sh start"
alias chrome-stop="/Users/smian/chrome_commands.sh stop"
alias chrome-logs="/Users/smian/chrome_commands.sh logs"

# =============================================================================
# Development Environment
# =============================================================================

# Node.js configuration
if command -v node >/dev/null 2>&1
    set -gx NPM_CONFIG_PREFIX "$HOME/.npm-global"
end

# Pyenv configuration
if command -v pyenv >/dev/null 2>&1
    set -gx PYENV_ROOT "$HOME/.pyenv"
    if test -d $PYENV_ROOT/bin
        fish_add_path $PYENV_ROOT/bin
    end
    pyenv init - | source
end

# Go configuration
if command -v go >/dev/null 2>&1
    set -gx GOPATH "$HOME/go"
    set -gx GOBIN "$GOPATH/bin"
end

# Rust configuration
# Note: Cargo bin is already added to PATH above, no need to source .cargo/env
# Fish uses fish_add_path instead of modifying PATH in shell scripts

# NVM (Node Version Manager)
set -gx NVM_DIR "$HOME/.nvm"

# Memory Bank
set -gx MEMORY_BANK_ROOT /Users/smian/memory-bank

# GPG configuration
set -gx GPG_TTY (tty)

# =============================================================================
# Load Additional Configuration
# =============================================================================

# Source LLM tools configuration (will be converted to fish)
if test -f $HOME/.config/fish/conf.d/llm-tools.fish
    source $HOME/.config/fish/conf.d/llm-tools.fish
end

# Source AGENTS.md support (will be converted to fish)
if test -f $HOME/.config/fish/conf.d/agents-md.fish
    source $HOME/.config/fish/conf.d/agents-md.fish
end

# Source MCP configuration management (will be converted to fish)
if test -f $HOME/.config/fish/conf.d/mcp-config.fish
    source $HOME/.config/fish/conf.d/mcp-config.fish
end

# Load machine-specific configuration if it exists
if test -f $HOME/.config/fish/config.local.fish
    source $HOME/.config/fish/config.local.fish
end

# Load work-specific configuration if it exists
if test -f $HOME/.config/fish/config.work.fish
    source $HOME/.config/fish/config.work.fish
end

# Auto-added by MCP Environment Setup
if test -f /Users/smian/.config/mcp-env/shell-env.sh
    # Fish doesn't use bash-style sourcing for env vars, but we can extract them
    # This will be handled by a fish function
end

set -gx NODE_OPTIONS "--max-old-space-size=8192"

# =============================================================================
# Welcome Message
# =============================================================================

function fish_greeting
    echo ""
    echo "🐟 Fish Shell Environment Ready"
    echo "   Type 'help' for fish-specific help"
    echo "   Type 'dotstatus' to see package status"
    echo ""
    echo "🤖 AI Tools Available:"
    echo "   kimi                    - Kimi AI assistant (interactive)"
    echo "   glm                     - ChatGLM assistant (interactive)"
    echo "   deep                    - DeepSeek AI assistant (interactive)"
    echo "   claude 'your question'  - One-shot Claude query"
    echo ""
    echo "🔧 MCP Configuration Tools:"
    echo "   mcpls                   - List available MCP servers"
    echo "   mcps                    - Quick MCP setup (global servers)"
    echo "   mcpm                    - Interactive MCP extraction menu"
    echo "   mcp-status              - Show MCP configuration status"
    echo ""
    echo "🔍 Environment Debugging:"
    echo "   envcheck                - Compare system vs shell environment"
    echo "   envdebug                - Full environment diagnostic"
    echo "   envsync                 - Sync shell to system values"
    echo ""
end
