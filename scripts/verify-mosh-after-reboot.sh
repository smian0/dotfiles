#!/usr/bin/env bash
# Verify mosh configuration persists after macOS reboot
# Run this after restarting your Mac to ensure everything still works

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║      POST-REBOOT MOSH VERIFICATION                       ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

passed=0
failed=0

# Test 1: SSH Server
echo -e "${BLUE}[TEST 1]${NC} SSH Server Status"
if launchctl list 2>/dev/null | grep -q "ssh" || ps aux | grep -q "[s]shd"; then
    echo -e "${GREEN}✓${NC} SSH server is running"
    ((passed++))
else
    echo -e "${RED}✗${NC} SSH server is NOT running"
    echo "  Fix: System Settings > General > Sharing > Remote Login"
    ((failed++))
fi
echo ""

# Test 2: Firewall Configuration
echo -e "${BLUE}[TEST 2]${NC} Firewall Rules"
if sudo -n /usr/libexec/ApplicationFirewall/socketfilterfw --listapps 2>/dev/null | grep -q "mosh-server"; then
    echo -e "${GREEN}✓${NC} mosh-server is in firewall allowed list"
    ((passed++))
else
    if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -q "disabled"; then
        echo -e "${YELLOW}○${NC} Firewall is disabled (mosh will work)"
        ((passed++))
    else
        echo -e "${YELLOW}⚠${NC}  Cannot verify firewall (requires sudo)"
        echo "  Run: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep mosh"
    fi
fi
echo ""

# Test 3: PATH Configuration
echo -e "${BLUE}[TEST 3]${NC} PATH Configuration"
if ssh -o ConnectTimeout=3 localhost "which mosh-server" 2>/dev/null | grep -q "mosh-server"; then
    echo -e "${GREEN}✓${NC} mosh-server accessible in SSH sessions"
    echo "  $(ssh localhost 'which mosh-server' 2>/dev/null)"
    ((passed++))
else
    echo -e "${RED}✗${NC} mosh-server NOT found in SSH PATH"
    echo "  Fix: Check ~/.zshenv contains Homebrew PATH"
    ((failed++))
fi
echo ""

# Test 4: Mosh Connection
echo -e "${BLUE}[TEST 4]${NC} Mosh Connection Test"
if timeout 10 mosh localhost -- exit 2>/dev/null; then
    echo -e "${GREEN}✓${NC} mosh connection successful!"
    ((passed++))
else
    echo -e "${RED}✗${NC} mosh connection failed"
    echo "  Check SSH keys: ssh localhost"
    ((failed++))
fi
echo ""

# Summary
echo -e "${BOLD}SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed:${NC} $passed tests"
echo -e "${RED}Failed:${NC} $failed tests"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ All configuration persisted after reboot!${NC}"
    echo ""
    echo "Mosh is ready to use:"
    echo "  mosh localhost"
    echo "  mosh $(whoami)@$(hostname)"
else
    echo -e "${YELLOW}Some issues detected. Run diagnostics:${NC}"
    echo "  make test-mosh"
fi
echo ""
