# Chrome Automation Setup Guide

This guide explains how to set up Chrome for automation using the chrome-devtools MCP server with Claude Code.

## Overview

The chrome-devtools MCP server allows Claude Code to control Chrome browser instances via the Chrome DevTools Protocol (CDP). This enables automated web browsing, testing, and data extraction.

## Prerequisites

- [x] Chrome installed at `/Applications/Google Chrome.app`
- [x] Port 9222 available (or choose another port)
- [x] Node.js and npm installed (for npx)
- [x] chrome-devtools-mcp package (auto-installed via npx)

## Quick Start

### 1. Launch Chrome with Remote Debugging

```bash
# Using the launch script (recommended)
./scripts/launch-chrome-debug.sh "Profile 7" 9222

# Or manually
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/chrome-debug \
  --profile-directory="Profile 7" &
```

### 2. Verify Chrome is Running

```bash
# Check if Chrome is listening on the debug port
curl -s http://localhost:9222/json | jq -r '.[0].title'

# List all open pages
curl -s http://localhost:9222/json | jq -r '.[] | select(.type=="page") | .title'
```

### 3. Configure MCP Server

Add to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--browserUrl",
        "http://127.0.0.1:9222"
      ],
      "description": "Chrome DevTools automation - connects to existing Chrome on port 9222",
      "purpose": "browser-automation"
    }
  }
}
```

**Important:** After adding or modifying the chrome-devtools configuration, restart Claude Code for changes to take effect.

### 4. Test Connection

Once Claude Code is restarted, test the connection:

```javascript
// List open pages
mcp__chrome-devtools__list_pages()

// Navigate to a URL
mcp__chrome-devtools__navigate_page({ url: "https://example.com" })

// Take a screenshot
mcp__chrome-devtools__take_screenshot()
```

## Configuration Reference

### Chrome Launch Flags

| Flag | Purpose | Required |
|------|---------|----------|
| `--remote-debugging-port=9222` | Enable CDP on port 9222 | ✅ Yes |
| `--remote-allow-origins=*` | Allow WebSocket connections | ✅ Yes |
| `--user-data-dir=/path` | Separate profile directory | ✅ Yes |
| `--profile-directory="Name"` | Use specific Chrome profile | Optional |
| `--no-first-run` | Skip first-run experience | Recommended |
| `--disable-sync` | Disable Chrome sync | Recommended |

### MCP Server Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--browserUrl` | Connect to existing Chrome | `http://127.0.0.1:9222` |
| `--executablePath` | Custom Chrome location | `/path/to/chrome` |
| `--headless` | Run without UI | `true` or `false` |
| `--channel` | Chrome channel | `stable`, `beta`, `dev`, `canary` |

## Common Use Cases

### Automated Web Search

```javascript
// Navigate to search engine
await mcp__chrome-devtools__navigate_page({ url: "https://www.perplexity.ai" });

// Wait for page to load
await mcp__chrome-devtools__wait_for({ text: "Ask anything" });

// Fill search box
const snapshot = await mcp__chrome-devtools__take_snapshot();
// Find the textarea UID from snapshot
await mcp__chrome-devtools__fill({ uid: "X_Y", value: "NVDA stock news" });

// Click submit
await mcp__chrome-devtools__click({ uid: "submit_button_uid" });

// Wait for results
await mcp__chrome-devtools__wait_for({ text: "NVIDIA", timeout: 15000 });
```

### Data Extraction

```javascript
// Execute JavaScript on the page
const result = await mcp__chrome-devtools__evaluate_script({
  function: "() => { return { title: document.title, text: document.body.innerText.substring(0, 1000) } }"
});
```

### Screenshot and Snapshot

```javascript
// Take full page screenshot
await mcp__chrome-devtools__take_screenshot({ fullPage: true, format: "png" });

// Get accessibility tree snapshot
const snapshot = await mcp__chrome-devtools__take_snapshot();
// Returns structured data with UIDs for each element
```

## Troubleshooting

### Issue: MCP Server Not Loading

**Symptoms:** chrome-devtools tools not available in Claude Code

**Solutions:**
1. Check `.mcp.json` syntax is valid JSON
2. Ensure `"type": "stdio"` is specified
3. Restart Claude Code after configuration changes
4. Check MCP server logs: `claude mcp list`

### Issue: WebSocket 403 Forbidden

**Symptoms:** Error connecting to Chrome DevTools Protocol

**Solution:** Add `--remote-allow-origins=*` flag to Chrome launch command

### Issue: Wrong Chrome Instance

**Symptoms:** Actions happening in different browser window

**Solution:**
1. Verify Chrome is running on expected port: `lsof -i :9222`
2. Check `--browserUrl` in `.mcp.json` matches Chrome's debug port
3. Only one Chrome instance should use port 9222

### Issue: Tools Not Available After Restart

**Symptoms:** chrome-devtools tools still missing

**Solutions:**
1. Verify MCP server process is running: `ps aux | grep chrome-devtools-mcp`
2. Check for errors in Claude Code console
3. Try removing and re-adding the MCP server configuration
4. Ensure chrome-devtools-mcp can be installed: `npx -y chrome-devtools-mcp@latest --help`

### Issue: Page Navigation Doesn't Submit Forms

**Symptoms:** Navigating to search URL doesn't trigger search

**Solution:** Use form automation:
1. Navigate to the page
2. Wait for elements to load
3. Fill form fields with `fill()`
4. Click submit button with `click()`

Don't rely on URL parameters alone - many modern web apps require actual UI interaction.

## Best Practices

### 1. Use Separate Profile Directory

Always use `--user-data-dir` with a temporary directory to avoid affecting your main Chrome profile:

```bash
--user-data-dir=/tmp/chrome-debug-minimal
```

### 2. Clean Up After Sessions

```bash
# Kill Chrome process
pkill -f "remote-debugging-port=9222"

# Clean temporary data
rm -rf /tmp/chrome-debug-minimal
```

### 3. Wait for Page Load

Always wait for page elements before interacting:

```javascript
await mcp__chrome-devtools__wait_for({ text: "Expected Text", timeout: 10000 });
```

### 4. Use Snapshots for Element Discovery

Take a snapshot first to find element UIDs:

```javascript
const snapshot = await mcp__chrome-devtools__take_snapshot();
// Inspect snapshot to find correct UID
await mcp__chrome-devtools__click({ uid: "found_uid" });
```

### 5. Handle Dynamic Content

For SPAs and dynamic sites, use multiple wait steps:

```javascript
// Wait for initial load
await wait_for({ text: "Main Content" });

// Wait after interaction
await click({ uid: "button_uid" });
await wait_for({ text: "New Content" });
```

## Security Considerations

- **Never run with `--remote-allow-origins=*` on public networks**
- Use isolated profile directories for automation
- Don't store sensitive data in automated Chrome sessions
- Kill Chrome instances when done: `pkill -f "remote-debugging-port=9222"`

## Advanced Configuration

### Multiple Chrome Instances

Run multiple Chrome instances on different ports:

```bash
# Instance 1: Personal browsing
./scripts/launch-chrome-debug.sh "Profile 1" 9222 /tmp/chrome-1

# Instance 2: Testing
./scripts/launch-chrome-debug.sh "Profile 2" 9223 /tmp/chrome-2
```

Configure multiple MCP servers:

```json
{
  "chrome-devtools-personal": {
    "args": ["chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9222"]
  },
  "chrome-devtools-testing": {
    "args": ["chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9223"]
  }
}
```

### Custom Chrome Path

For Chrome Beta, Canary, or custom installations:

```json
{
  "args": [
    "chrome-devtools-mcp@latest",
    "--executablePath", "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
    "--channel", "beta"
  ]
}
```

## References

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [chrome-devtools-mcp GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools)
- [MCP Server Documentation](https://modelcontextprotocol.io/)

## Quick Reference

### Common Commands

```bash
# Launch Chrome
./scripts/launch-chrome-debug.sh "Profile 7" 9222

# Check if running
curl -s http://localhost:9222/json

# Kill Chrome
pkill -f "remote-debugging-port=9222"

# Clean up
rm -rf /tmp/chrome-debug-minimal
```

### MCP Server Configuration

```json
{
  "chrome-devtools": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9222"]
  }
}
```

---

**Last Updated:** 2025-10-05
