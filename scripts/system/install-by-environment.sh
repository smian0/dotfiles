#!/usr/bin/env bash
# Environment-based installation script
# Automatically detects environment and installs appropriate packages

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Environment detection
detect_environment() {
    local env="personal"  # default
    
    # Check for work indicators
    if [[ "$(hostname)" == *"work"* ]] || [[ "$(hostname)" == *"corp"* ]] || [[ -d "/Applications/Microsoft Teams.app" ]]; then
        env="work"
    fi
    
    # Check for CI environment
    if [[ -n "${CI:-}" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        env="minimal"
    fi
    
    # Check for server environment (no GUI)
    if [[ ! -d "/Applications" ]] && [[ "$OSTYPE" == "linux-gnu"* ]]; then
        env="minimal"
    fi
    
    # Allow override via environment variable
    env="${DOTFILES_PROFILE:-$env}"
    
    echo "$env"
}

# Install based on detected environment
main() {
    local environment
    environment=$(detect_environment)
    
    echo "Detected environment: $environment"
    echo "Override with: DOTFILES_PROFILE=<profile> $0"
    echo ""
    
    # Use profile manager
    bash "$SCRIPT_DIR/profile-manager.sh" install "$environment"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi