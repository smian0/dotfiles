# Cursor Configuration Package

Cursor IDE configuration files managed with GNU Stow.

## Architecture

- `.cursor/mcp.json` - Model Context Protocol (MCP) server configuration
- Global configuration with project-specific override capability
- Automatic backup preservation system

## Installation

```bash
# Install using Stow
stow cursor

# Or install for specific target
stow --target=$HOME cursor
```

## Uninstallation

```bash
stow --delete cursor
```

## MCP Integration

Provides global MCP server configuration that serves as fallback for all projects. Project-specific configurations can override global settings through the MCP auto-linking system.
