#!/bin/bash
# Chrome Remote Debug Launcher Template
# Usage: launch-chrome-debug.sh [PROFILE_NAME] [DEBUG_PORT] [USER_DATA_DIR]
# Example: launch-chrome-debug.sh "Profile 7" 9222 /tmp/chrome-debug

set -e

PROFILE_NAME="${1:-Profile 7}"
DEBUG_PORT="${2:-9222}"
USER_DATA_DIR="${3:-/tmp/chrome-debug-minimal}"
ORIGINAL_PROFILE="$HOME/Library/Application Support/Google/Chrome/$PROFILE_NAME"

echo "🔧 Chrome Remote Debug Launcher"
echo "================================"
echo "Profile: $PROFILE_NAME"
echo "Port: $DEBUG_PORT"
echo "User Data: $USER_DATA_DIR"
echo ""

# Kill existing Chrome instances on this port
if lsof -Pi :$DEBUG_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $DEBUG_PORT is in use. Killing existing Chrome..."
    pkill -f "remote-debugging-port=$DEBUG_PORT" 2>/dev/null || true
    sleep 1
fi

# Clean and create temp directory
rm -rf "$USER_DATA_DIR"
mkdir -p "$USER_DATA_DIR/$PROFILE_NAME"

echo "📋 Copying profile data..."
# Copy essential profile files
if [ -d "$ORIGINAL_PROFILE" ]; then
    cp "$ORIGINAL_PROFILE/Preferences" "$USER_DATA_DIR/$PROFILE_NAME/" 2>/dev/null || true
    cp "$ORIGINAL_PROFILE/Bookmarks"* "$USER_DATA_DIR/$PROFILE_NAME/" 2>/dev/null || true
    cp "$ORIGINAL_PROFILE/Login Data"* "$USER_DATA_DIR/$PROFILE_NAME/" 2>/dev/null || true
    cp "$ORIGINAL_PROFILE/Cookies"* "$USER_DATA_DIR/$PROFILE_NAME/" 2>/dev/null || true

    # Copy extensions if they exist
    if [ -d "$ORIGINAL_PROFILE/Extensions" ]; then
        cp -r "$ORIGINAL_PROFILE/Extensions" "$USER_DATA_DIR/$PROFILE_NAME/" 2>/dev/null || true
    fi
else
    echo "⚠️  Original profile not found, creating fresh profile"
fi

echo "🌐 Launching Chrome with remote debugging..."
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
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

CHROME_PID=$!
sleep 2

# Verify Chrome started
if ps -p $CHROME_PID > /dev/null; then
    echo ""
    echo "✅ Chrome launched successfully!"
    echo "📍 DevTools Protocol: http://localhost:$DEBUG_PORT"
    echo "🔍 Inspect pages: http://localhost:$DEBUG_PORT/json"
    echo "🆔 Process ID: $CHROME_PID"
    echo ""
    echo "💡 To use with chrome-devtools MCP server, configure:"
    echo "   \"args\": [\"-y\", \"chrome-devtools-mcp@latest\", \"--browserUrl\", \"http://127.0.0.1:$DEBUG_PORT\"]"
else
    echo "❌ Failed to launch Chrome"
    exit 1
fi
