# Zsh Configuration for Dotfiles Management
# Auto-managed by dotfiles system

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

# Browser forwarding configuration for VS Code Remote SSH
export BROWSER="open"
export DISPLAY=":0"
export XAUTHORITY="$HOME/.Xauthority"

# Ensure browser opens in local environment
export BROWSER_FORWARDING_ENABLED=1

# Claude Code OAuth Token (for SSH sessions only)
if [[ -n "$SSH_CLIENT" || -n "$SSH_TTY" || -n "$SSH_CONNECTION" ]]; then
    export CLAUDE_CODE_OAUTH_TOKEN="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"
fi

# =============================================================================
# SSH Agent Configuration
# =============================================================================

# Start SSH agent if not running
if [[ -z "$SSH_AUTH_SOCK" ]]; then
    eval "$(ssh-agent -s)" > /dev/null 2>&1
fi

# Add GitHub SSH key automatically
if [[ -f "$HOME/.ssh/id_ed25519_github_smian0" ]]; then
    ssh-add -l | grep -q "id_ed25519_github_smian0" || ssh-add "$HOME/.ssh/id_ed25519_github_smian0" > /dev/null 2>&1
fi



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

# Standard grep with color support
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

# Environment debugging aliases
alias envdebug='env-debug'
alias envsync='env-sync'
alias envcheck='env-check'

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

# Source LLM tools configuration
if [[ -f "$HOME/dotfiles/zsh/llm-tools.zsh" ]]; then
    source "$HOME/dotfiles/zsh/llm-tools.zsh"
fi

# =============================================================================
# Custom Functions
# =============================================================================

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Environment debugging and synchronization
function env-debug() {
    if [[ -x "$HOME/dotfiles/scripts/env-debug.sh" ]]; then
        "$HOME/dotfiles/scripts/env-debug.sh"
    else
        echo "env-debug.sh not found or not executable"
    fi
}

function env-sync() {
    echo "🔄 Syncing shell environment with system (launchctl)..."
    local synced=0
    
    # Key environment variables to sync
    local vars=("GITHUB_TOKEN" "OPENAI_API_KEY" "ANTHROPIC_API_KEY" "BRAVE_API_KEY" "OLLAMA_API_KEY" "DEEPSEEK_API_KEY" "GLM_API_KEY" "KIMI_API_KEY")
    
    for var in "${vars[@]}"; do
        local system_val=$(launchctl getenv "$var" 2>/dev/null || echo "")
        local shell_val=$(printenv "$var" 2>/dev/null || echo "")
        
        if [[ -n "$system_val" && "$system_val" != "$shell_val" ]]; then
            export "$var"="$system_val"
            echo "✓ Synced $var"
            ((synced++))
        fi
    done
    
    if [[ $synced -eq 0 ]]; then
        echo "✅ No sync needed - all variables match"
    else
        echo "✅ Synced $synced environment variables"
    fi
}

function env-check() {
    local var="${1:-GITHUB_TOKEN}"
    echo "System (launchctl): $(launchctl getenv "$var" 2>/dev/null | head -c 20)..."
    echo "Shell (current):    $(printenv "$var" 2>/dev/null | head -c 20)..."
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
    command find . -name "*$1*" -type f
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
            while read -r link; do
                if [[ "$(readlink "$link" 2>/dev/null)" == *"$PWD/$package"* ]]; then
                    stowed=true
                    break
                fi
            done < <(find "$HOME" -maxdepth 2 -type l 2>/dev/null)
            
            if [[ "$stowed" == "true" ]]; then
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

# Pyenv configuration
if command -v pyenv >/dev/null 2>&1; then
    export PYENV_ROOT="$HOME/.pyenv"
    [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init - zsh)"
fi

# Python configuration
if command -v python3 >/dev/null 2>&1; then
    alias python='python3'
    alias py='python3'
    alias pip='pip3'
fi

# Go configuration
if command -v go >/dev/null 2>&1; then
    export GOPATH="$HOME/go"
    export GOBIN="$GOPATH/bin"
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

# Add Homebrew completions to fpath before loading compinit
if [[ -d "/opt/homebrew/share/zsh/site-functions" ]]; then
    fpath=("/opt/homebrew/share/zsh/site-functions" $fpath)
fi

# Add custom completions directory
if [[ -d "$HOME/.zsh/completions" ]]; then
    fpath=("$HOME/.zsh/completions" $fpath)
fi

# Initialize Zsh completion system
autoload -Uz compinit
# Only regenerate dump once a day for faster startup
if [[ -n "$HOME/.zcompdump" ]]; then
    if [[ ! -f "$HOME/.zcompdump" || "$HOME/.zcompdump" -ot /usr/share/zsh ]]; then
        compinit
    else
        compinit -C
    fi
else
    compinit
fi

# Enable bash completion compatibility mode
autoload -Uz bashcompinit
bashcompinit

# Completion styling
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%B%F{yellow}--- %d ---%f%b'
zstyle ':completion:*:warnings' format '%B%F{red}No matches for: %d%f%b'
zstyle ':completion:*:messages' format '%B%F{purple} -- %d --%f%b'
zstyle ':completion:*:corrections' format '%B%F{green}!- %d (errors: %e) -!%f%b'
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$HOME/.zsh/cache"
zstyle ':completion:*' completer _complete _match _approximate
zstyle ':completion:*:match:*' original only
zstyle ':completion:*:approximate:*' max-errors 1 numeric
zstyle ':completion:*:functions' ignored-patterns '_*'
zstyle ':completion:*:*:kill:*' menu yes select
zstyle ':completion:*:kill:*' force-list always

# Faster completion for directories
zstyle ':completion:*' accept-exact-dirs true
zstyle ':completion:*' path-completion true

# Better SSH/SCP/rsync completions
zstyle ':completion:*:(ssh|scp|rsync):*' tag-order 'hosts:-host:host hosts:-domain:domain hosts:-ipaddr:ip\ address *'
zstyle ':completion:*:(scp|rsync):*' group-order users files all-files hosts-domain hosts-host hosts-ipaddr
zstyle ':completion:*:ssh:*' group-order users hosts-domain hosts-host users hosts-ipaddr
zstyle ':completion:*:(ssh|scp|rsync):*:hosts-host' ignored-patterns '*(.|:)*' loopback ip6-loopback localhost ip6-localhost broadcasthost
zstyle ':completion:*:(ssh|scp|rsync):*:hosts-domain' ignored-patterns '<->.<->.<->.<->' '^[-[:alnum:]]##(.[-[:alnum:]]##)##' '*@*'
zstyle ':completion:*:(ssh|scp|rsync):*:hosts-ipaddr' ignored-patterns '^(<->.<->.<->.<->|(|::)([[:xdigit:].]##:(#c,2))##(|%*))' '127.0.0.<->' '255.255.255.255' '::1' 'fe80::*'

# Docker completion
if command -v docker >/dev/null 2>&1; then
    # Try to load Docker's native completion if available
    if [[ -f "/opt/homebrew/share/zsh/site-functions/_docker" ]]; then
        # Docker completion should be loaded automatically via fpath
        :
    elif command -v docker-compose >/dev/null 2>&1; then
        # Try loading docker-compose completion
        if [[ -f "/opt/homebrew/share/zsh/site-functions/_docker-compose" ]]; then
            :
        fi
    fi
fi

# Git completion (native Zsh version is better than bash version)
# Git completion should be automatically loaded from fpath

# Additional completions for common tools
# Kubectl
if command -v kubectl >/dev/null 2>&1; then
    source <(kubectl completion zsh 2>/dev/null) || true
fi

# Helm
if command -v helm >/dev/null 2>&1; then
    source <(helm completion zsh 2>/dev/null) || true
fi

# npm completion
if command -v npm >/dev/null 2>&1; then
    source <(npm completion 2>/dev/null) || true
fi

# pip completion
if command -v pip >/dev/null 2>&1; then
    source <(pip completion --zsh 2>/dev/null) || true
fi

# AWS CLI completion
if [[ -f "/opt/homebrew/share/zsh/site-functions/aws_zsh_completer.sh" ]]; then
    source "/opt/homebrew/share/zsh/site-functions/aws_zsh_completer.sh"
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
# AI Agent Configuration Support
# =============================================================================
# Source AGENTS.md configuration for AI agent standardization
if [[ -f "$HOME/dotfiles/zsh/agents-md.zsh" ]]; then
    source "$HOME/dotfiles/zsh/agents-md.zsh"
fi

# Source MCP configuration management
if [[ -f "$HOME/dotfiles/zsh/mcp-config.zsh" ]]; then
    source "$HOME/dotfiles/zsh/mcp-config.zsh"
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
        echo "   Type 'sysinfo' for system information"
        echo ""
        echo "🤖 AI Tools Available:"
        echo "   kimi                    - Kimi AI assistant (interactive)"
        echo "   glm                     - ChatGLM assistant (interactive)"
        echo "   deep                    - DeepSeek AI assistant (interactive)"
        echo "   kimi 'your question'    - One-shot Kimi query"
        echo "   glm 'your question'     - One-shot ChatGLM query"
        echo "   deep 'your question'    - One-shot DeepSeek query"
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
    fi
}

# Show welcome message on first load
if [[ -z "$DOTFILES_WELCOME_SHOWN" ]]; then
    export DOTFILES_WELCOME_SHOWN=1
    dotfiles_welcome
fi

# =============================================================================

# Chrome Keeper Management Aliases
alias chrome-status="/Users/smian/chrome_commands.sh status"
alias chrome-start="/Users/smian/chrome_commands.sh start"
alias chrome-stop="/Users/smian/chrome_commands.sh stop"
alias chrome-logs="/Users/smian/chrome_commands.sh logs"

# =============================================================================

# Added by LM Studio CLI (lms)
export PATH="$PATH:/Users/smian/.cache/lm-studio/bin"
# End of LM Studio CLI section


# # Claude Code Router configuration
# export ANTHROPIC_BASE_URL="http://127.0.0.1:8080"

# =============================================================================
# OpenCode Agent Transformation Support
# =============================================================================
# Shell function to wrap opencode with agent transformation
opencode() {
    # Run our wrapper which handles transformation and calls real opencode
    "$HOME/.local/bin/opencode" "$@"
}

# =============================================================================
# GitHub Safety Function
# =============================================================================

# GitHub CLI wrapper to prevent accidental operations on non-owned repos
gh() {
  if [[ "$1" == "issue" && "$2" == "create" ]]; then
    # Parse --repo flag to get target repository
    local target_repo=""
    local args=("$@")
    
    # Look for --repo flag
    for ((i=3; i<=${#args[@]}; i++)); do
      if [[ "${args[i]}" == "--repo" && $((i+1)) -le ${#args[@]} ]]; then
        target_repo="${args[$((i+1))]}"
        break
      elif [[ "${args[i]}" == --repo=* ]]; then
        target_repo="${args[i]#--repo=}"
        break
      fi
    done
    
    # If no --repo flag, use current repository context
    if [[ -z "$target_repo" ]]; then
      target_repo=$(command gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown")
    fi
    
    # Extract owner from repo (e.g., "Cloud-Kinetix/bmad-enhanced" → "Cloud-Kinetix")
    local repo_owner=$(echo "$target_repo" | cut -d'/' -f1)
    
    # Define allowed organizations/users
    local allowed_owners=("Cloud-Kinetix" "smian0")
    
    if [[ "$target_repo" == "unknown" ]]; then
      echo "❌ BLOCKED: Cannot determine target repository!"
      echo "Please run from within a git repository or use --repo flag"
      echo "If this is intentional, use: command gh issue create ..."
      return 1
    fi
    
    if [[ ! " ${allowed_owners[@]} " =~ " ${repo_owner} " ]]; then
      echo "❌ BLOCKED: Cannot create issues in third-party repository!"
      echo "Target repo: $target_repo"
      echo "Owner: $repo_owner"  
      echo "Allowed owners: ${allowed_owners[*]}"
      echo ""
      echo "If this is intentional, use: command gh issue create ..."
      return 1
    fi
    
    echo "✅ Safe repository: $target_repo"
    command gh "$@"
  else
    command gh "$@"
  fi
}

# Auto-added by MCP Environment Setup
source "/Users/smian/.config/mcp-env/shell-env.sh"
