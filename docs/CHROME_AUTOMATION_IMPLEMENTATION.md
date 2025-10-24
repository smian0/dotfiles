# Chrome Automation Implementation Summary

**Date:** 2025-10-05
**Purpose:** Document the Chrome automation setup and learnings from implementing Perplexity search automation

## What Was Implemented

### 1. Scripts

#### `scripts/launch-chrome-debug.sh`
Generic Chrome launcher with remote debugging support.

**Location:** `/Users/smian/dotfiles/scripts/launch-chrome-debug.sh`

**Features:**
- Configurable profile, port, and data directory
- Automatic profile data copying
- Process verification and status reporting
- Security flags pre-configured
- MCP server configuration helper output

**Usage:**
```bash
./scripts/launch-chrome-debug.sh "Profile 7" 9222
```

#### `scripts/perplexity-search.sh`
Automated Perplexity AI search via Chrome DevTools Protocol.

**Location:** `/Users/smian/dotfiles/scripts/perplexity-search.sh`

**Features:**
- Direct CDP WebSocket communication
- Automated form filling and submission
- Result extraction and display
- Error handling and status reporting

**Usage:**
```bash
./scripts/perplexity-search.sh "NVDA stock news"
```

### 2. Documentation

#### `docs/CHROME_AUTOMATION.md`
Comprehensive guide covering setup, configuration, troubleshooting, and best practices.

**Sections:**
- Quick Start guide
- Configuration reference (Chrome flags, MCP arguments)
- Common use cases with code examples
- Troubleshooting guide with solutions
- Security considerations
- Advanced configuration options

#### `scripts/README.md`
Updated to include Chrome automation scripts with usage examples.

### 3. Slash Command

#### `claude/.claude/commands/perplexity-search.md`
Claude Code slash command for Perplexity searches.

**Command:** `/perplexity-search <query>`

**Features:**
- Step-by-step automation instructions
- Error handling procedures
- Output formatting guidelines
- Usage examples

### 4. Updated Files

#### `Desktop/Chrome-Profile7-Minimal.command`
Enhanced with:
- Process ID tracking
- Startup verification
- MCP configuration hints
- Better error reporting

## Key Learnings

### Issue #1: Configuration File Location
**Problem:** Editing wrong `.mcp.json` file
**Root Cause:** Multiple MCP config files (global vs project-level)
**Solution:** Always check which file Claude Code actually loads
- Global: `~/.claude/.mcp.json`
- Project: `<project>/.mcp.json`

**Lesson:** Verify configuration file location before editing

### Issue #2: MCP Server Connection
**Problem:** chrome-devtools MCP server not connecting to existing Chrome
**Root Cause:** Missing `--browserUrl` argument
**Solution:** Add to MCP server configuration:
```json
"args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9222"]
```

**Lesson:** chrome-devtools server launches its own Chrome by default; use `--browserUrl` to connect to existing instance

### Issue #3: WebSocket Connection Refused
**Problem:** CDP WebSocket connections failing with 403 Forbidden
**Root Cause:** Chrome missing `--remote-allow-origins=*` flag
**Solution:** Add flag to Chrome launch command
```bash
--remote-allow-origins=*
```

**Lesson:** Chrome's CDP requires explicit permission for WebSocket origins

### Issue #4: Page Navigation vs. Form Submission
**Problem:** Navigating to Perplexity search URL doesn't trigger search
**Root Cause:** Modern web apps require actual UI interaction
**Solution:** Proper automation flow:
1. Navigate to homepage
2. Wait for page load
3. Fill form fields
4. Click submit button
5. Wait for results

**Lesson:** URL parameters alone don't work for SPAs; must interact with actual UI elements

### Issue #5: MCP Server Restart Required
**Problem:** Configuration changes not taking effect
**Root Cause:** Changes to `.mcp.json` require Claude Code restart
**Solution:** Always restart Claude Code after modifying `.mcp.json`

**Lesson:** MCP server configuration is loaded at Claude Code startup

## Codified Patterns

### Pattern 1: Chrome Launch for Automation
```bash
#!/bin/bash
# Standard Chrome debug launch pattern
PROFILE="${1:-Profile 7}"
PORT="${2:-9222}"
DATA_DIR="${3:-/tmp/chrome-debug}"

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=$PORT \
  --remote-allow-origins=* \
  --user-data-dir="$DATA_DIR" \
  --profile-directory="$PROFILE" \
  --no-first-run \
  --disable-sync &
```

### Pattern 2: MCP Server Configuration
```json
{
  "chrome-devtools": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9222"],
    "description": "Chrome automation - connects to existing Chrome on port 9222"
  }
}
```

### Pattern 3: Web Form Automation
```javascript
// 1. Navigate
await navigate({ url: "https://example.com" });

// 2. Wait for load
await wait_for({ text: "Expected Element" });

// 3. Get snapshot to find elements
const snapshot = await take_snapshot();

// 4. Fill form
await fill({ uid: "input_uid", value: "search query" });

// 5. Submit
await click({ uid: "submit_uid" });

// 6. Wait for results
await wait_for({ text: "Results", timeout: 15000 });

// 7. Extract data
const result = await evaluate_script({
  function: "() => document.body.innerText"
});
```

### Pattern 4: CDP WebSocket Communication
```python
import websocket
import urllib.request
import json

# Get WebSocket URL
response = urllib.request.urlopen('http://localhost:9222/json')
pages = json.loads(response.read())
ws_url = pages[0]['webSocketDebuggerUrl']

# Connect
ws = websocket.create_connection(ws_url)

# Send command
cmd = {"id": 1, "method": "Page.navigate", "params": {"url": "https://example.com"}}
ws.send(json.dumps(cmd))

# Receive response
result = json.loads(ws.recv())
```

## File Structure

```
dotfiles/
├── scripts/
│   ├── launch-chrome-debug.sh          # Generic Chrome launcher
│   ├── perplexity-search.sh            # Automated Perplexity search
│   └── README.md                        # Updated with Chrome scripts
├── docs/
│   ├── CHROME_AUTOMATION.md             # Comprehensive guide
│   └── CHROME_AUTOMATION_IMPLEMENTATION.md  # This file
├── claude/.claude/
│   └── commands/
│       └── perplexity-search.md         # Slash command definition
└── Desktop/
    └── Chrome-Profile7-Minimal.command  # Enhanced launcher
```

## Testing Checklist

- [x] Chrome launches with correct flags
- [x] CDP accessible on port 9222
- [x] MCP server connects to Chrome
- [x] chrome-devtools tools available in Claude Code
- [x] Navigation works
- [x] Form filling works
- [x] Submit button clicking works
- [x] Result extraction works
- [x] Perplexity search end-to-end successful

## Future Enhancements

### Potential Improvements
1. **Error Recovery:** Automatic retry logic for failed automations
2. **Multi-Site Support:** Generalized search automation for Google, Bing, etc.
3. **Screenshot Comparison:** Visual regression testing capabilities
4. **Proxy Support:** Route traffic through proxy servers
5. **Session Recording:** Record and replay browser sessions
6. **Performance Metrics:** Collect timing data for optimizations

### Additional Scripts to Consider
- `google-search.sh` - Google search automation
- `linkedin-search.sh` - LinkedIn profile searches
- `screenshot-compare.sh` - Visual diff tool
- `chrome-cleanup.sh` - Kill all debug instances and clean temp data

## Security Reminders

⚠️ **Critical Security Points:**

1. Never use `--remote-allow-origins=*` on:
   - Public WiFi networks
   - Production environments
   - Shared machines

2. Always use isolated profile directories:
   - Use `/tmp/` or similar temporary locations
   - Never point to your actual Chrome profile
   - Clean up after use

3. Don't store sensitive data in automated sessions:
   - No passwords
   - No API keys
   - No personal information

4. Kill Chrome when done:
   ```bash
   pkill -f "remote-debugging-port=9222"
   rm -rf /tmp/chrome-debug-*
   ```

## References

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [chrome-devtools-mcp GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools)
- [websocket-client docs](https://websocket-client.readthedocs.io/)
- [MCP Specification](https://modelcontextprotocol.io/)

---

**Success Criteria Met:**
- ✅ Chrome automation working end-to-end
- ✅ Scripts created and documented
- ✅ Patterns codified for reuse
- ✅ Troubleshooting guide complete
- ✅ Security considerations documented

**Next Steps:**
1. Test automation on different websites
2. Create additional automation scripts
3. Integrate with CI/CD if needed
4. Share learnings with team/community
