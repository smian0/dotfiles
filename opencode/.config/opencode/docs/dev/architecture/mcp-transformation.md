# MCP Transformation System

The MCP (Model Context Protocol) Transformation System provides seamless integration between Claude's MCP configuration format and OpenCode's format, enabling automatic conversion and live synchronization of MCP server configurations.

## Overview

The system consists of three main components working together to provide both startup synchronization and runtime live updates:

1. **Pre-Launch Transformer** - Initial configuration sync during OpenCode startup
2. **Runtime Plugin** - Live monitoring and transformation during OpenCode sessions  
3. **Core Transformation Library** - Shared transformation logic and validation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Startup       │    │   Runtime        │    │   OpenCode      │
│ Pre-Launch      │───▶│   Plugin         │───▶│   Usage         │
│ Transformation │    │   Monitoring     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
     Initial sync        Live monitoring         Active usage

┌─────────────────────────────────────────────────────────────────┐
│                Core Transformation Library                      │
│  • Format conversion logic                                      │
│  • Validation and error handling                               │
│  • Metadata generation                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Flow

### Input: Claude MCP Format
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "type": "stdio",
      "description": "Official library documentation lookup"
    }
  }
}
```

### Output: OpenCode MCP Format
```json
{
  "mcp": {
    "context7": {
      "command": ["npx", "-y", "@upstash/context7-mcp"],
      "type": "local",
      "enabled": true
    }
  }
}
```

## Components

### 1. Pre-Launch Transformer (`scripts/pre-launch-mcp.js`)

**Purpose**: Performs initial MCP configuration synchronization during OpenCode startup.

**Key Features**:
- **Smart Timestamp Checking**: Only transforms when Claude's `.mcp.json` is newer than `opencode.json`
- **Merge Mode**: Preserves existing OpenCode configurations while adding/updating MCP servers
- **Metadata Generation**: Creates `.mcp-metadata.json` with server descriptions and purposes
- **Error Handling**: Graceful fallback if transformation fails

**Integration**: Called by `scripts/pre-launch-transform.js` as part of the startup sequence.

**Example Output**:
```
[Pre-Launch MCP] MCP config is up-to-date (.mcp.json → opencode.json)
[Pre-Launch MCP] No MCP transformations needed
```

### 2. Runtime Plugin (`plugin/mcp-transformer.js`)

**Purpose**: Provides live monitoring and transformation during OpenCode sessions.

**Key Features**:
- **Tool Interception**: Hooks into `tool.execute.before` to detect MCP file operations
- **File Watching**: Monitors `.mcp.json` files for external changes
- **Post-Edit Transformation**: Automatically transforms after manual edits
- **Project Support**: Handles both global and project-specific MCP configurations

**Hooks**:
- `tool.execute.before`: Intercepts read/write operations on `.mcp.json` files
- `session.start`: Initializes file watchers for live monitoring

**Example Scenarios**:
- User manually edits `.mcp.json` → Plugin auto-transforms to `opencode.json`
- External tool updates Claude MCP config → File watcher triggers transformation
- Project-specific `.claude/.mcp.json` accessed → Creates corresponding `.opencode.json`

### 3. Core Transformation Library (`plugin-util/mcp-transformer-core.js`)

**Purpose**: Shared transformation logic used by both pre-launch and plugin components.

**Key Functions**:
- `transformMcpServer(serverName, claudeConfig)`: Converts individual server configs
- `transformMcp(claudeMcpConfig, existingConfig, options)`: Full transformation with validation
- Format mapping, validation, and metadata generation

**Transformation Rules**:
- **Command Merging**: Combines `command` + `args` into single array
- **Type Mapping**: `stdio` → `local`, preserves `remote`
- **Default Enablement**: All transformed servers default to `enabled: true`
- **Metadata Extraction**: Preserves descriptions, purposes, and scopes

## File Locations

### Source Files (Claude Format)
- **Global**: `~/.claude/.mcp.json` (from dotfiles symlink)
- **Project**: `./.claude/.mcp.json` (in project directory)

### Target Files (OpenCode Format)  
- **Global**: `/Users/smian/dotfiles/opencode/.config/opencode/opencode.json`
- **Project**: `./.opencode.json` (in project directory)

### Generated Files
- **Metadata**: `.mcp-metadata.json` (server descriptions and purposes)

## Usage Examples

### Manual Transformation
```bash
# Transform Claude MCP config to OpenCode format
node scripts/mcp-transformer.js

# Dry run to see what would be transformed
node scripts/mcp-transformer.js --dry-run

# Verbose output with details
node scripts/mcp-transformer.js --verbose
```

### Check MCP Status
```bash
# Check if transformation is needed
node scripts/pre-launch-mcp.js
```

### Using the MCP Manager Agent
```bash
# List all configured MCP servers
oc run --agent mcp-manager "List all MCP servers"

# Check specific server details
oc run --agent mcp-manager "Tell me about the playwright MCP server"

# Analyze configuration
oc run --agent mcp-manager "Which MCP servers are disabled and why?"
```

## Integration Points

### With Pre-Launch System
- Called by `scripts/pre-launch-transform.js`
- Runs after agent and command transformations
- Part of the `oc` startup sequence

### With Plugin System
- Registered in `opencode.json` plugins configuration
- Active during all OpenCode sessions
- Provides live monitoring capabilities

### With Agent System
- Custom `mcp-manager` agent uses gpt-oss:120b model
- Provides intelligent MCP server analysis and management
- Leverages transformation metadata for rich descriptions

## Configuration Options

### Transformation Options
```javascript
{
  enableLogging: true,      // Enable/disable console output
  validateInput: true,      // Validate Claude MCP format
  generateMetadata: true,   // Create .mcp-metadata.json
  overwriteExisting: false  // Merge vs. overwrite mode
}
```

### Agent Configuration
```json
{
  "agent": {
    "mcp-manager": {
      "model": "ollamat/gpt-oss:120b",
      "reasoningEffort": "low",
      "description": "MCP Server Manager - List, analyze, and manage Model Context Protocol servers and tools"
    }
  }
}
```

## Error Handling

### Common Issues
- **Missing Source File**: Gracefully skips transformation
- **Invalid JSON**: Reports parsing errors with file paths
- **Permission Errors**: Logs access issues without crashing
- **Watch Failures**: Falls back to manual detection

### Validation
- Claude MCP format validation
- OpenCode format compliance
- Server configuration validation
- Command array validation

## Performance Considerations

### Efficiency Features
- **Timestamp-based Updates**: Avoids unnecessary transformations
- **Merge Mode**: Preserves existing configurations
- **Low Reasoning Effort**: Uses efficient model settings for MCP manager agent
- **Smart File Watching**: Only monitors when configurations exist

### Resource Usage
- Minimal startup overhead (timestamp checks only)
- Efficient runtime monitoring (event-driven)
- Fast transformation (JSON parsing + mapping)

## Future Enhancements

### Potential Features
- **Bidirectional Sync**: OpenCode → Claude transformation
- **Validation Dashboard**: Web UI for MCP configuration health
- **Auto-discovery**: Scan for common MCP servers
- **Health Monitoring**: Check MCP server status and availability
- **Configuration Templates**: Predefined MCP server configurations

### Integration Opportunities
- **VS Code Extension**: Edit MCP configs with IntelliSense
- **Claude Desktop Integration**: Native MCP server sharing
- **Package Manager Integration**: Install MCP servers like npm packages

## Related Documentation

- [Agent Transformation](./agent-transformation.md) - Similar transformation system for agents
- [Command Transformation](./command-transformation.md) - Command transformation architecture
- [OpenCode Rate Limit Fallback](../opencode-rate-limit-fallback-system.md) - Related automation system

## Debugging

### Enable Verbose Logging
```bash
# Manual transformation with verbose output
node scripts/mcp-transformer.js --verbose

# Check pre-launch logs
oc run --print-logs | grep "MCP"
```

### Check Plugin Status
```bash
# Verify plugin is loaded
oc run "Check if MCP transformer plugin is active"

# Monitor plugin hooks
tail -f ~/.local/share/opencode/log/$(ls -t ~/.local/share/opencode/log/ | head -1) | grep "MCP Transformer"
```

---

*This transformation system provides a foundation for seamless MCP server integration between Claude and OpenCode, with both startup synchronization and live runtime updates.*