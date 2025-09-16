#!/bin/bash
# OpenCode Wrapper Manager
# Manages the direct binary replacement wrapper for opencode command interception

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(dirname "$SCRIPT_DIR")"

# OpenCode paths
OPENCODE_BIN="$HOME/.npm-global/bin/opencode"
OPENCODE_BACKUP="$HOME/.npm-global/bin/opencode.original"
REAL_OPENCODE_PATH="/Users/smian/.npm-global/lib/node_modules/opencode-ai/node_modules/opencode-darwin-arm64/bin/opencode"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[OpenCode Manager]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1"; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }

# Check if opencode is installed
check_opencode_installed() {
    if [[ ! -f "$REAL_OPENCODE_PATH" ]]; then
        error "OpenCode not found. Please install with: npm install -g opencode-ai"
        exit 1
    fi
}

# Install the wrapper
install_wrapper() {
    log "Installing OpenCode wrapper..."
    
    check_opencode_installed
    
    # Backup original if it exists and isn't already our wrapper
    if [[ -f "$OPENCODE_BIN" ]] && ! grep -q "OpenCode Direct Binary Replacement Wrapper" "$OPENCODE_BIN" 2>/dev/null; then
        log "Backing up original opencode binary..."
        cp "$OPENCODE_BIN" "$OPENCODE_BACKUP"
        success "Original binary backed up to: $OPENCODE_BACKUP"
    fi
    
    # Create wrapper script with dynamic binary discovery
    cat > "$OPENCODE_BIN" << 'EOF'
#!/bin/bash
# OpenCode Direct Binary Replacement Wrapper
# This wrapper intercepts opencode commands to run agent transformation
# and then calls the real opencode binary directly

echo "🔧 [OpenCode Wrapper] Starting with args: $*" >&2

# Debug mode - uncomment to see what's being loaded
DEBUG_MODE=true

# Find real opencode binary dynamically
find_real_opencode() {
    # Try common locations in order of preference
    local candidates=(
        # npm global with architecture-specific binary
        "$HOME/.npm-global/lib/node_modules/opencode-ai/node_modules/opencode-darwin-arm64/bin/opencode"
        "$HOME/.npm-global/lib/node_modules/opencode-ai/node_modules/opencode-linux-x64/bin/opencode"
        "$HOME/.npm-global/lib/node_modules/opencode-ai/node_modules/opencode-win32-x64/bin/opencode"
        # Backup location if npm structure changes
        "$HOME/.npm-global/lib/node_modules/opencode-ai/bin/opencode"
        # System npm locations
        "/usr/local/lib/node_modules/opencode-ai/bin/opencode"
        "/opt/homebrew/lib/node_modules/opencode-ai/bin/opencode"
        # Fallback to backup if we have it
        "/Users/smian/.npm-global/bin/opencode.original"
    )
    
    for candidate in "${candidates[@]}"; do
        if [[ -x "$candidate" ]]; then
            echo "$candidate"
            return 0
        fi
    done
    
    # Last resort: try to find via npm
    local npm_prefix=$(npm prefix -g 2>/dev/null || echo "")
    if [[ -n "$npm_prefix" ]]; then
        local npm_candidate="$npm_prefix/lib/node_modules/opencode-ai/bin/opencode"
        if [[ -x "$npm_candidate" ]]; then
            echo "$npm_candidate"
            return 0
        fi
    fi
    
    return 1
}

REAL_OPENCODE=$(find_real_opencode)
if [[ -z "$REAL_OPENCODE" ]]; then
    echo "Error: Real opencode binary not found in any expected location" >&2
    echo "Try running: npm install -g opencode-ai" >&2
    exit 1
fi

[[ "$DEBUG_MODE" == "true" ]] && echo "Using real opencode at: $REAL_OPENCODE"

# Load environment variables from system (launchctl)
load_env_var() {
    local var_name="$1"
    local var_value=$(launchctl getenv "$var_name" 2>/dev/null || echo "")
    if [[ -n "$var_value" ]]; then
        export "$var_name"="$var_value"
        [[ "$DEBUG_MODE" == "true" ]] && echo "Loaded $var_name: ${var_value:0:10}..."
    fi
}

# Load all API keys from system environment
load_env_var "OLLAMA_API_KEY"
load_env_var "OPENAI_API_KEY" 
load_env_var "ANTHROPIC_API_KEY"
load_env_var "GITHUB_TOKEN"
load_env_var "DEEPSEEK_API_KEY"
load_env_var "GLM_API_KEY"
load_env_var "KIMI_API_KEY"
load_env_var "BRAVE_API_KEY"

# Pre-launch agent transformation
run_pre_launch_transform() {
    local pre_launch_script="$HOME/dotfiles/opencode/.config/opencode/scripts/pre-launch-transform.js"
    
    # Only run transformation for commands that might load agents
    case "${1:-}" in
        "" | "-h" | "--help" | "help" | "version" | "--version")
            # These commands don't load agents, skip transformation
            return 0
            ;;
        *)
            # All other commands might load agents, run transformation
            if [[ -f "$pre_launch_script" ]]; then
                [[ "$DEBUG_MODE" == "true" ]] && echo "Running pre-launch agent transformation..."
                if node "$pre_launch_script" 2>/dev/null; then
                    [[ "$DEBUG_MODE" == "true" ]] && echo "✅ Pre-launch transformation completed"
                else
                    [[ "$DEBUG_MODE" == "true" ]] && echo "⚠️  Pre-launch transformation had issues, proceeding anyway..."
                fi
            else
                [[ "$DEBUG_MODE" == "true" ]] && echo "⚠️  Pre-launch transform script not found, proceeding..."
            fi
            ;;
    esac
}

# Run pre-launch agent transformation
run_pre_launch_transform "$@"

# Execute the real opencode with all arguments
[[ "$DEBUG_MODE" == "true" ]] && echo "Executing: $REAL_OPENCODE $*"
exec "$REAL_OPENCODE" "$@"
EOF
    
    chmod +x "$OPENCODE_BIN"
    success "OpenCode wrapper installed successfully!"
}

# Restore original opencode
restore_original() {
    log "Restoring original opencode binary..."
    
    if [[ -f "$OPENCODE_BACKUP" ]]; then
        cp "$OPENCODE_BACKUP" "$OPENCODE_BIN"
        success "Original opencode binary restored"
    else
        warn "No backup found, reinstalling from npm..."
        rm -f "$OPENCODE_BIN"
        npm install -g opencode-ai
        success "OpenCode reinstalled from npm"
    fi
}

# Check wrapper status
status() {
    log "OpenCode Wrapper Status:"
    echo
    
    if [[ -f "$OPENCODE_BIN" ]]; then
        if grep -q "OpenCode Direct Binary Replacement Wrapper" "$OPENCODE_BIN" 2>/dev/null; then
            success "Wrapper is installed and active"
            echo "  Location: $OPENCODE_BIN"
        else
            warn "OpenCode binary exists but wrapper is not installed"
        fi
    else
        error "OpenCode binary not found"
    fi
    
    if [[ -f "$OPENCODE_BACKUP" ]]; then
        success "Backup exists: $OPENCODE_BACKUP"
    else
        warn "No backup found"
    fi
    
    if [[ -f "$REAL_OPENCODE_PATH" ]]; then
        success "Real OpenCode binary found: $REAL_OPENCODE_PATH"
    else
        error "Real OpenCode binary not found - install with: npm install -g opencode-ai"
    fi
}

# Show usage
usage() {
    echo "OpenCode Wrapper Manager"
    echo
    echo "Usage: $0 <command>"
    echo
    echo "Commands:"
    echo "  install    Install the OpenCode wrapper"
    echo "  restore    Restore original OpenCode binary"
    echo "  status     Show wrapper status"
    echo "  help       Show this help message"
    echo
    echo "Examples:"
    echo "  $0 install    # Install wrapper after npm update"
    echo "  $0 restore    # Remove wrapper and restore original"
    echo "  $0 status     # Check current state"
}

# Main script logic
case "${1:-}" in
    install)
        install_wrapper
        ;;
    restore)
        restore_original
        ;;
    status)
        status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: ${1:-}"
        echo
        usage
        exit 1
        ;;
esac