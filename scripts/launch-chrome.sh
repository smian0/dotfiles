#!/bin/bash
# Chrome Launcher
# Usage: launch-chrome.sh [PROFILE_NAME] [enable-debug]
# Example: launch-chrome.sh "Profile 7"
# Example with debug: launch-chrome.sh "Profile 7" enable-debug

set -e

PROFILE_NAME="${1:-Profile 7}"
ENABLE_DEBUG="${2:-no}"
DEBUG_PORT="9222"
USER_DATA_DIR="$HOME/Library/Application Support/Google/Chrome"

echo "🔧 Chrome Launcher"
echo "=================="
echo "Profile: $PROFILE_NAME"
if [ "$ENABLE_DEBUG" = "enable-debug" ]; then
    echo "Debug Mode: ENABLED (port $DEBUG_PORT)"
else
    echo "Debug Mode: DISABLED (normal browser mode)"
fi
echo "User Data: $USER_DATA_DIR"
echo ""

# Kill any running Chrome instances to ensure clean start
if pgrep -f "Google Chrome" > /dev/null; then
    echo "📋 Stopping existing Chrome instances..."
    pkill -f "Google Chrome" 2>/dev/null || true
    sleep 1
fi

# Build launch command
LAUNCH_CMD="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
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

echo "🌐 Launching Chrome..."
"$LAUNCH_CMD" "${LAUNCH_ARGS[@]}" &

CHROME_PID=$!
sleep 2

# Verify Chrome started
if ps -p $CHROME_PID > /dev/null; then
    echo ""
    echo "✅ Chrome launched successfully!"
    echo "🆔 Process ID: $CHROME_PID"

    if [ "$ENABLE_DEBUG" = "enable-debug" ]; then
        echo "📍 DevTools Protocol: http://localhost:$DEBUG_PORT"
        echo "🔍 Inspect pages: http://localhost:$DEBUG_PORT/json"
        echo ""
        echo "💡 To use with chrome-devtools MCP:"
        echo "   \"args\": [\"-y\", \"chrome-devtools-mcp@latest\", \"--browserUrl\", \"http://127.0.0.1:$DEBUG_PORT\"]"
    fi
else
    echo "❌ Failed to launch Chrome"
    exit 1
fi
