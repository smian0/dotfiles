#!/bin/bash
# Chrome Management Commands

case "$1" in
    "start")
        echo "Starting Chrome Keeper service..."
        launchctl load /Users/smian/Library/LaunchAgents/com.chrome.keeper.plist
        echo "Chrome Keeper started!"
        ;;
    "stop")
        echo "Stopping Chrome Keeper service..."
        launchctl unload /Users/smian/Library/LaunchAgents/com.chrome.keeper.plist
        echo "Chrome Keeper stopped!"
        ;;
    "status")
        echo "Chrome Keeper Status:"
        if launchctl list | grep -q "com.chrome.keeper"; then
            echo "✅ Chrome Keeper is running"
            launchctl list | grep chrome
        else
            echo "❌ Chrome Keeper is not running"
        fi
        echo ""
        echo "Chrome Process Status:"
        if pgrep -f "Google Chrome" > /dev/null; then
            echo "✅ Chrome is running"
        else
            echo "❌ Chrome is not running"
        fi
        ;;
    "logs")
        echo "Chrome Keeper Logs:"
        if [ -f "/Users/smian/chrome_keeper.log" ]; then
            tail -20 /Users/smian/chrome_keeper.log
        else
            echo "No logs found yet"
        fi
        ;;
    *)
        echo "Chrome Management Commands:"
        echo "  ./chrome_commands.sh start   - Start Chrome keeper"
        echo "  ./chrome_commands.sh stop    - Stop Chrome keeper" 
        echo "  ./chrome_commands.sh status  - Check status"
        echo "  ./chrome_commands.sh logs    - View logs"
        ;;
esac