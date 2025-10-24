# Comet Browser Automation Testing Guide

## Current Status

✅ **Completed:**
- Comet launch script created and tested
- MCP server configuration added (`comet-devtools`)
- Comet running successfully on port 9223
- Chrome DevTools Protocol endpoint verified working
- Connection to Comet confirmed (17 tabs open, including Perplexity pages)

⚠️ **Issue Identified:**
The `comet-devtools` MCP server is configured in `.mcp.json` but tools are not appearing in Claude Code's available tools list. This requires investigation.

## Why Comet Automation Isn't Working Yet

### Root Cause
When Claude Code loads MCP servers from `.mcp.json`, it creates tool namespaces like `mcp__<server-name>__<tool-name>`. For example:
- `chrome-devtools` server creates tools: `mcp__chrome-devtools__navigate_page`, `mcp__chrome-devtools__click`, etc.
- `comet-devtools` server *should* create: `mcp__comet-devtools__navigate_page`, `mcp__comet-devtools__click`, etc.

However, the `comet-devtools` tools are not appearing in the available tools list after restart.

### Possible Causes
1. **MCP server failed to start**: The comet-devtools server may have failed to initialize
2. **Tool namespace collision**: Both servers use the same `chrome-devtools-mcp` package
3. **Configuration issue**: The server configuration may need additional parameters

## Verification Steps

### 1. Verify Comet Is Running
```bash
curl -s http://localhost:9223/json/version | jq '.Browser'
# Should output: "Chrome/140.1.7339.21337"
```

### 2. Check MCP Server Configuration
```bash
cat ~/.claude/.mcp.json | jq '.mcpServers["comet-devtools"]'
# Should show configuration with port 9223
```

### 3. Test Direct CDP Connection
```bash
python3 ~/dotfiles/scripts/comet-perplexity-search.py "test query"
# Should list open tabs and confirm connection
```

## Workaround Solutions

### Option 1: Temporary Port Switch (Current Method)
Temporarily point `chrome-devtools` to port 9223 (Comet) instead of 9222 (Chrome):

```bash
# Edit ~/.claude/.mcp.json
# Change chrome-devtools args to: ["http://127.0.0.1:9223"]
# Restart Claude Code
```

**Pros:** Immediate access to Comet automation
**Cons:** Loses Chrome automation, requires restart

### Option 2: Use Python Script
Use the direct CDP automation script:

```bash
python3 ~/dotfiles/scripts/comet-perplexity-search.py "your search query"
```

**Pros:** Works immediately, no restart needed
**Cons:** Limited functionality, not integrated with Claude Code

### Option 3: Chrome Extension Approach
Control Comet via the existing `/perplexity` command (which uses Chrome to access perplexity.ai):

```
/perplexity "your search query"
```

**Pros:** Works now
**Cons:** Uses Chrome, not Comet; doesn't test Comet integration

## Recommended Next Steps

### Short Term: Test with Port Switch
1. Edit `~/.claude/.mcp.json`:
   ```json
   "chrome-devtools": {
     "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", "http://127.0.0.1:9223"]
   }
   ```

2. **Fully restart Claude Code** (quit and reopen)

3. Test automation:
   ```
   Use chrome-devtools to navigate to perplexity.ai and search for "AI developments"
   ```

4. Verify it's using Comet (check that it shows your existing Comet tabs)

### Medium Term: Debug comet-devtools Server
1. Check Claude Code MCP server logs
2. Verify both servers can coexist
3. Test if renaming the server helps (e.g., `comet-browser` instead of `comet-devtools`)

### Long Term: Ideal Solution
Create a unified browser automation command that can switch between Chrome and Comet:

```bash
# Proposed slash command: /browser-automation
/browser-automation --browser=comet --action="search perplexity for AI news"
/browser-automation --browser=chrome --action="navigate to github.com"
```

## Testing Checklist

When testing Comet automation:

- [ ] Comet is running on port 9223
  ```bash
  lsof -i :9223
  ```

- [ ] DevTools endpoint is accessible
  ```bash
  curl http://localhost:9223/json/version
  ```

- [ ] MCP server configuration exists
  ```bash
  cat ~/.claude/.mcp.json | grep -A5 comet-devtools
  ```

- [ ] Claude Code has been **fully restarted** (quit + reopen)

- [ ] MCP tools are available
  - Check for `mcp__comet-devtools__*` tools in Claude Code
  - Or temporarily use `mcp__chrome-devtools__*` with port 9223

- [ ] Can list pages in Comet
  ```
  Use chrome-devtools to list all pages
  ```

- [ ] Can navigate in Comet
  ```
  Use chrome-devtools to navigate to perplexity.ai
  ```

- [ ] Can perform Perplexity search
  ```
  Use chrome-devtools to search Perplexity for "test query"
  ```

## Example Test Session

After proper setup, this should work:

```markdown
**User:** Use comet-devtools to search Perplexity for "quantum computing breakthroughs 2025"

**Claude:**
1. Lists pages in Comet browser
2. Navigates to https://www.perplexity.ai
3. Fills in search box with query
4. Submits search
5. Waits for results
6. Takes snapshot of results
7. Extracts and presents key findings
```

## Current Limitations

1. **MCP Server Not Loading**: comet-devtools tools not appearing
2. **Single Server Constraint**: Can't use both chrome-devtools and comet-devtools simultaneously
3. **Restart Required**: Every .mcp.json change requires full Claude Code restart
4. **No Persistent State**: Each restart loses browser context

## Files Created

- `/Users/smian/dotfiles/scripts/launch-comet-debug.sh` - Comet launcher
- `/Users/smian/dotfiles/scripts/comet-perplexity-search.py` - Direct CDP test script
- `/Users/smian/dotfiles/claude/.claude/commands/launch-comet.md` - Slash command
- `/Users/smian/dotfiles/docs/COMET_BROWSER_AUTOMATION.md` - Full documentation
- `/Users/smian/dotfiles/docs/COMET_BROWSER_TESTING.md` - This file

## Investigation Needed

To resolve the MCP server loading issue:

1. **Check MCP server startup logs**
   - Look for errors when comet-devtools initializes
   - Compare with successful chrome-devtools startup

2. **Test server isolation**
   - Try disabling chrome-devtools temporarily
   - See if comet-devtools tools appear

3. **Verify package behavior**
   - Check if `chrome-devtools-mcp` supports multiple instances
   - Review package documentation for multi-instance setup

4. **Alternative configuration**
   - Try different server names
   - Test with different browserUrl formats
   - Add additional environment variables

---
**Status**: Investigation ongoing - Comet browser confirmed working, MCP integration pending
**Last Updated**: 2025-10-05
