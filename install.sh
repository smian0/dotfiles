#!/usr/bin/env bash
# Dotfiles installation script
# Supports macOS and Ubuntu Linux

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            if [[ "$ID" == "ubuntu" ]]; then
                echo "ubuntu"
            else
                echo "linux"
            fi
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
log "Detected OS: $OS"

# Check if running from dotfiles directory
if [[ ! -f ".stow-global-ignore" ]]; then
    error "Must run from dotfiles repository root directory"
fi

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    if [[ "$OS" == "macos" ]]; then
        # Check if Homebrew is installed
        if ! command -v brew >/dev/null 2>&1; then
            warn "Homebrew not installed. Installing..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install required packages
        brew install stow pass gnupg pinentry-mac git node mosh
        
    elif [[ "$OS" == "ubuntu" ]]; then
        # Update package list
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y stow pass gnupg2 git curl nodejs npm mosh
        
    else
        warn "Unknown OS. Please install manually: stow, pass, gpg, git"
    fi
}

# Check for required tools
check_requirements() {
    local missing_tools=()
    
    for tool in git stow npm; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        warn "Missing required tools: ${missing_tools[*]}"
        read -p "Install missing dependencies? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            error "Required tools not installed. Exiting."
        fi
    fi
}

# Core packages to install
CORE_PACKAGES=("git" "zsh" "vim")

# Parse command line arguments
PACKAGES=()
INSTALL_ALL=false
DRY_RUN=false
PROFILE=""
NON_INTERACTIVE=false
INSTALL_CLAUDE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            INSTALL_ALL=true
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --non-interactive|--yes|-y)
            NON_INTERACTIVE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options] [packages...]"
            echo "Options:"
            echo "  --all              Install all available packages"
            echo "  --profile NAME     Install specific profile (default, minimal)"
            echo "  --dry-run          Show what would be installed without making changes"
            echo "  --non-interactive  Skip confirmation prompts (for automation)"
            echo "  --yes, -y          Same as --non-interactive"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Install default profile + Claude Code"
            echo "  $0 --all           # Install everything + Claude Code"
            echo "  $0 --profile minimal      # Install minimal profile (git, vim, zsh)"
            echo "  $0 --profile default      # Install default profile (explicit)"
            echo "  $0 git zsh         # Install specific packages"
            exit 0
            ;;
        *)
            PACKAGES+=("$1")
            shift
            ;;
    esac
done

# Install Claude Code globally
install_claude_code() {
    if command -v npm >/dev/null 2>&1; then
        if npm list -g @anthropic-ai/claude-code >/dev/null 2>&1; then
            log "Claude Code is already installed globally"
        else
            log "Installing Claude Code globally via npm..."
            npm install -g @anthropic-ai/claude-code
            log "Claude Code installed successfully"
        fi
    else
        warn "npm not available, skipping Claude Code installation"
        warn "Install Node.js first: brew install node"
    fi
    
    # Install dependencies for markdown linting system
    install_markdown_linting_deps
}

install_markdown_linting_deps() {
    log "Installing markdown linting dependencies..."
    
    # Install uv (Python package manager) if not present
    if ! command -v uv >/dev/null 2>&1; then
        log "Installing uv (Python package manager)..."
        if [[ "$OS" == "macos" ]]; then
            if command -v brew >/dev/null 2>&1; then
                brew install uv
            else
                curl -LsSf https://astral.sh/uv/install.sh | sh
            fi
        else
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
        
        # Add to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        log "uv already installed"
    fi
    
    # Install fswatch for file monitoring (optional)
    if [[ "$OS" == "macos" ]] && command -v brew >/dev/null 2>&1; then
        if ! command -v fswatch >/dev/null 2>&1; then
            log "Installing fswatch for markdown file monitoring..."
            brew install fswatch
        else
            log "fswatch already installed"
        fi
    fi
    
    # Verify marksman MCP server can run
    if [[ -f "claude/.claude/mcp_servers/marksman_mcp_server.py" ]]; then
        log "Testing marksman MCP server..."
        if uv run --script claude/.claude/mcp_servers/marksman_mcp_server.py --help >/dev/null 2>&1; then
            log "✅ Marksman MCP server is working"
        else
            warn "⚠️  Marksman MCP server test failed - check dependencies"
        fi
    else
        warn "⚠️  Marksman MCP server not found at expected location"
    fi
}

# Check requirements
check_requirements

# Determine what to install
if [[ -n "$PROFILE" ]]; then
    # Load packages from profile
    PROFILE_FILE="profiles/${PROFILE}.txt"
    if [[ -f "$PROFILE_FILE" ]]; then
        log "Installing profile: $PROFILE"
        # Install Claude Code with default profile
        if [[ "$PROFILE" == "default" ]]; then
            INSTALL_CLAUDE=true
            install_claude_code
        fi
        PACKAGES=()
        while IFS= read -r package; do
            [[ -n "$package" ]] && PACKAGES+=("$package")
        done < "$PROFILE_FILE"
    else
        error "Profile not found: $PROFILE"
    fi
elif [[ $INSTALL_ALL == true ]]; then
    log "Installing all packages and Claude Code..."
    INSTALL_CLAUDE=true
    install_claude_code
    PACKAGES=(".claude" ".cursor" ".taskmaster" ".windsurf" "bin" "claude-project" "direnv" "git" "pass-store" "vim" "zsh")
elif [[ ${#PACKAGES[@]} -eq 0 ]]; then
    log "Installing default profile and Claude Code..."
    INSTALL_CLAUDE=true
    install_claude_code
    # Load default profile
    PROFILE_FILE="profiles/default.txt"
    if [[ -f "$PROFILE_FILE" ]]; then
        PACKAGES=()
        while IFS= read -r package; do
            [[ -n "$package" ]] && PACKAGES+=("$package")
        done < "$PROFILE_FILE"
    else
        warn "Default profile not found, using core packages"
        PACKAGES=("${CORE_PACKAGES[@]}")
    fi
fi

# Show installation plan and ask for confirmation
show_installation_plan() {
    echo ""
    echo "============================================="
    echo "           DOTFILES INSTALLATION PLAN"
    echo "============================================="
    echo ""
    
    # Show system info
    echo "🖥️  System Information:"
    echo "   OS: $OS"
    echo "   Shell: $SHELL"
    echo "   User: $USER"
    echo "   Home: $HOME"
    echo ""
    
    # Show what will be installed
    echo "📦 Packages to install:"
    for package in "${PACKAGES[@]}"; do
        if [[ -d "$package" ]]; then
            echo "   ✓ $package"
            # Show package contents
            if [[ -f "$package/.description" ]]; then
                echo "     $(cat "$package/.description")"
            else
                case "$package" in
                    git) echo "     Git configuration with aliases and colors" ;;
                    zsh) echo "     Zsh with Oh My Zsh, plugins, and custom config" ;;
                    vim) echo "     Vim configuration and settings" ;;
                    bin) echo "     Custom utility scripts" ;;
                    direnv) echo "     Directory environment management" ;;
                    pass-store) echo "     Password store configuration" ;;
                    ccstatusline) echo "     Claude Code status line configuration" ;;
                    *) echo "     Package configuration files" ;;
                esac
            fi
        else
            echo "   ✗ $package (not found)"
        fi
    done
    echo ""
    
    # Show additional installations
    echo "🔧 Additional installations:"
    if [[ $INSTALL_CLAUDE == true ]]; then
        echo "   ✓ Claude Code (npm global package)"
        echo "     AI-powered code assistant CLI"
    else
        echo "   • Claude Code installation skipped (specific packages selected)"
    fi
    
    # Show dependencies that might be installed
    echo ""
    echo "📋 Dependencies (will be installed if missing):"
    echo "   • GNU Stow (for symlink management)"
    echo "   • Pass (password store)"
    echo "   • GPG (encryption)"
    echo "   • Git (version control)"
    echo "   • Node.js & npm (for Claude Code)"
    
    if [[ "$OS" == "macos" ]]; then
        echo "   • Homebrew (package manager for macOS)"
    fi
    echo ""
    
    # Show what files will be backed up
    echo "💾 Files that will be backed up (if they exist):"
    for package in "${PACKAGES[@]}"; do
        case "$package" in
            zsh) echo "   • ~/.zshrc → ~/.zshrc.backup" ;;
            git) echo "   • ~/.gitconfig → ~/.gitconfig.backup" ;;
            vim) echo "   • ~/.vimrc → ~/.vimrc.backup" ;;
        esac
    done
    echo ""
    
    echo "⚡ Installation will:"
    echo "   1. Check and install missing dependencies"
    echo "   2. Backup existing configuration files"
    echo "   3. Run package-specific setup scripts (if needed)"
    echo "   4. Create symlinks using GNU Stow"
    echo "   5. Install Claude Code globally via npm"
    echo ""
}

# Ask for user confirmation
ask_confirmation() {
    if [[ $NON_INTERACTIVE == true ]]; then
        log "Non-interactive mode: skipping confirmation"
        return 0
    fi
    
    show_installation_plan
    
    echo "❓ Do you want to proceed with this installation? [y/N]"
    echo -n "   Enter your choice: "
    read -r response
    
    case "$response" in
        [yY]|[yY][eE][sS])
            echo ""
            log "Installation confirmed. Proceeding..."
            return 0
            ;;
        *)
            echo ""
            warn "Installation cancelled by user."
            echo "💡 Tips:"
            echo "   • Use --dry-run to see what would be installed"
            echo "   • Use --help to see all available options"
            echo "   • Use --non-interactive to skip this prompt"
            exit 0
            ;;
    esac
}

# Handle dry run mode
if [[ $DRY_RUN == true ]]; then
    log "DRY RUN MODE - No changes will be made"
    show_installation_plan
    echo "🏃 This was a dry run. No actual changes were made."
    echo "   Remove --dry-run to perform the actual installation."
    exit 0
fi

# Ask for confirmation before proceeding
ask_confirmation

# Backup existing configurations
backup_existing() {
    local target="$1"
    if [[ -e "$HOME/$target" ]] && [[ ! -L "$HOME/$target" ]]; then
        warn "Backing up existing $target to $target.backup"
        mv "$HOME/$target" "$HOME/$target.backup"
    fi
}

# Install packages with Stow
log "Installing packages: ${PACKAGES[*]}"
for package in "${PACKAGES[@]}"; do
    if [[ -d "$package" ]]; then
        log "Stowing $package..."
        
        # Handle special cases and run package-specific setup
        if [[ "$package" == "zsh" ]]; then
            backup_existing ".zshrc"
            # Run zsh package setup BEFORE stowing
            if [[ -f "$package/install.sh" ]]; then
                log "Running zsh package setup..."
                (cd "$package" && bash install.sh)
                # Clean up any conflicting files that Oh My Zsh might have created
                if [[ -f "$HOME/.zshrc" ]] && [[ ! -L "$HOME/.zshrc" ]]; then
                    mv "$HOME/.zshrc" "$HOME/.zshrc.oh-my-zsh-template"
                fi
            fi
        elif [[ "$package" == "git" ]]; then
            backup_existing ".gitconfig"
        elif [[ "$package" == "vim" ]]; then
            backup_existing ".vimrc"
        fi
        
        stow -v "$package"
    else
        warn "Package $package not found, skipping"
    fi
done


# Clone pass-store repository if it doesn't exist
if [[ ! -d "$HOME/.password-store" ]]; then
    log "Pass store not found. Would you like to clone it?"
    read -p "Clone pass-store repository? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git clone git@github.com:smian0/pass-store.git "$HOME/.password-store"
        log "Pass store cloned to ~/.password-store"
    fi
fi

log "✅ Dotfiles installation completed!"
log ""
log "Next steps:"
log "1. Configure GPG key for pass (if not already done)"
log "2. Add API keys to pass: pass insert api/anthropic"
log "3. Restart your shell or run: source ~/.zshrc"
log "4. Run 'stow <package>' to add more configurations"

if command -v claude >/dev/null 2>&1; then
    log ""
    log "🤖 Claude Code detected. Run 'claude doctor' to verify configuration"
fi