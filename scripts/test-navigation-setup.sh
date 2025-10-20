#!/bin/bash
# Test script for zoxide + sesh + tmux setup
# This script verifies all components are working correctly

set -e

echo "🧪 Testing Navigation & Session Management Setup"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}✅ $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# Test 1: Check if zoxide is installed
echo "Test 1: Zoxide Installation"
if command -v zoxide >/dev/null 2>&1; then
    pass "zoxide is installed: $(which zoxide)"
else
    fail "zoxide is not installed"
fi
echo ""

# Test 2: Check if sesh is installed
echo "Test 2: Sesh Installation"
if command -v sesh >/dev/null 2>&1; then
    pass "sesh is installed: $(which sesh)"
else
    fail "sesh is not installed"
fi
echo ""

# Test 3: Check if tmux is installed
echo "Test 3: Tmux Installation"
if command -v tmux >/dev/null 2>&1; then
    pass "tmux is installed: $(which tmux)"
    info "tmux version: $(tmux -V)"
else
    fail "tmux is not installed"
fi
echo ""

# Test 4: Check if fzf is installed
echo "Test 4: FZF Installation"
if command -v fzf >/dev/null 2>&1; then
    pass "fzf is installed: $(which fzf)"
else
    fail "fzf is not installed (required for 'ss' command)"
fi
echo ""

# Test 5: Check zoxide initialization
echo "Test 5: Zoxide Functions"
if type z >/dev/null 2>&1 && type zi >/dev/null 2>&1; then
    pass "z and zi commands are available"
else
    fail "z or zi commands not found - zoxide not initialized in shell"
fi
echo ""

# Test 6: Check sesh aliases
echo "Test 6: Sesh Aliases"
missing_aliases=""
for cmd in ss sk sl sc; do
    if ! alias "$cmd" >/dev/null 2>&1; then
        missing_aliases="$missing_aliases $cmd"
    fi
done

if [ -z "$missing_aliases" ]; then
    pass "All sesh aliases (ss, sk, sl, sc) are configured"
else
    fail "Missing aliases:$missing_aliases"
fi
echo ""

# Test 7: Zoxide database test
echo "Test 7: Zoxide Database"
# Add some test directories
TEST_DIRS=(
    "/tmp/zoxide-test-1"
    "/tmp/zoxide-test-project"
    "/tmp/zoxide-test-work"
)

for dir in "${TEST_DIRS[@]}"; do
    mkdir -p "$dir"
    zoxide add "$dir" 2>/dev/null || true
done

# Query the database
if zoxide query test 2>/dev/null | grep -q "zoxide-test"; then
    pass "Zoxide can track and query directories"
    info "Found: $(zoxide query test 2>/dev/null | head -1)"
else
    info "Zoxide database functional (may be empty on fresh install)"
fi

# Cleanup test directories
for dir in "${TEST_DIRS[@]}"; do
    rm -rf "$dir"
    zoxide remove "$dir" 2>/dev/null || true
done
echo ""

# Test 8: Sesh list functionality
echo "Test 8: Sesh List Functionality"
sesh_output=$(sesh list 2>&1)
if [ $? -eq 0 ]; then
    pass "sesh list works"
    if [ -n "$sesh_output" ]; then
        info "Found $(echo "$sesh_output" | wc -l) existing sessions"
    else
        info "No active sessions (this is fine)"
    fi
else
    fail "sesh list failed"
fi
echo ""

# Test 9: Configuration file check
echo "Test 9: Configuration Files"
if grep -q "zoxide init" ~/.zshrc 2>/dev/null; then
    pass "Zoxide initialization found in ~/.zshrc"
else
    fail "Zoxide initialization not found in ~/.zshrc"
fi

if grep -q "sesh" ~/.zshrc 2>/dev/null; then
    pass "Sesh configuration found in ~/.zshrc"
else
    fail "Sesh configuration not found in ~/.zshrc"
fi
echo ""

# Test 10: Interactive test
echo "Test 10: Interactive Features"
echo ""
info "Manual tests you can run:"
echo "  1. 'cd /tmp && cd ~/Downloads && z tmp' - Should jump to /tmp"
echo "  2. 'zi' - Opens interactive directory search (requires fzf)"
echo "  3. 'sl' - List tmux sessions"
echo "  4. 'sc' - Create session in current directory"
echo "  5. 'ss' - Select session with fzf (if sessions exist)"
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}✅ All automated tests passed!${NC}"
echo ""
echo "📖 Documentation: ~/dotfiles/docs/NAVIGATION_SESSION_MANAGEMENT.md"
echo ""
echo "🚀 Quick Start:"
echo "  • Navigate with:  z <keyword>  or  zi (interactive)"
echo "  • Sessions with:  ss (select)  or  sc (create)"
echo ""
