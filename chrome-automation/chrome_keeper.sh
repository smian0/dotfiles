#!/bin/bash
# Chrome Keeper - Ensures Chrome stays running for MCP extension

echo "Starting Chrome Keeper..."
echo "This script will keep Chrome running in the background for MCP"

while true; do
    # Check if Chrome is running
    if ! pgrep -f "Google Chrome" > /dev/null; then
        echo "$(date): Chrome not running, starting..."
        open -a "Google Chrome"
        sleep 10  # Give Chrome time to fully start
        echo "$(date): Chrome restarted"
    fi
    
    # Check every 60 seconds
    sleep 60
done