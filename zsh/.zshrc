# Zsh Configuration for Dotfiles Management
# Auto-managed by dotfiles system

# Zsh Configuration - Clean startup without theme prompts

# =============================================================================
# Environment Configuration
# =============================================================================

# XDG Base Directory Specification
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_CACHE_HOME="$HOME/.cache"

# Terminal Configuration
export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
export FORCE_COLOR=1
export TERM=xterm-256color

# History Configuration
export HISTSIZE=100000
export SAVEHIST=100000
export HISTFILE=~/.zsh_history

# Editor and pager
export EDITOR="vim"
export VISUAL="vim"
export PAGER="less"

# Language and locale
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# History configuration (using larger values from personal config)
export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=100000
export SAVEHIST=100000

# PATH Management
typeset -U path  # Keep unique entries in PATH

# Homebrew paths (macOS)
if [[ -d "/opt/homebrew/bin" ]]; then
    path=("/opt/homebrew/bin" "/opt/homebrew/sbin" $path)
fi

# Local bin directories
path=("$HOME/.local/bin" "$HOME/bin" $path)

# Dotfiles bin directory
if [[ -d "$HOME/dotfiles/bin" ]]; then
    path=("$HOME/dotfiles/bin" $path)
fi

# Development tools
if [[ -d "$HOME/.cargo/bin" ]]; then
    path=("$HOME/.cargo/bin" $path)
fi

if [[ -d "$HOME/go/bin" ]]; then
    path=("$HOME/go/bin" $path)
fi

# Node.js tools
if [[ -d "$HOME/.npm-global/bin" ]]; then
    path=("$HOME/.npm-global/bin" $path)
fi

# Bun
if [[ -d "$HOME/.bun/bin" ]]; then
    export BUN_INSTALL="$HOME/.bun"
    path=("$BUN_INSTALL/bin" $path)
fi

# Flutter
if [[ -d "$HOME/development/flutter/bin" ]]; then
    path=("$HOME/development/flutter/bin" $path)
fi

# LM Studio
if [[ -d "$HOME/.cache/lm-studio/bin" ]]; then
    path=("$HOME/.cache/lm-studio/bin" $path)
fi

# Windsurf
if [[ -d "/Users/smian/.codeium/windsurf/bin" ]]; then
    path=("/Users/smian/.codeium/windsurf/bin" $path)
fi

# PostgreSQL
if [[ -d "/opt/homebrew/opt/postgresql@16/bin" ]]; then
    path=("/opt/homebrew/opt/postgresql@16/bin" $path)
fi

# Ruby (Homebrew version)
if [[ -d "/opt/homebrew/opt/ruby/bin" ]]; then
    path=("/opt/homebrew/opt/ruby/bin" $path)
fi

# TCL/TK
if [[ -d "/opt/homebrew/opt/tcl-tk@8/bin" ]]; then
    path=("/opt/homebrew/opt/tcl-tk@8/bin" $path)
    export LDFLAGS="-L/opt/homebrew/opt/tcl-tk@8/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk@8/include"
    export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk@8/lib/pkgconfig"
fi

# Export the modified PATH
export PATH

# =============================================================================
# Zsh Options
# =============================================================================

# History options
setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicates first when trimming history
setopt HIST_IGNORE_DUPS          # Don't record duplicates in history
setopt HIST_IGNORE_ALL_DUPS      # Remove older duplicate entries from history
setopt HIST_FIND_NO_DUPS         # Don't display duplicates when searching
setopt HIST_IGNORE_SPACE         # Don't record commands starting with space
setopt HIST_SAVE_NO_DUPS         # Don't save duplicates to history file
setopt HIST_VERIFY               # Show command before executing from history
setopt SHARE_HISTORY             # Share history between sessions
setopt APPEND_HISTORY            # Append to history file
setopt INC_APPEND_HISTORY        # Add commands to history immediately

# Directory options
setopt AUTO_CD                   # Change directory without cd command
setopt AUTO_PUSHD                # Push old directory onto stack
setopt PUSHD_IGNORE_DUPS         # Don't push duplicates onto stack
setopt PUSHD_SILENT              # Don't print directory stack

# Completion options
setopt COMPLETE_IN_WORD          # Complete from both ends of word
setopt AUTO_MENU                 # Show completion menu on successive tab press
setopt AUTO_LIST                 # Automatically list choices on ambiguous completion
setopt AUTO_PARAM_SLASH          # Add trailing slash to directory names

# Globbing options
setopt EXTENDED_GLOB             # Enable extended globbing
setopt GLOB_DOTS                 # Include dotfiles in glob patterns

# Job control
setopt AUTO_RESUME               # Resume jobs on exact command match
setopt LONG_LIST_JOBS            # Show detailed job information

# Miscellaneous
setopt INTERACTIVE_COMMENTS      # Allow comments in interactive shell
setopt NO_BEEP                   # Disable beeping
setopt PROMPT_SUBST              # Enable prompt substitution

# =============================================================================
# Oh My Zsh Configuration
# =============================================================================

# Oh My Zsh installation path
export ZSH="$HOME/.oh-my-zsh"

# Theme configuration - with auto-install fallback
ZSH_THEME="robbyrussell"

# Theme management functions
_check_theme_health() {
    # Simple theme health check - just verify Oh My Zsh is working
    if [[ ! -f "$ZSH/oh-my-zsh.sh" ]]; then
        echo "⚠️  Oh My Zsh not found - theme functionality may be limited"
    fi
}

# Plugin configuration
plugins=(
    git
    brew
    macos
    zsh-autosuggestions
    zsh-syntax-highlighting
    docker
    kubectl
    node
    npm
    python
    rust
    golang
    pass
)

# Oh My Zsh settings
CASE_SENSITIVE="false"
HYPHEN_INSENSITIVE="true"
DISABLE_AUTO_UPDATE="false"
DISABLE_UPDATE_PROMPT="false"
export UPDATE_ZSH_DAYS=7
DISABLE_LS_COLORS="false"
DISABLE_AUTO_TITLE="false"
ENABLE_CORRECTION="false"
COMPLETION_WAITING_DOTS="true"
DISABLE_UNTRACKED_FILES_DIRTY="false"
HIST_STAMPS="yyyy-mm-dd"

# Auto-install Oh My Zsh and dependencies if missing
if [[ ! -f "$ZSH/oh-my-zsh.sh" ]]; then
    echo "🔧 Oh My Zsh not found. Auto-installing..."
    
    # Install Oh My Zsh
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    
    # Install required plugins
    local custom_plugins_dir="$ZSH/custom/plugins"
    
    # zsh-autosuggestions
    if [[ ! -d "$custom_plugins_dir/zsh-autosuggestions" ]]; then
        echo "📦 Installing zsh-autosuggestions..."
        git clone https://github.com/zsh-users/zsh-autosuggestions "$custom_plugins_dir/zsh-autosuggestions"
    fi
    
    # zsh-syntax-highlighting
    if [[ ! -d "$custom_plugins_dir/zsh-syntax-highlighting" ]]; then
        echo "📦 Installing zsh-syntax-highlighting..."
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$custom_plugins_dir/zsh-syntax-highlighting"
    fi
    
    echo "✅ Oh My Zsh and plugins installed successfully!"
    echo "💡 Restart your terminal for full functionality"
fi

# Load Oh My Zsh
if [[ -f "$ZSH/oh-my-zsh.sh" ]]; then
    source "$ZSH/oh-my-zsh.sh"
fi

# Run one-time setup checks
_run_setup_checks() {
    # Only run setup checks once per day to avoid spam
    local setup_check_file="$HOME/.cache/zsh-setup-check"
    local today=$(date +%Y-%m-%d)
    
    if [[ -f "$setup_check_file" ]]; then
        local last_check=$(cat "$setup_check_file" 2>/dev/null)
        if [[ "$last_check" == "$today" ]]; then
            return 0
        fi
    fi
    
    # Create cache directory if needed
    mkdir -p "$(dirname "$setup_check_file")"
    
    # Run checks
    _check_theme_health
    
    # Record that we ran checks today
    echo "$today" > "$setup_check_file"
}

# Run setup checks (only once per day)
_run_setup_checks

# =============================================================================
# Aliases
# =============================================================================

# Core command improvements
alias ls='ls -G'
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ~='cd ~'
alias -- -='cd -'

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
alias htop='htop'
alias df='df -h'
alias du='du -h'
alias free='vm_stat'

# Network utilities
alias ping='ping -c 5'
alias ports='netstat -tulanp'
alias myip='curl -s https://ipinfo.io/ip'
alias localip='ipconfig getifaddr en0'

# Package management (macOS)
if command -v brew >/dev/null 2>&1; then
    alias brewup='brew update && brew upgrade && brew cleanup'
    alias brewinfo='brew list --versions'
fi

# =============================================================================
# Pass Integration
# =============================================================================

# Pass aliases for convenience
alias pls='pass ls'
alias pshow='pass show'
alias pgen='pass generate'
alias pedit='pass edit'
alias pgit='pass git'

# Helper functions for common pass operations
function papi() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: papi <service>"
        echo "Available services:"
        pass ls api 2>/dev/null | grep -v "^api$" | sed 's/^[├└│─ ]*/  /'
        return 1
    fi
    pass show "api/$1" 2>/dev/null | head -1
}

function padd() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: padd <service>"
        return 1
    fi
    pass insert "api/$1"
}

function pcp() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: pcp <service>"
        return 1
    fi
    pass show -c "api/$1" 2>/dev/null
}

# =============================================================================
# AI Tools Integration
# =============================================================================

# Kimi and GLM AI assistants are provided by the bin/ scripts
# These should be available in PATH via: stow bin
# The scripts set appropriate environment variables and call Claude CLI

# Remove any old aliases that might interfere and set correct ones
unalias kimi glm 2>/dev/null || true

# Override any existing aliases with the correct dotfiles bin scripts
alias kimi='~/dotfiles/bin/kimi'
alias glm='~/dotfiles/bin/glm'

# AI assistant chooser function
function ai() {
    local service="$1"
    shift
    local prompt="$*"
    
    case "$service" in
        kimi|moonshot)
            kimi "$prompt"
            ;;
        glm|chatglm)
            glm "$prompt"
            ;;
        claude)
            if command_exists claude; then
                claude "$prompt"
            else
                echo "Claude CLI not available. Install Claude Code first."
                return 1
            fi
            ;;
        help|--help|-h)
            echo "AI Assistant Tool"
            echo "Usage: ai <service> [prompt]"
            echo ""
            echo "Available services:"
            echo "  kimi, moonshot   - Kimi AI (Moonshot)"
            echo "  glm, chatglm     - ChatGLM"
            echo "  claude           - Claude Code CLI"
            echo ""
            echo "Interactive mode (no prompt):"
            echo "  kimi             - Start Kimi interactive session"
            echo "  glm              - Start ChatGLM interactive session"
            echo "  ai kimi          - Start Kimi via ai wrapper"
            echo ""
            echo "One-shot examples:"
            echo "  ai kimi 'Explain git branches'"
            echo "  ai glm 'Write a Python script'"
            echo "  ai claude 'Review this code'"
            ;;
        *)
            echo "Unknown AI service: $service"
            echo "Run 'ai help' for available services"
            return 1
            ;;
    esac
}

# Quick AI aliases
alias ask='ai'
alias askimi='kimi'
alias askglm='glm'

# AI setup helper
function ai-setup() {
    echo "AI Tools Setup Assistant"
    echo "======================="
    echo ""
    echo "This will help you store API keys securely using pass."
    echo ""
    
    # Check if pass is available
    if ! command_exists pass; then
        echo "Error: pass (password store) not found"
        echo "Install it first or run the dotfiles master installer"
        return 1
    fi
    
    # Setup Kimi API key
    if ! pass show api/kimi >/dev/null 2>&1; then
        echo "🌙 Setting up Kimi AI (Moonshot):"
        echo "1. Visit: https://platform.moonshot.cn/"
        echo "2. Create account and get API key"
        echo "3. Enter your API key when prompted"
        echo ""
        echo -n "Do you want to store Kimi API key now? (y/n): "
        read -r response
        if [[ "$response" == "y" ]]; then
            pass insert api/kimi
        fi
    else
        echo "✓ Kimi API key already configured"
    fi
    
    echo ""
    
    # Setup GLM API key
    if ! pass show api/glm >/dev/null 2>&1; then
        echo "🤖 Setting up ChatGLM:"
        echo "1. Visit: https://open.bigmodel.cn/"
        echo "2. Create account and get API key"
        echo "3. Enter your API key when prompted"
        echo ""
        echo -n "Do you want to store GLM API key now? (y/n): "
        read -r response
        if [[ "$response" == "y" ]]; then
            pass insert api/glm
        fi
    else
        echo "✓ GLM API key already configured"
    fi
    
    echo ""
    echo "AI Tools Setup Complete!"
    echo ""
    echo "Test your setup:"
    echo "  kimi 'Hello, how are you?'"
    echo "  glm 'Write a hello world in Python'"
    echo "  ai help"
}

# AI status checker
function ai-status() {
    echo "AI Tools Status"
    echo "==============="
    echo ""
    
    # Check dependencies
    local deps_ok=true
    
    if command_exists curl; then
        echo "✓ curl: available"
    else
        echo "✗ curl: missing (required for API calls)"
        deps_ok=false
    fi
    
    if command_exists jq; then
        echo "✓ jq: available"
    else
        echo "✗ jq: missing (required for JSON parsing)"
        echo "  Install with: brew install jq"
        deps_ok=false
    fi
    
    if command_exists pass; then
        echo "✓ pass: available"
    else
        echo "✗ pass: missing (recommended for secure API key storage)"
        deps_ok=false
    fi
    
    echo ""
    
    # Check API keys
    echo "API Key Status:"
    
    if command_exists pass && pass show api/kimi >/dev/null 2>&1; then
        echo "✓ Kimi API key: configured in pass"
    elif [[ -n "$KIMI_API_KEY" ]]; then
        echo "✓ Kimi API key: configured in environment"
    else
        echo "✗ Kimi API key: not configured"
        echo "  Run 'ai-setup' to configure"
    fi
    
    if command_exists pass && pass show api/glm >/dev/null 2>&1; then
        echo "✓ GLM API key: configured in pass"
    elif [[ -n "$GLM_API_KEY" ]]; then
        echo "✓ GLM API key: configured in environment"
    else
        echo "✗ GLM API key: not configured"
        echo "  Run 'ai-setup' to configure"
    fi
    
    if command_exists claude; then
        echo "✓ Claude Code CLI: available"
    else
        echo "✗ Claude Code CLI: not installed"
    fi
    
    echo ""
    
    if [[ "$deps_ok" == true ]]; then
        echo "✅ All dependencies satisfied"
        echo "Run 'ai-setup' to configure API keys if needed"
    else
        echo "❌ Missing dependencies - install them first"
    fi
}

# =============================================================================
# Custom Functions
# =============================================================================

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Extract various archive formats
function extract() {
    if [[ -f "$1" ]]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"     ;;
            *.tar.gz)    tar xzf "$1"     ;;
            *.bz2)       bunzip2 "$1"     ;;
            *.rar)       unrar x "$1"     ;;
            *.gz)        gunzip "$1"      ;;
            *.tar)       tar xf "$1"      ;;
            *.tbz2)      tar xjf "$1"     ;;
            *.tgz)       tar xzf "$1"     ;;
            *.zip)       unzip "$1"       ;;
            *.Z)         uncompress "$1"  ;;
            *.7z)        7z x "$1"        ;;
            *)           echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Create directory and change to it
function mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Find files and directories
function ff() {
    find . -name "*$1*" -type f
}

function fd() {
    find . -name "*$1*" -type d
}

# Quick grep in files
function fif() {
    grep -r --include="*.$2" "$1" .
}

# Git shortcuts
function gac() {
    git add . && git commit -m "$1"
}

function gacp() {
    git add . && git commit -m "$1" && git push
}

# Docker shortcuts
function drun() {
    docker run -it --rm "$@"
}

function dexec() {
    docker exec -it "$1" bash
}

# System info
function sysinfo() {
    echo "System Information:"
    echo "=================="
    echo "OS: $(uname -s)"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    if command -v sw_vers >/dev/null 2>&1; then
        echo "macOS Version: $(sw_vers -productVersion)"
    fi
    echo "Shell: $SHELL"
    echo "Terminal: $TERM"
    echo "User: $USER"
    echo "Home: $HOME"
    echo "Working Directory: $PWD"
    echo "Date: $(date)"
    echo "Uptime: $(uptime)"
}

# Network info
function netinfo() {
    echo "Network Information:"
    echo "==================="
    echo "Local IP: $(ipconfig getifaddr en0 2>/dev/null || echo 'Not connected')"
    echo "Public IP: $(curl -s https://ipinfo.io/ip 2>/dev/null || echo 'Not available')"
    echo "WiFi Network: $(networksetup -getairportnetwork en0 2>/dev/null | cut -d: -f2 | xargs)"
}

# =============================================================================
# Dotfiles Management
# =============================================================================

# Dotfiles aliases
alias dotfiles='cd ~/dotfiles'
alias dots='dotfiles'
alias dotstow='cd ~/dotfiles && stow --target=$HOME'
alias dotunstow='cd ~/dotfiles && stow --delete --target=$HOME'

# Quick dotfiles management functions
function dotadd() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: dotadd <package>"
        echo "Available packages:"
        ls ~/dotfiles/
        return 1
    fi
    cd ~/dotfiles && stow --target=$HOME "$1"
}

function dotremove() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: dotremove <package>"
        return 1
    fi
    cd ~/dotfiles && stow --delete --target=$HOME "$1"
}

function dotstatus() {
    echo "Dotfiles Status:"
    echo "==============="
    cd ~/dotfiles
    
    echo "Available packages:"
    ls -1 | grep -v README.md | while read -r package; do
        if [[ -d "$package" ]]; then
            # Check if package is stowed by looking for symlinks
            local stowed=false
            find "$HOME" -maxdepth 2 -type l 2>/dev/null | while read -r link; do
                if [[ "$(readlink "$link")" == *"$PWD/$package"* ]]; then
                    stowed=true
                    break
                fi
            done
            
            if $stowed; then
                echo "  ✓ $package (stowed)"
            else
                echo "  ○ $package (not stowed)"
            fi
        fi
    done
}

# =============================================================================
# Development Environment
# =============================================================================

# Node.js configuration
if command -v node >/dev/null 2>&1; then
    export NPM_CONFIG_PREFIX="$HOME/.npm-global"
fi

# Python configuration
if command -v python3 >/dev/null 2>&1; then
    alias python='python3'
    alias pip='pip3'
fi

# Go configuration
if command -v go >/dev/null 2>&1; then
    export GOPATH="$HOME/go"
    export GOBIN="$GOPATH/bin"
fi

# Claude Code aliases
alias cl="/Users/smian/.nvm/versions/node/v20.19.1/bin/claude"
alias cld="cl --dangerously-skip-permissions"
alias cldr="cl --dangerously-skip-permissions --resume"

# Force override AI tool aliases to use dotfiles bin scripts
alias kimi='~/dotfiles/bin/kimi'
alias glm='~/dotfiles/bin/glm'

# Use faster alternatives when available
if command -v rg &> /dev/null; then
    alias grep='rg'
fi
if command -v fd &> /dev/null; then
    alias find='fd'
fi

# History management
alias savehist='save_history'

# Custom functions
save_history() {
    fc -W
    echo "History saved to $HISTFILE"
}

# Rust configuration
if [[ -f "$HOME/.cargo/env" ]]; then
    source "$HOME/.cargo/env"
fi

# NVM (Node Version Manager)
export NVM_DIR="$HOME/.nvm"
# Temporarily unset NPM_CONFIG_PREFIX for NVM compatibility
if [[ -n "$NPM_CONFIG_PREFIX" ]]; then
    export NPM_CONFIG_PREFIX_BACKUP="$NPM_CONFIG_PREFIX"
    unset NPM_CONFIG_PREFIX
fi
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && . "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"
# Restore NPM_CONFIG_PREFIX after NVM loads
if [[ -n "$NPM_CONFIG_PREFIX_BACKUP" ]]; then
    export NPM_CONFIG_PREFIX="$NPM_CONFIG_PREFIX_BACKUP"
    unset NPM_CONFIG_PREFIX_BACKUP
fi

# Memory Bank
export MEMORY_BANK_ROOT=/Users/smian/memory-bank

# =============================================================================
# Completion Configuration
# =============================================================================

# Enable completion for custom functions
if [[ -d "/opt/homebrew/share/zsh/site-functions" ]]; then
    fpath=("/opt/homebrew/share/zsh/site-functions" $fpath)
fi

# Docker completion
if command -v docker >/dev/null 2>&1; then
    complete -o default -F __docker_complete docker
fi

# Git completion
if [[ -f "/opt/homebrew/etc/bash_completion.d/git-completion.bash" ]]; then
    source "/opt/homebrew/etc/bash_completion.d/git-completion.bash"
fi

# =============================================================================
# Security and Privacy
# =============================================================================

# GPG configuration
export GPG_TTY=$(tty)

# SSH configuration
if [[ -d "$HOME/.ssh" ]]; then
    # Start ssh-agent if not running
    if ! pgrep -u "$USER" ssh-agent > /dev/null; then
        ssh-agent > "$HOME/.ssh/ssh-agent-thing"
    fi
    if [[ "$SSH_AGENT_PID" == "" ]] && [[ -f "$HOME/.ssh/ssh-agent-thing" ]]; then
        eval "$(<$HOME/.ssh/ssh-agent-thing)" > /dev/null
    fi
fi

# =============================================================================
# Load Local Configuration
# =============================================================================

# Load machine-specific configuration if it exists
if [[ -f "$HOME/.zshrc.local" ]]; then
    source "$HOME/.zshrc.local"
fi

# Load work-specific configuration if it exists
if [[ -f "$HOME/.zshrc.work" ]]; then
    source "$HOME/.zshrc.work"
fi

# =============================================================================
# Welcome Message
# =============================================================================

function dotfiles_welcome() {
    if [[ -t 0 && -t 1 && -t 2 ]]; then  # Only show in interactive terminals
        echo ""
        echo "🏠 Dotfiles Environment Ready"
        echo "   Type 'dotstatus' to see package status"
        echo "   Type 'pls' to see stored passwords"
        echo "   Type 'ai-status' to check AI tools"
        echo "   Type 'ai-setup' to configure AI assistants"
        echo "   Type 'sysinfo' for system information"
        echo ""
        echo "🤖 AI Tools Available:"
        echo "   kimi                    - Kimi AI assistant (interactive)"
        echo "   glm                     - ChatGLM assistant (interactive)"
        echo "   kimi 'your question'    - One-shot Kimi query"
        echo "   glm 'your question'     - One-shot ChatGLM query"
        echo "   ai help                 - Show all AI options"
        echo ""
    fi
}

# Show welcome message on first load
if [[ -z "$DOTFILES_WELCOME_SHOWN" ]]; then
    export DOTFILES_WELCOME_SHOWN=1
    dotfiles_welcome
fi

# =============================================================================
