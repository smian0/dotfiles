# Chrome Automation Setup for Claude Code MCP

This directory contains scripts and configuration for keeping Chrome running in the background to maintain MCP (Model Context Protocol) connectivity with Claude Code.

## Problem Solved

When Chrome is closed, the Claude Code MCP server loses connection to the browser, breaking web automation capabilities. This setup ensures Chrome stays running automatically.

## Files Overview

- `chrome_keeper.sh` - Background script that monitors and restarts Chrome
- `chrome_commands.sh` - Management interface for the Chrome keeper service
- `com.chrome.keeper.plist` - macOS LaunchAgent configuration for auto-startup
- `install.sh` - Automated installation script
- `uninstall.sh` - Clean removal script

## Quick Setup

```bash
# Run the installation script
./install.sh

# Check status
./chrome_commands.sh status

# View logs
./chrome_commands.sh logs
```

## Manual Setup

### 1. Install Scripts

```bash
# Copy chrome_keeper.sh to home directory and make executable
cp chrome_keeper.sh ~/chrome_keeper.sh
chmod +x ~/chrome_keeper.sh

# Copy chrome_commands.sh to home directory and make executable  
cp chrome_commands.sh ~/chrome_commands.sh
chmod +x ~/chrome_commands.sh
```

### 2. Install LaunchAgent

```bash
# Copy LaunchAgent to proper location
cp com.chrome.keeper.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.chrome.keeper.plist
```

### 3. Start Chrome Keeper

```bash
# Start the service
~/chrome_commands.sh start

# Verify it's running
~/chrome_commands.sh status
```

## Management Commands

```bash
# Start Chrome keeper service
~/chrome_commands.sh start

# Stop Chrome keeper service
~/chrome_commands.sh stop

# Check service status
~/chrome_commands.sh status

# View recent logs
~/chrome_commands.sh logs
```

## How It Works

1. **chrome_keeper.sh**: Runs continuously, checking every 60 seconds if Chrome is running
2. **LaunchAgent**: Ensures chrome_keeper.sh starts automatically at login and restarts if it crashes
3. **chrome_commands.sh**: Provides easy management interface for the service

## Logs

- Service logs: `~/chrome_keeper.log`
- Error logs: `~/chrome_keeper.error.log`
- LaunchAgent logs: Available via `launchctl list | grep chrome`

## Troubleshooting

### Chrome Keeper Not Starting

```bash
# Check if LaunchAgent is loaded
launchctl list | grep chrome

# Manually load if needed
launchctl load ~/Library/LaunchAgents/com.chrome.keeper.plist

# Check logs for errors
tail -f ~/chrome_keeper.error.log
```

### MCP Still Not Connecting

```bash
# Restart Claude Code after Chrome is running
# Close and reopen Claude Code application

# Or restart with specific MCP debug
claude --mcp-debug
```

### Chrome Opening Too Many Windows

The script only opens Chrome if it's completely closed. If you want to prevent multiple windows:

1. Set Chrome to restore tabs on startup
2. Or modify `chrome_keeper.sh` to use a specific Chrome profile

## Uninstallation

```bash
# Use the uninstall script
./uninstall.sh

# Or manually:
launchctl unload ~/Library/LaunchAgents/com.chrome.keeper.plist
rm ~/Library/LaunchAgents/com.chrome.keeper.plist
rm ~/chrome_keeper.sh ~/chrome_commands.sh
rm ~/chrome_keeper.log ~/chrome_keeper.error.log
```

## Integration with Dotfiles

This setup can be automatically installed as part of your dotfiles configuration:

```bash
# Add to your dotfiles install script
cd chrome-automation && ./install.sh
```

## Security Notes

- The script only monitors and starts Chrome, no data access
- LaunchAgent runs with user permissions only
- Logs contain only timestamp and status information
- No network connections made by the scripts themselves

---

*This setup ensures reliable Claude Code MCP connectivity for web automation tasks.*