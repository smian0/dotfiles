#!/usr/bin/env bash
# Test mosh installation and configuration
# Can be run anytime to verify mosh is properly set up

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

passed=0
failed=0
warnings=0

echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           MOSH INSTALLATION TEST REPORT                  ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# System information
echo -e "${BLUE}📋 SYSTEM INFORMATION${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OS: macOS $(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
echo "Architecture: $(uname -m)"
echo "Shell: $SHELL"
echo ""

# Test results header
echo -e "${BOLD}TEST RESULTS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Mosh client installed
if command -v mosh >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Mosh client installed: $(which mosh)"
    ((passed++))
else
    echo -e "${RED}✗${NC} Mosh client not found"
    ((failed++))
fi

# Test 2: Mosh server installed
if command -v mosh-server >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Mosh server installed: $(which mosh-server)"
    ((passed++))
else
    echo -e "${RED}✗${NC} Mosh server not found"
    ((failed++))
fi

# Test 3: Version check
if command -v mosh >/dev/null 2>&1; then
    version=$(mosh --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} Mosh version: $version"
    ((passed++))
fi

# Test 4: Executables are runnable
if [ -x "$(which mosh 2>/dev/null)" ]; then
    echo -e "${GREEN}✓${NC} Mosh client is executable"
    ((passed++))
else
    echo -e "${RED}✗${NC} Mosh client is not executable"
    ((failed++))
fi

if [ -x "$(which mosh-server 2>/dev/null)" ]; then
    echo -e "${GREEN}✓${NC} Mosh server is executable"
    ((passed++))
else
    echo -e "${RED}✗${NC} Mosh server is not executable"
    ((failed++))
fi

# Test 5: Binary type check
if command -v mosh-server >/dev/null 2>&1; then
    if file "$(which mosh-server)" | grep -q "Mach-O.*executable"; then
        echo -e "${GREEN}✓${NC} Mosh server is valid Mach-O executable"
        ((passed++))
    fi
fi

echo ""

# SSH server check
echo -e "${BLUE}🔌 SERVICES STATUS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if launchctl list 2>/dev/null | grep -q "com.openssh.sshd"; then
    echo -e "${GREEN}✓${NC} SSH server is running"
    ssh_running=true
    ((passed++))
else
    echo -e "${YELLOW}⚠${NC}  SSH server is NOT running"
    echo "   Enable: System Settings > General > Sharing > Remote Login"
    ssh_running=false
    ((warnings++))
fi

echo ""

# Firewall check
echo -e "${BLUE}🔥 FIREWALL STATUS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we can read firewall status
if sudo -n /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate >/dev/null 2>&1; then
    if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
        echo -e "${GREEN}✓${NC} Firewall is enabled"

        if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps 2>/dev/null | grep -q "mosh-server"; then
            echo -e "${GREEN}✓${NC} mosh-server is in firewall allowed list"
            ((passed++))
        else
            echo -e "${YELLOW}⚠${NC}  mosh-server NOT in firewall allowed list"
            echo "   Run: ./scripts/configure-mosh-firewall.sh"
            ((warnings++))
        fi
    else
        echo -e "${YELLOW}⚠${NC}  Firewall is disabled"
        ((warnings++))
    fi
else
    echo -e "${YELLOW}⚠${NC}  Cannot check firewall status (requires sudo)"
    echo "   Check manually:"
    echo "   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep mosh"
    ((warnings++))
fi

echo ""

# Connection test (only if SSH is running)
if [ "$ssh_running" = true ]; then
    echo -e "${BLUE}🔗 CONNECTION TEST${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Try to connect to localhost
    if timeout 5 mosh localhost -- exit 2>&1 >/dev/null; then
        echo -e "${GREEN}✓${NC} Successfully connected to localhost via mosh"
        ((passed++))
    else
        echo -e "${RED}✗${NC} Failed to connect to localhost via mosh"
        echo "   Check SSH keys and firewall configuration"
        ((failed++))
    fi
    echo ""
fi

# Summary
echo -e "${BOLD}SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed:${NC}   $passed tests"
echo -e "${YELLOW}Warnings:${NC} $warnings items need attention"
echo -e "${RED}Failed:${NC}   $failed tests"
echo ""

# Next steps
if [ $failed -gt 0 ] || [ $warnings -gt 0 ]; then
    echo -e "${BOLD}📝 RECOMMENDED ACTIONS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ "$ssh_running" = false ]; then
        echo "1️⃣  Enable SSH Server"
        echo "   System Settings > General > Sharing > Remote Login"
        echo ""
    fi

    echo "2️⃣  Configure Firewall"
    echo "   ./scripts/configure-mosh-firewall.sh"
    echo ""

    echo "3️⃣  Test Connection"
    echo "   mosh localhost"
    echo ""
fi

echo -e "${BLUE}📚 Documentation:${NC} docs/REMOTE-ACCESS.md"
echo ""

# Exit with appropriate code
if [ $failed -gt 0 ]; then
    exit 1
elif [ $warnings -gt 0 ]; then
    exit 2
else
    exit 0
fi
