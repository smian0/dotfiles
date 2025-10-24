#!/bin/bash
# Comet Browser Launcher
# Usage: launch-comet.sh [PROFILE_NAME] [enable-debug]
# Example: launch-comet.sh Default
# Example with debug: launch-comet.sh Default enable-debug

set -e

PROFILE_NAME="${1:-Default}"
ENABLE_DEBUG="${2:-no}"
DEBUG_PORT="9223"

USER_DATA_DIR="$HOME/Library/Application Support/Comet"

echo "🚀 Comet Browser Launcher"
echo "========================="
echo "Profile: $PROFILE_NAME"
if [ "$ENABLE_DEBUG" = "enable-debug" ]; then
    echo "Debug Mode: ENABLED (port $DEBUG_PORT)"
else
    echo "Debug Mode: DISABLED (normal browser mode)"
fi
echo "User Data: $USER_DATA_DIR"
echo ""

# Kill any running Comet instances to ensure clean start
if pgrep -f "/Applications/Comet.app" > /dev/null; then
    echo "📋 Stopping existing Comet instances..."
    pkill -f "/Applications/Comet.app" 2>/dev/null || true
    sleep 1
fi

# Build launch command
LAUNCH_CMD="/Applications/Comet.app/Contents/MacOS/Comet"
LAUNCH_ARGS=(
  "--user-data-dir=$USER_DATA_DIR"
  "--profile-directory=$PROFILE_NAME"
  "--no-first-run"
)

# Only add debug flags if explicitly requested
if [ "$ENABLE_DEBUG" = "enable-debug" ]; then
    echo "⚠️  Enabling remote debugging on port $DEBUG_PORT"
    LAUNCH_ARGS+=(
      "--remote-debugging-port=$DEBUG_PORT"
      "--remote-allow-origins=*"
      "--disable-background-timer-throttling"
      "--disable-renderer-backgrounding"
      "--disable-backgrounding-occluded-windows"
    )
fi

echo "🌐 Launching Comet Browser..."
"$LAUNCH_CMD" "${LAUNCH_ARGS[@]}" &

COMET_PID=$!
sleep 2

# Verify Comet started
if ps -p $COMET_PID > /dev/null; then
    echo ""
    echo "✅ Comet Browser launched successfully!"
    echo "🆔 Process ID: $COMET_PID"

    if [ "$ENABLE_DEBUG" = "enable-debug" ]; then
        echo "📍 DevTools Protocol: http://localhost:$DEBUG_PORT"
        echo "🔍 Inspect pages: http://localhost:$DEBUG_PORT/json"
        echo ""
        echo "💡 To use with chrome-devtools MCP:"
        echo "   \"args\": [\"-y\", \"chrome-devtools-mcp@latest\", \"--browserUrl\", \"http://127.0.0.1:$DEBUG_PORT\"]"
    fi
else
    echo "❌ Failed to launch Comet Browser"
    exit 1
fi
