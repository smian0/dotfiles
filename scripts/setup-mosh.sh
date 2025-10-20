#!/usr/bin/env bash
# Optional Mosh Setup Script
# Run this after installing dotfiles to configure mosh for remote access
# This is OPTIONAL - only run if you plan to use mosh

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }
prompt() {
    echo -e "${YELLOW}[?]${NC} $1"
    read -p "    (y/n) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           MOSH CONFIGURATION (OPTIONAL)                  ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    error "This script is currently only for macOS"
fi

# Check if mosh is installed
if ! command -v mosh >/dev/null 2>&1; then
    error "Mosh not found. Run 'make install' first to install mosh."
fi

log "Mosh $(mosh --version | head -1) is installed"
echo ""

echo "This script will optionally:"
echo "  1. Enable SSH server (Remote Login)"
echo "  2. Set up SSH keys for localhost testing"
echo "  3. Configure macOS firewall for mosh"
echo ""

# Step 1: Enable SSH Server
echo -e "${BOLD}STEP 1: SSH Server${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ssh_running=false
if ps aux | grep -q "[s]shd" || timeout 2 nc -z localhost 22 2>/dev/null; then
    log "SSH server is already running"
    ssh_running=true
else
    if prompt "Enable SSH server (Remote Login)?"; then
        step "Enabling SSH server..."
        if sudo systemsetup -setremotelogin on 2>&1 | grep -q "already On\|enabled"; then
            log "SSH server enabled"
            ssh_running=true
        else
            warn "Failed to enable SSH server. Enable manually in System Settings."
        fi
    else
        warn "Skipping SSH server setup"
    fi
fi

echo ""

# Step 2: SSH Keys (only if SSH is running)
if [ "$ssh_running" = true ]; then
    echo -e "${BOLD}STEP 2: SSH Keys${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Check if key exists
    if [ -f ~/.ssh/id_ed25519 ]; then
        log "SSH key already exists"
    else
        if prompt "Generate SSH key for localhost access?"; then
            step "Generating SSH key..."
            ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "$(whoami)@$(hostname)"
            log "SSH key generated"
        fi
    fi

    # Check if key is in authorized_keys
    if [ -f ~/.ssh/id_ed25519.pub ]; then
        mkdir -p ~/.ssh
        touch ~/.ssh/authorized_keys
        chmod 700 ~/.ssh
        chmod 600 ~/.ssh/authorized_keys

        if grep -q "$(cat ~/.ssh/id_ed25519.pub)" ~/.ssh/authorized_keys 2>/dev/null; then
            log "SSH key already in authorized_keys"
        else
            if prompt "Add SSH key to authorized_keys for localhost access?"; then
                cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
                log "SSH key added to authorized_keys"
            fi
        fi
    fi

    echo ""
fi

# Step 3: Firewall Configuration
echo -e "${BOLD}STEP 3: Firewall Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -q "enabled"; then
    log "Firewall is enabled"

    if prompt "Configure firewall to allow mosh (UDP 60000-61000)?"; then
        step "Configuring firewall..."

        MOSH_SERVER_PATH=$(which mosh-server)
        sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$MOSH_SERVER_PATH" 2>/dev/null || true
        sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$MOSH_SERVER_PATH" 2>/dev/null || true
        sudo pkill -HUP socketfilterfw 2>/dev/null || true

        if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps 2>/dev/null | grep -q "mosh-server"; then
            log "Firewall configured for mosh"
        else
            warn "Could not verify firewall configuration"
        fi
    else
        warn "Skipping firewall configuration"
    fi
else
    warn "Firewall is disabled - skipping configuration"
fi

echo ""

# Step 4: Test Configuration
echo -e "${BOLD}STEP 4: Test Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$ssh_running" = true ]; then
    if prompt "Test mosh connection to localhost?"; then
        step "Testing mosh connection..."
        echo "(This will open a mosh session. Type 'exit' to close it)"
        echo ""

        if mosh localhost; then
            echo ""
            log "Mosh connection successful!"
        else
            warn "Mosh connection failed. Check troubleshooting guide."
        fi
    fi
else
    warn "SSH server not running - cannot test mosh"
fi

echo ""

# Summary
echo -e "${BOLD}SETUP COMPLETE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Mosh is configured!"
echo ""
echo "Usage:"
echo "  Local:  mosh localhost"
echo "  Remote: mosh $(whoami)@$(hostname)"
echo ""
echo "Documentation:"
echo "  Guide: docs/REMOTE-ACCESS.md"
echo "  Test:  ./scripts/test-mosh.sh"
echo ""
