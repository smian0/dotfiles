#!/usr/bin/env bash
# Git package installation script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }

log "Installing Git configuration..."

# Set up commit message template
git config --global commit.template ~/.gitmessage

# Install hooks to global git template directory
HOOKS_DIR="$HOME/.git-templates/hooks"
mkdir -p "$HOOKS_DIR"

if [[ -f "$SCRIPT_DIR/hooks/pre-commit" ]]; then
    cp "$SCRIPT_DIR/hooks/pre-commit" "$HOOKS_DIR/"
    chmod +x "$HOOKS_DIR/pre-commit"
    success "Installed pre-commit hook"
fi

# Configure Git to use the template directory
git config --global init.templatedir ~/.git-templates

# Apply hooks to existing repositories
log "Applying hooks to existing repositories..."

# Apply to dotfiles repo
if [[ -d "$HOME/.dotfiles" ]]; then
    cp "$HOOKS_DIR/pre-commit" "$HOME/.dotfiles/.git/hooks/" 2>/dev/null || true
    chmod +x "$HOME/.dotfiles/.git/hooks/pre-commit" 2>/dev/null || true
fi

# Apply to password store
if [[ -d "$HOME/.password-store" ]]; then
    cp "$HOOKS_DIR/pre-commit" "$HOME/.password-store/.git/hooks/" 2>/dev/null || true
    chmod +x "$HOME/.password-store/.git/hooks/pre-commit" 2>/dev/null || true
fi

success "Git configuration installed successfully"

log "Git aliases available:"
echo "  git lg    - Pretty log with graph"
echo "  git st    - Status"
echo "  git co    - Checkout"
echo "  git br    - Branch"
echo "  git cleanup - Remove merged branches"