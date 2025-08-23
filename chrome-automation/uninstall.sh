#!/bin/bash
# Chrome Automation Setup - Uninstallation Script
# Removes Chrome keeper service and cleans up files

set -e

echo "🗑️  Uninstalling Chrome Automation Setup..."
echo

HOME_DIR="$HOME"
LAUNCH_AGENTS_DIR="$HOME_DIR/Library/LaunchAgents"

echo "⏹️  Stopping Chrome Keeper service..."

# Unload LaunchAgent (ignore errors if not loaded)
launchctl unload "$LAUNCH_AGENTS_DIR/com.chrome.keeper.plist" 2>/dev/null || true
echo "   ✅ LaunchAgent stopped"

echo "🗂️  Removing files..."

# Remove LaunchAgent plist
if [ -f "$LAUNCH_AGENTS_DIR/com.chrome.keeper.plist" ]; then
    rm "$LAUNCH_AGENTS_DIR/com.chrome.keeper.plist"
    echo "   ✅ LaunchAgent configuration removed"
else
    echo "   ℹ️  LaunchAgent configuration not found"
fi

# Remove scripts
if [ -f "$HOME_DIR/chrome_keeper.sh" ]; then
    rm "$HOME_DIR/chrome_keeper.sh"
    echo "   ✅ chrome_keeper.sh removed"
else
    echo "   ℹ️  chrome_keeper.sh not found"
fi

if [ -f "$HOME_DIR/chrome_commands.sh" ]; then
    rm "$HOME_DIR/chrome_commands.sh"
    echo "   ✅ chrome_commands.sh removed"
else
    echo "   ℹ️  chrome_commands.sh not found"
fi

echo "🧹 Cleaning up log files..."

# Remove log files (optional - ask user)
if [ -f "$HOME_DIR/chrome_keeper.log" ] || [ -f "$HOME_DIR/chrome_keeper.error.log" ]; then
    echo "   📋 Log files found:"
    [ -f "$HOME_DIR/chrome_keeper.log" ] && echo "      • chrome_keeper.log"
    [ -f "$HOME_DIR/chrome_keeper.error.log" ] && echo "      • chrome_keeper.error.log"
    
    read -p "   🤔 Remove log files? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        [ -f "$HOME_DIR/chrome_keeper.log" ] && rm "$HOME_DIR/chrome_keeper.log"
        [ -f "$HOME_DIR/chrome_keeper.error.log" ] && rm "$HOME_DIR/chrome_keeper.error.log"
        echo "   ✅ Log files removed"
    else
        echo "   ℹ️  Log files kept"
    fi
else
    echo "   ℹ️  No log files found"
fi

echo
echo "✨ Uninstallation complete!"
echo
echo "📝 What was removed:"
echo "   • LaunchAgent: com.chrome.keeper.plist"
echo "   • Scripts: chrome_keeper.sh, chrome_commands.sh"
echo "   • Optionally: Log files"
echo
echo "💡 Chrome will no longer be automatically kept running"
echo "   You can still manually run Chrome for Claude Code MCP as needed"
echo