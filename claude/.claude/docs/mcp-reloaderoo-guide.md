# MCP Development with Reloaderoo Integration Guide

## Overview

This guide explains how to use Reloaderoo with MCP (Model Context Protocol) server development in your dotfiles environment. Reloaderoo provides hot-reloading and CLI testing capabilities that significantly improve the MCP development workflow.

## What is Reloaderoo?

Reloaderoo is a powerful MCP debugging and development tool with two primary modes:

1. **CLI Mode**: Direct command-line testing of MCP servers without complex client setup
2. **Proxy Mode**: Hot-reload development with transparent proxy for AI clients

## Quick Start

### Install and Setup Hot-Reload for Existing MCP Servers

```bash
# Automatically wrap all MCP servers with hot-reload capability
mcp-hotreload ~/.claude/.mcp.json

# Preview changes before applying
mcp-hotreload --dry-run ~/.claude/.mcp.json

# Get help
mcp-hotreload --help
```

This will automatically install reloaderoo if needed and configure your MCP servers for hot-reload development.

### CLI Development and Testing

```bash
# Test any MCP server directly
mcp-dev test /path/to/server.py

# Start development proxy with hot-reload
mcp-dev proxy /path/to/server.py

# Call specific tools via CLI
mcp-dev call tell_joke '{"prompt":"dad joke"}' /path/to/server.py

# Get server information
mcp-dev inspect /path/to/server.py
```

## Global Commands

The dotfiles environment provides two global commands for MCP development:

### `mcp-hotreload` - Production Hot-Reload Setup

Automatically configures Claude Code's `.mcp.json` files for hot-reload development:

```bash
# Configure all MCP servers for hot-reload
mcp-hotreload ~/.claude/.mcp.json

# Preview what would be changed
mcp-hotreload --dry-run .mcp.json

# Works with any .mcp.json file
mcp-hotreload /path/to/project/.mcp.json
```

**What it does:**
- Wraps existing MCP server commands with reloaderoo proxy
- Preserves all existing environment variables
- Only processes stdio servers (skips HTTP servers)
- Creates automatic backups
- Installs reloaderoo if missing (with user confirmation)

### `mcp-dev` - CLI Development and Testing

Direct command-line interaction with MCP servers:

```bash
# Test server tools and functionality
mcp-dev test /path/to/server.py

# Start development proxy with hot-reload
mcp-dev proxy /path/to/server.py

# Call specific tools directly
mcp-dev call tool_name '{"param":"value"}' /path/to/server.py

# Get server information and capabilities
mcp-dev inspect /path/to/server.py

# Show help
mcp-dev help
```

## Development Workflow

### 1. Setup Hot-Reload for Claude Code

```bash
# Configure your MCP servers for hot-reload
mcp-hotreload ~/.claude/.mcp.json

# Restart Claude Code to load new configuration
```

### 2. Development with Hot-Reload

```bash
# Make changes to your MCP server code
vim /path/to/your_server.py

# In Claude Code, use the restart_server tool instead of restarting Claude
# Changes will be picked up immediately!
```

### 3. CLI Testing During Development

```bash
# Test your server directly from command line
mcp-dev test /path/to/your_server.py

# Call specific tools to debug
mcp-dev call your_tool '{"param":"value"}' /path/to/your_server.py
```

## Configuration Examples

### Before Hot-Reload Setup

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python3",
      "args": ["server.py"],
      "type": "stdio",
      "env": {
        "GITHUB_TOKEN": "token-value",
        "CUSTOM_VAR": "custom-value"
      }
    }
  }
}
```

### After Hot-Reload Setup (Automatic)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": [
        "reloaderoo",
        "proxy",
        "--",
        "python3",
        "server.py"
      ],
      "type": "stdio",
      "env": {
        "GITHUB_TOKEN": "token-value",
        "CUSTOM_VAR": "custom-value",
        "MCPDEV_PROXY_AUTO_RESTART": "true"
      }
    }
  }
}
```

**Note:** All existing environment variables are preserved automatically.

## Language Support

### Python MCP Servers
```bash
# Direct Python
mcp-dev test /path/to/server.py
mcp-hotreload config.json  # Wraps: python3 server.py

# uv-based servers
mcp-dev test uv run --script /path/to/server.py

# uvx-based servers
mcp-dev test uvx --from git+https://repo package start-server
```

### Node.js MCP Servers
```bash
# Node.js servers
mcp-dev test /path/to/server.js
mcp-hotreload config.json  # Wraps: node server.js

# npm/npx servers
mcp-dev test npx your-mcp-server
```

### Any Command
```bash
# Works with any command that starts an MCP server
mcp-dev test deno run --allow-all server.ts
mcp-dev test ./my-custom-server
```

## Environment Variables

Configure Reloaderoo behavior with environment variables:

```bash
export MCPDEV_LOG_LEVEL=debug        # Set log level
export MCPDEV_AUTO_RESTART=true      # Enable auto-restart
export MCPDEV_PROXY_TIMEOUT=30000    # Set timeout (ms)
```

## Advanced Usage

### Multiple Server Development

```bash
# Configure different projects
mcp-hotreload ~/project1/.mcp.json
mcp-hotreload ~/project2/.mcp.json

# Test multiple servers
mcp-dev test /path/to/server1.py &
mcp-dev test /path/to/server2.py &
```

### Custom Environment Variables

The `mcp-hotreload` tool preserves any existing environment variables:

```json
{
  "mcpServers": {
    "my-server": {
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "CUSTOM_DATABASE_URL": "postgres://...",
        "DEBUG_MODE": "true"
      }
    }
  }
}
```

After running `mcp-hotreload`, all these variables remain intact with only `MCPDEV_PROXY_AUTO_RESTART` added.

### Integration with CI/CD

```bash
# Add to your testing pipeline
mcp-dev test /path/to/server.py

# Or test multiple servers
for server in servers/*.py; do
  mcp-dev test "$server" || exit 1
done
```

## Troubleshooting

### Common Issues

**1. Server not starting**
```bash
# Check if server runs directly first
/path/to/your_server.py --help

# Test with mcp-dev
mcp-dev test /path/to/your_server.py

# Check reloaderoo installation
npx reloaderoo --version
```

**2. Hot-reload not working in Claude Code**
- Ensure you used `mcp-hotreload` to configure your `.mcp.json`
- Restart Claude Code after configuration changes
- Use `restart_server` tool instead of restarting Claude Code for code changes

**3. Tool calls failing**
```bash
# Test with CLI first
mcp-dev inspect /path/to/server.py
mcp-dev call tool_name '{"param":"value"}' /path/to/server.py
```

**4. Dependencies missing**
```bash
# mcp-hotreload will check and install reloaderoo automatically
# For manual installation:
npm install -g reloaderoo

# Check if jq is installed
which jq || brew install jq
```

### Debugging

**Enable verbose logging:**
```bash
# Set debug log level
MCPDEV_LOG_LEVEL=debug mcp-dev proxy /path/to/server.py
```

**Direct reloaderoo commands:**
```bash
# List tools available in a server
npx reloaderoo inspect list-tools -- /path/to/server.py

# Call a specific tool
npx reloaderoo inspect call-tool tool_name --params '{"param":"value"}' -- /path/to/server.py

# Start proxy mode with hot-reload
npx reloaderoo proxy --auto-restart -- /path/to/server.py
```

## Best Practices

1. **Use `mcp-hotreload` for production setup**: Configure your `.mcp.json` files once
2. **Use `mcp-dev` for development testing**: Quick CLI testing and debugging
3. **Always test directly first**: Verify your server works with `mcp-dev test`
4. **Use `restart_server` tool**: Never restart Claude Code for code changes
5. **Preserve environment variables**: `mcp-hotreload` handles this automatically
6. **Version control configurations**: Keep your `.mcp.json` files in git

## Development Tips

### Quick Testing Workflow
```bash
# 1. Test your server works
mcp-dev test /path/to/server.py

# 2. Configure for hot-reload
mcp-hotreload .mcp.json

# 3. Restart Claude Code once

# 4. Develop with hot-reload
# - Edit code
# - Use restart_server tool in Claude Code
# - Test immediately
```

### CLI Testing During Development
```bash
# Test specific functionality without Claude Code
mcp-dev call your_tool '{"test": "data"}' /path/to/server.py

# Inspect server capabilities
mcp-dev inspect /path/to/server.py

# Start development proxy for external testing
mcp-dev proxy /path/to/server.py
```

## Migration from Manual Setup

If you have manually configured reloaderoo in your `.mcp.json`:

```bash
# Use mcp-hotreload to standardize your configuration
mcp-hotreload --dry-run .mcp.json  # Preview changes
mcp-hotreload .mcp.json            # Apply standardized config
```

This will:
- Preserve all your existing environment variables
- Standardize the reloaderoo configuration
- Add any missing environment variables
- Skip servers already properly configured

## Next Steps

1. **Configure your existing MCP servers**: Run `mcp-hotreload ~/.claude/.mcp.json`
2. **Test the CLI workflow**: Use `mcp-dev test` with your servers
3. **Integrate into development**: Use `restart_server` tool instead of Claude Code restarts
4. **Automate testing**: Add `mcp-dev test` to your CI/CD pipelines

## Dependencies

- **Node.js/npx**: Required for reloaderoo
- **jq**: Required for JSON processing (auto-checked by mcp-hotreload)
- **reloaderoo**: Auto-installed by mcp-hotreload if missing

## Global Command Reference

```bash
# Hot-reload setup
mcp-hotreload [--dry-run] <config-file>

# CLI development
mcp-dev test <server-path>
mcp-dev proxy <server-path>
mcp-dev call <tool> <params> <server-path>
mcp-dev inspect <server-path>
mcp-dev help
```

Both commands are globally available from anywhere in your system.

---

For more information, see:
- [Reloaderoo GitHub](https://github.com/cameroncooke/reloaderoo)
- [MCP Specification](https://modelcontextprotocol.io/docs)