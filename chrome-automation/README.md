# Chrome Automation Setup for Claude Code MCP

Background Chrome monitoring to maintain MCP connectivity with Claude Code.

## Problem Solved

When Chrome is closed, the Claude Code MCP server loses connection to the browser, breaking web automation capabilities. This setup ensures Chrome stays running automatically.

## Architecture

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

## How It Works

1. **chrome_keeper.sh**: Runs continuously, checking every 60 seconds if Chrome is running
2. **LaunchAgent**: Ensures chrome_keeper.sh starts automatically at login and restarts if it crashes
3. **chrome_commands.sh**: Provides easy management interface for the service

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

## Logs

- Service logs: `~/chrome_keeper.log`
- Error logs: `~/chrome_keeper.error.log`
- LaunchAgent logs: Available via `launchctl list | grep chrome`

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