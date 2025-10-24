# Workflow: Add MCP Server

**Purpose**: Install and configure a new MCP server at user or project level

**Pattern**: User wants to add a new MCP server to their configuration

## Trigger Conditions

✅ This workflow activates when:
- User asks to add/install a new MCP server
- User provides server name, command, and arguments
- User wants to configure a new tool integration

## Execution Steps

**Step 1: Determine scope**

Choose configuration level:
- **User-level** (`~/.claude/.mcp.json`): Development tools available everywhere (serena, context7, zen)
- **Project-level** (`<project>/.mcp.json`): Team-shared project integrations (APIs, databases)

**Step 2: Add server definition to `.mcp.json`**

Edit the appropriate `.mcp.json` file:

**User-level:**
```bash
vim ~/.claude/.mcp.json
```

**Project-level:**
```bash
vim .mcp.json
# or
vim .claude/.mcp.json  # For private project servers
```

**Add server entry:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"],
      "type": "stdio",
      "description": "My custom MCP server",
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**Common command patterns:**

**NPX package:**
```json
{
  "command": "npx",
  "args": ["-y", "package-name"]
}
```

**Python script:**
```json
{
  "command": "python3",
  "args": ["path/to/server.py"]
}
```

**Python with uvx:**
```json
{
  "command": "uvx",
  "args": ["my-python-mcp-server"]
}
```

**Node.js script:**
```json
{
  "command": "node",
  "args": ["path/to/server.js"]
}
```

**Step 3: Add tool permissions to `settings.json`**

Edit the corresponding `settings.json`:

**User-level:**
```bash
vim ~/.claude/settings.json
```

**Project-level:**
```bash
vim .claude/settings.json
```

**Add permissions:**
```json
{
  "permissions": {
    "allow": [
      "mcp__my-server__tool1",
      "mcp__my-server__tool2",
      "mcp__my-server__*"
    ]
  }
}
```

**Permission naming convention:** `mcp__<server-name>__<tool-name>`

**Step 4: Validate configuration**

```bash
# Validate JSON syntax
jq . ~/.claude/.mcp.json

# Run consistency check
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
```

Expected: No errors, configuration valid.

**Step 5: Register server (user-level only)**

**If user-level:**
```bash
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
```

**If project-level:** Skip this step (Claude Code loads automatically)

**Step 6: Restart Claude Code**

Restart Claude Code completely (not just reload window).

**Step 7: Verify server is connected**

```bash
claude mcp list | grep my-server
```

Expected: Server appears with "✔ connected" status.

**Step 8: Test server functionality**

Try using one of the server's tools in Claude Code to verify it works.

**Step 9: Commit to version control**

**User-level:**
```bash
cd ~/dotfiles
git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "feat: add my-server MCP integration"
```

**Project-level:**
```bash
git add .mcp.json .claude/settings.json
git commit -m "feat: add my-server MCP integration"
```

## Alternative: Interactive Script

Use the interactive add script for guided setup:

```bash
~/.claude/skills/mcp-manager/scripts/add-mcp-server.sh
```

**Prompts:**
1. Server name
2. Command (npx, uvx, node, python3)
3. Arguments
4. Description
5. Environment variables
6. Scope (user or project)

**Script automatically:**
- Validates server name uniqueness
- Adds to `.mcp.json`
- Creates permission placeholders in `settings.json`
- Validates final configuration

## Integration with Main Skill

**Before adding (see main skill):**
- Best Practices: Choosing user vs project scope
- Configuration Files: Understanding `.mcp.json` structure
- Environment Variables: How to use ${VAR} syntax

**After adding (see main skill):**
- Sync workflow: Registering user-level servers
- Validate workflow: Checking configuration consistency
- Troubleshooting: Common server loading issues

## Error Handling

**JSON syntax error:**
- Fix syntax: `jq . ~/.claude/.mcp.json`
- Common issues: Missing commas, trailing commas, unquoted keys

**Server name conflict:**
- Choose unique name
- Check existing servers: `jq -r '.mcpServers | keys[]' ~/.claude/.mcp.json`

**Command not found:**
- Verify command exists: `which npx` or `which python3`
- Install if missing: `npm install -g npx` or `brew install python3`

**Server not connecting:**
- Check Claude Code logs: `~/.claude/logs/mcp-*.log`
- Test command manually: `npx -y package-name --help`
- Verify environment variables are set
- See main skill troubleshooting section

## Example: Adding Context7 Server

```bash
# 1. Add to user manifest
jq '.mcpServers["context7"] = {
  "command": "npx",
  "args": ["-y", "@context7/mcp-server"],
  "type": "stdio",
  "description": "Library documentation lookup"
}' ~/.claude/.mcp.json | sponge ~/.claude/.mcp.json

# 2. Add permissions
jq '.permissions.allow += [
  "mcp__context7__resolve-library-id",
  "mcp__context7__get-library-docs"
]' ~/.claude/settings.json | sponge ~/.claude/settings.json

# 3. Validate
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh

# 4. Sync
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh

# 5. Restart Claude Code

# 6. Verify
claude mcp list | grep context7
# Expected: context7  ✔ connected

# 7. Commit
cd ~/dotfiles && git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "feat: add context7 MCP server for documentation lookup"
```

## Checklist

**Before adding:**
- [ ] Server name is unique
- [ ] Command exists and is accessible
- [ ] Required API keys/credentials ready
- [ ] Decided on user vs project scope

**After adding:**
- [ ] JSON syntax validated
- [ ] Permissions added for all tools
- [ ] Configuration consistency checked
- [ ] Server registered (if user-level)
- [ ] Claude Code restarted
- [ ] Server shows as connected
- [ ] Tool functionality tested
- [ ] Changes committed to git
