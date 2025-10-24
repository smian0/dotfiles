# Chrome Automation Quick Reference

One-page cheat sheet for Chrome automation with claude-devtools MCP server.

## Quick Setup (3 Steps)

```bash
# 1. Launch Chrome with debugging
./scripts/launch-chrome-debug.sh "Profile 7" 9222

# 2. Add to ~/.claude/.mcp.json
{
  "chrome-devtools": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9222"]
  }
}

# 3. Restart Claude Code
```

## Common Commands

### Launch & Verify
```bash
# Launch Chrome
./scripts/launch-chrome-debug.sh "Profile 7" 9222

# Check if running
curl -s http://localhost:9222/json | jq -r '.[0].title'

# List all pages
curl -s http://localhost:9222/json | jq -r '.[] | select(.type=="page") | .title'

# Kill Chrome
pkill -f "remote-debugging-port=9222"
```

### MCP Tools (Claude Code)
```javascript
// List pages
mcp__chrome-devtools__list_pages()

// Navigate
mcp__chrome-devtools__navigate_page({ url: "https://example.com" })

// Wait for element
mcp__chrome-devtools__wait_for({ text: "Expected Text", timeout: 10000 })

// Take snapshot
mcp__chrome-devtools__take_snapshot()

// Fill form
mcp__chrome-devtools__fill({ uid: "element_uid", value: "text" })

// Click button
mcp__chrome-devtools__click({ uid: "button_uid" })

// Execute JavaScript
mcp__chrome-devtools__evaluate_script({
  function: "() => document.title"
})

// Screenshot
mcp__chrome-devtools__take_screenshot({ fullPage: true, format: "png" })
```

## Perplexity Search Pattern

```javascript
// 1. Navigate
await mcp__chrome-devtools__navigate_page({ url: "https://www.perplexity.ai" });

// 2. Wait
await mcp__chrome-devtools__wait_for({ text: "Ask anything" });

// 3. Snapshot
const snap = await mcp__chrome-devtools__take_snapshot();
// Find textarea UID

// 4. Fill
await mcp__chrome-devtools__fill({ uid: "textarea_uid", value: "NVDA stock news" });

// 5. Submit
await mcp__chrome-devtools__click({ uid: "submit_uid" });

// 6. Wait for results
await mcp__chrome-devtools__wait_for({ text: "NVIDIA", timeout: 15000 });

// 7. Extract
const result = await mcp__chrome-devtools__evaluate_script({
  function: "() => document.body.innerText.substring(0, 2000)"
});
```

## Required Chrome Flags

```bash
--remote-debugging-port=9222      # Enable CDP
--remote-allow-origins=*          # Allow WebSocket connections
--user-data-dir=/tmp/chrome-debug # Isolated profile
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tools not available | Restart Claude Code |
| WebSocket 403 | Add `--remote-allow-origins=*` |
| Wrong Chrome | Check `--browserUrl` port |
| Form won't submit | Use `fill()` + `click()`, not just navigate |
| MCP changes ignored | Restart Claude Code |

## Common UIDs Pattern

After `take_snapshot()`, look for:
- Textbox/Textarea: `uid=X_Y textbox`
- Button: `uid=X_Y button`
- Link: `uid=X_Y link`

Use the UID number (e.g., `"7_62"`) in your calls.

## File Locations

```
~/dotfiles/scripts/launch-chrome-debug.sh    - Launch script
~/dotfiles/scripts/perplexity-search.sh      - Search script
~/.claude/.mcp.json                          - MCP config
~/dotfiles/docs/CHROME_AUTOMATION.md         - Full docs
```

## One-Liner Examples

```bash
# Quick search
./scripts/perplexity-search.sh "NVDA stock news"

# Check Chrome health
curl -s http://localhost:9222/json/version | jq

# Kill all debug Chrome
pkill -f "remote-debugging-port"

# Clean temp data
rm -rf /tmp/chrome-debug-*
```

## Security Checklist

- [ ] Use temp directory for `--user-data-dir`
- [ ] Never use `--remote-allow-origins=*` on public WiFi
- [ ] Kill Chrome when done
- [ ] Clean up temp directories
- [ ] Don't store passwords in automated sessions

## Slash Commands

```
/perplexity-search NVDA stock news
/perplexity-search latest AI developments
```

---

**For full documentation:** [CHROME_AUTOMATION.md](CHROME_AUTOMATION.md)

**Last Updated:** 2025-10-05
