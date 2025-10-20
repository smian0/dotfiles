#!/bin/bash
# Comet Browser Remote Debug Launcher
# Usage: launch-comet-debug.sh [DEBUG_PORT]
# Example: launch-comet-debug.sh 9223

set -e

DEBUG_PORT="${1:-9223}"
USE_TEMP_PROFILE="${2:-yes}"

if [ "$USE_TEMP_PROFILE" = "yes" ]; then
    USER_DATA_DIR="/tmp/comet-debug-temp"
    PROFILE_NAME="DebugProfile"
else
    USER_DATA_DIR="$HOME/Library/Application Support/Comet"
    PROFILE_NAME="Default"
fi

echo "🚀 Comet Browser Remote Debug Launcher"
echo "======================================"
echo "Profile: $PROFILE_NAME"
echo "Port: $DEBUG_PORT"
echo "User Data: $USER_DATA_DIR"
echo ""

# Kill existing Comet instances on this port
if lsof -Pi :$DEBUG_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $DEBUG_PORT is in use. Killing existing Comet..."
    pkill -f "remote-debugging-port=$DEBUG_PORT" 2>/dev/null || true
    sleep 1
fi

# Kill any running Comet instances to ensure clean start
echo "📋 Stopping any existing Comet instances..."
pkill -f "/Applications/Comet.app" 2>/dev/null || true
sleep 1

# Clean temp directory if using temp profile
if [ "$USE_TEMP_PROFILE" = "yes" ]; then
    echo "🧹 Cleaning temporary profile directory..."
    rm -rf "$USER_DATA_DIR"
    mkdir -p "$USER_DATA_DIR/$PROFILE_NAME"
fi

echo "🌐 Launching Comet Browser with remote debugging..."
/Applications/Comet.app/Contents/MacOS/Comet \
  --remote-debugging-port=$DEBUG_PORT \
  --remote-allow-origins=* \
  --user-data-dir="$USER_DATA_DIR" \
  --profile-directory="$PROFILE_NAME" \
  --no-first-run \
  --disable-default-apps \
  --disable-extensions-except \
  --disable-background-timer-throttling \
  --disable-renderer-backgrounding \
  --disable-backgrounding-occluded-windows \
  --disable-background-networking \
  --disable-sync &

COMET_PID=$!
sleep 2

# Verify Comet started
if ps -p $COMET_PID > /dev/null; then
    echo ""
    echo "✅ Comet Browser launched successfully!"
    echo "📍 DevTools Protocol: http://localhost:$DEBUG_PORT"
    echo "🔍 Inspect pages: http://localhost:$DEBUG_PORT/json"
    echo "🆔 Process ID: $COMET_PID"
    echo ""
    echo "💡 To use with chrome-devtools MCP server, configure:"
    echo "   \"args\": [\"-y\", \"chrome-devtools-mcp@latest\", \"--browserUrl\", \"http://127.0.0.1:$DEBUG_PORT\"]"
else
    echo "❌ Failed to launch Comet Browser"
    exit 1
fi
