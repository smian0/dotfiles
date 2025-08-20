#!/bin/bash
# Chrome Automation Setup - Installation Script
# Installs Chrome keeper service for Claude Code MCP connectivity

set -e

echo "🚀 Installing Chrome Automation Setup for Claude Code MCP..."
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="$HOME"
LAUNCH_AGENTS_DIR="$HOME_DIR/Library/LaunchAgents"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

echo "📁 Installing scripts..."

# Copy and make scripts executable
cp "$SCRIPT_DIR/chrome_keeper.sh" "$HOME_DIR/chrome_keeper.sh"
chmod +x "$HOME_DIR/chrome_keeper.sh"
echo "   ✅ chrome_keeper.sh installed to $HOME_DIR/"

cp "$SCRIPT_DIR/chrome_commands.sh" "$HOME_DIR/chrome_commands.sh"
chmod +x "$HOME_DIR/chrome_commands.sh"
echo "   ✅ chrome_commands.sh installed to $HOME_DIR/"

echo "⚙️  Installing LaunchAgent..."

# Update paths in LaunchAgent plist to use actual home directory
sed "s|/Users/smian|$HOME_DIR|g" "$SCRIPT_DIR/com.chrome.keeper.plist" > "$LAUNCH_AGENTS_DIR/com.chrome.keeper.plist"
echo "   ✅ LaunchAgent installed to $LAUNCH_AGENTS_DIR/"

echo "🔧 Loading LaunchAgent..."

# Unload first in case it's already loaded (ignore errors)
launchctl unload "$LAUNCH_AGENTS_DIR/com.chrome.keeper.plist" 2>/dev/null || true

# Load the LaunchAgent
launchctl load "$LAUNCH_AGENTS_DIR/com.chrome.keeper.plist"
echo "   ✅ LaunchAgent loaded and will start automatically at login"

echo "🎯 Starting Chrome Keeper service..."

# Give it a moment to start
sleep 2

# Check status
if launchctl list | grep -q "com.chrome.keeper"; then
    echo "   ✅ Chrome Keeper service is running"
else
    echo "   ⚠️  Chrome Keeper service may need a moment to start"
fi

echo
echo "🎉 Installation complete!"
echo
echo "📋 Next steps:"
echo "   • Run: $HOME_DIR/chrome_commands.sh status    # Check service status"
echo "   • Run: $HOME_DIR/chrome_commands.sh logs      # View logs"
echo "   • Open Claude Code and test MCP connectivity"
echo
echo "💡 Management commands available at: $HOME_DIR/chrome_commands.sh"
echo "📚 Documentation: $SCRIPT_DIR/README.md"
echo

# Show current status
echo "📊 Current Status:"
"$HOME_DIR/chrome_commands.sh" status