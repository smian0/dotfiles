# Comet Browser Automation Setup

## Overview

Comet Browser is Perplexity's Chromium-based browser with built-in AI features. Since it's built on Chromium, it supports the Chrome DevTools Protocol (CDP), allowing full automation via the same MCP server used for Chrome.

## Quick Start

1. **Launch Comet with debugging:**
   ```bash
   bash ~/dotfiles/scripts/launch-comet-debug.sh "Profile 1" 9223 /tmp/comet-debug
   ```

2. **Restart Claude Code** to load the `comet-devtools` MCP server

3. **Use automation tools** via the `comet-devtools` server (same tools as `chrome-devtools`)

## Architecture

### Components

- **Comet Browser**: `/Applications/Comet.app` (Chromium-based, version 140.x)
- **Launch Script**: `~/dotfiles/scripts/launch-comet-debug.sh`
- **Debug Port**: 9223 (default, configurable)
- **MCP Server**: `comet-devtools` (using `chrome-devtools-mcp@latest`)
- **Slash Command**: `/launch-comet`

### How It Works

```
┌─────────────────────────────────────────────────────┐
│  Claude Code                                        │
│  ├─ MCP Server: comet-devtools                     │
│  │  └─ Protocol: Chrome DevTools Protocol (CDP)    │
│  └─ Tools: navigate, click, fill, screenshot, etc. │
└──────────────────┬──────────────────────────────────┘
                   │ WebSocket
                   ↓
┌─────────────────────────────────────────────────────┐
│  Comet Browser (Port 9223)                          │
│  ├─ Profile: Profile 1                              │
│  ├─ User Data: /tmp/comet-debug                     │
│  └─ CDP Endpoint: ws://127.0.0.1:9223/devtools/...  │
└─────────────────────────────────────────────────────┘
```

## Launch Script Details

### Basic Usage
```bash
launch-comet-debug.sh [PROFILE_NAME] [DEBUG_PORT] [USER_DATA_DIR]
```

### Examples
```bash
# Default: Profile 1 on port 9223
bash ~/dotfiles/scripts/launch-comet-debug.sh

# Custom profile and port
bash ~/dotfiles/scripts/launch-comet-debug.sh "Work Profile" 9224 /tmp/comet-work

# Multiple instances (different ports)
bash ~/dotfiles/scripts/launch-comet-debug.sh "Profile 1" 9223 /tmp/comet-1
bash ~/dotfiles/scripts/launch-comet-debug.sh "Profile 2" 9224 /tmp/comet-2
```

### What the Script Does

1. **Validates port availability** - Kills any existing process on the specified port
2. **Creates temporary profile** - Copies profile data to temp directory
3. **Launches Comet** with:
   - Remote debugging enabled (`--remote-debugging-port`)
   - Remote origins allowed (`--remote-allow-origins=*`)
   - Isolated user data directory
   - Background throttling disabled (for automation)
4. **Verifies launch** - Checks process and CDP endpoint

## MCP Server Configuration

### In `.mcp.json`
```json
{
  "mcpServers": {
    "comet-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9223"],
      "description": "Comet Browser (Perplexity) DevTools automation - connects to Comet Profile 1 on port 9223",
      "purpose": "browser-automation"
    }
  }
}
```

### Available Tools (via comet-devtools)

Same as Chrome DevTools MCP:

- **Navigation**: `navigate_page`, `navigate_page_history`, `new_page`, `close_page`
- **Interaction**: `click`, `fill`, `fill_form`, `hover`, `drag`, `upload_file`
- **Inspection**: `take_snapshot`, `take_screenshot`, `list_console_messages`
- **Network**: `list_network_requests`, `get_network_request`
- **Performance**: `performance_start_trace`, `performance_stop_trace`
- **Execution**: `evaluate_script`, `wait_for`
- **Emulation**: `emulate_cpu`, `emulate_network`, `resize_page`

## Usage Examples

### Example 1: Automated Perplexity Search
```markdown
Use comet-devtools to:
1. Navigate to perplexity.ai
2. Fill search box with "AI market trends 2025"
3. Click submit
4. Wait for results
5. Take screenshot
```

### Example 2: Multi-Tab Research
```markdown
Use comet-devtools to:
1. Open 3 new tabs
2. Navigate each to different research sources
3. Extract main content from each
4. Compile findings into summary
```

## Comparison: Comet vs Chrome

| Feature | Comet Browser | Chrome Browser |
|---------|---------------|----------------|
| **Base** | Chromium 140.x | Chrome/Chromium |
| **Debug Port** | 9223 (default) | 9222 (default) |
| **MCP Server** | `comet-devtools` | `chrome-devtools` |
| **Launch Script** | `launch-comet-debug.sh` | `launch-chrome-debug.sh` |
| **Profile Location** | `~/Library/Application Support/Comet/` | `~/Library/Application Support/Google/Chrome/` |
| **Special Features** | Perplexity AI integration | Standard Chrome features |
| **CDP Support** | ✅ Full | ✅ Full |
| **Extension Support** | ✅ Chrome extensions | ✅ Native |

## Perplexity Integration

Comet Browser has native Perplexity integration. You can automate Perplexity searches directly in Comet:

```markdown
Use comet-devtools to navigate to perplexity.ai and search for "quantum computing breakthroughs 2025"
```

This bypasses the need to use the regular `/perplexity` command (which uses Chrome).

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 9223
lsof -i :9223

# Kill process
pkill -f "remote-debugging-port=9223"

# Or use the script (it handles this automatically)
bash ~/dotfiles/scripts/launch-comet-debug.sh
```

### Comet Won't Launch
```bash
# Verify Comet is installed
ls /Applications/Comet.app

# Check version
/Applications/Comet.app/Contents/MacOS/Comet --version

# Try launching manually
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9223
```

### MCP Server Not Working
1. Ensure Comet is running with debugging enabled
2. Verify endpoint: `curl http://localhost:9223/json/version`
3. Restart Claude Code after modifying `.mcp.json`
4. Check MCP server logs in Claude Code output

### Profile Not Found
The script will create a fresh profile if the specified profile doesn't exist. To use an existing profile:

```bash
# List available profiles
ls ~/Library/Application\ Support/Comet/

# Launch with specific profile
bash ~/dotfiles/scripts/launch-comet-debug.sh "Default" 9223 /tmp/comet-debug
```

## Advanced Usage

### Running Multiple Comet Instances
```bash
# Instance 1: Research
bash ~/dotfiles/scripts/launch-comet-debug.sh "Research" 9223 /tmp/comet-research

# Instance 2: Testing
bash ~/dotfiles/scripts/launch-comet-debug.sh "Testing" 9224 /tmp/comet-testing
```

Update `.mcp.json` with multiple servers:
```json
{
  "comet-research": {
    "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9223"]
  },
  "comet-testing": {
    "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9224"]
  }
}
```

### Custom Chromium Flags
Edit `launch-comet-debug.sh` to add custom flags:

```bash
/Applications/Comet.app/Contents/MacOS/Comet \
  --remote-debugging-port=$DEBUG_PORT \
  --remote-allow-origins=* \
  --user-data-dir="$USER_DATA_DIR" \
  --profile-directory="$PROFILE_NAME" \
  --disable-gpu \              # Add custom flags here
  --headless=new \             # Run headless
  --window-size=1920,1080 &    # Set window size
```

## Security Considerations

### Remote Debugging Port
- **Local only**: Debug port (9223) is bound to localhost
- **No authentication**: Anyone with local access can control the browser
- **Temporary profiles**: Script uses isolated temp directories by default

### Best Practices
1. **Don't expose debug port** to network
2. **Use temporary profiles** for automation (default behavior)
3. **Kill processes** when done: `pkill -f "remote-debugging-port=9223"`
4. **Clean temp data**: `rm -rf /tmp/comet-debug*`

## Integration with Existing Workflows

### Use with /perplexity Command
Instead of Chrome + Perplexity.ai, you can use Comet's native integration:

```bash
# Old way (Chrome browser → perplexity.ai)
/perplexity "search query"

# New way (Comet browser with native Perplexity)
# Just use comet-devtools to interact with Perplexity features
```

### Switching Between Chrome and Comet
Both can run simultaneously on different ports:

- **Chrome**: Port 9222 via `chrome-devtools` MCP server
- **Comet**: Port 9223 via `comet-devtools` MCP server

Use the appropriate MCP server for each task.

## Reference

### Comet Browser Details
- **Developer**: Perplexity AI
- **Base**: Chromium 140.x
- **Platform**: macOS, Windows
- **Release**: July 2025
- **Website**: [Perplexity Comet](https://www.perplexity.ai/comet)

### Related Documentation
- [Chrome Automation Guide](./CHROME_AUTOMATION.md)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [MCP Server Documentation](https://github.com/ChromeDevTools/chrome-devtools-mcp)

---
**Last Updated**: 2025-10-05
