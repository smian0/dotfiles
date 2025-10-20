#!/bin/zsh
# Interactive demo script for navigation & session management
# Run this in your zsh shell to see everything working

echo "🎯 Navigation & Session Management Demo"
echo "========================================"
echo ""

# Test zoxide
echo "📍 Testing Zoxide (Smart Directory Navigation)"
echo "----------------------------------------------"
echo ""
echo "1. Creating test directories..."
mkdir -p /tmp/demo-project-{api,web,docs}
cd /tmp/demo-project-api && pwd
cd /tmp/demo-project-web && pwd
cd /tmp/demo-project-docs && pwd
cd /tmp

echo ""
echo "2. Zoxide learned these directories. Try:"
echo "   z api     → jumps to /tmp/demo-project-api"
echo "   z web     → jumps to /tmp/demo-project-web"
echo "   z docs    → jumps to /tmp/demo-project-docs"
echo ""
echo "3. View your directory history:"
zoxide query --list --score | head -10
echo ""

# Test sesh
echo "📊 Testing Sesh (Session Management)"
echo "------------------------------------"
echo ""
echo "Current tmux sessions:"
sesh list || echo "(No active sessions)"
echo ""
echo "Available commands:"
echo "  sl   → List all sessions"
echo "  sc   → Create session in current directory"
echo "  ss   → Interactive session selector"
echo "  sk   → Kill a session"
echo ""

# Cleanup
echo "🧹 Cleanup"
echo "---------"
read -q "REPLY?Remove test directories? (y/n) "
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf /tmp/demo-project-*
    echo "✅ Test directories removed"
else
    echo "ℹ️  Test directories kept at /tmp/demo-project-*"
fi

echo ""
echo "✨ Demo complete! Try these commands:"
echo "   z <keyword>   - Jump to directory"
echo "   zi            - Interactive search"
echo "   ss            - Select session"
echo "   sc            - Create session here"
