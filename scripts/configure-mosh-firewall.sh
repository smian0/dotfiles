#!/usr/bin/env bash
# Configure macOS firewall for Mosh (Mobile Shell)
# Mosh uses UDP ports 60000-61000 for persistent connections

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    error "This script is only for macOS"
fi

# Check if mosh-server is installed
if ! command -v mosh-server >/dev/null 2>&1; then
    error "mosh-server not found. Install with: brew install mosh"
fi

# Get mosh-server path
MOSH_SERVER_PATH=$(which mosh-server)
log "Found mosh-server at: $MOSH_SERVER_PATH"

# Check if firewall is enabled
if ! sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
    warn "Firewall is not enabled. Skipping configuration."
    exit 0
fi

log "Configuring macOS firewall for mosh..."

# Add mosh-server to firewall allowed applications
log "Adding mosh-server to firewall allowed applications..."
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$MOSH_SERVER_PATH"

# Set mosh-server to allow incoming connections
log "Setting mosh-server to allow incoming connections..."
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$MOSH_SERVER_PATH"

# Reload firewall rules
log "Reloading firewall rules..."
if sudo pfctl -f /etc/pf.conf 2>/dev/null; then
    log "Firewall rules reloaded successfully"
else
    warn "Could not reload PF rules (may not be configured)"
fi

# Verify configuration
log "Verifying firewall configuration..."
if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep -q "mosh-server"; then
    echo -e "${GREEN}✓${NC} mosh-server is configured in the firewall"
else
    warn "mosh-server may not be properly configured in the firewall"
fi

echo
log "Mosh firewall configuration complete!"
log "Mosh uses UDP ports 60000-61000 for connections"
echo
echo "To verify mosh is working:"
echo "  1. On this machine: Start SSH server (System Settings > General > Sharing)"
echo "  2. From another machine: mosh user@hostname"
echo
echo "If you still have connection issues, check:"
echo "  - System Settings > Network > Firewall > Options"
echo "  - Ensure mosh-server is in the allowed applications list"
echo "  - UDP ports 60000-61000 are not blocked by your router"
