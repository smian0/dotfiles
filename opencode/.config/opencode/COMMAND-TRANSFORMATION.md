# Command Transformation System

## Overview

The OpenCode configuration includes automatic transformation of Claude Code commands to OpenCode format using runtime plugin interception. This allows existing Claude commands to work seamlessly in OpenCode without manual conversion.

## Architecture

### Runtime Plugin System
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/plugin/command-transformer.js`

The command transformer uses Node.js filesystem interception to transform Claude commands on-the-fly:

1. **Filesystem Patching** - Intercepts `fs.readFileSync` and `fs.readFile` calls
2. **Path Detection** - Identifies Claude command file requests
3. **Format Conversion** - Transforms frontmatter from Claude to OpenCode format
4. **Tool Mapping** - Updates tool names for OpenCode compatibility

### Transformation Process

Claude commands are automatically converted when OpenCode reads them:

```yaml
# Before (Claude format)
---
allowed-tools: Read, Write, Bash, Grep
---

# After (OpenCode format)
---
description: "Auto-converted command"
agent: build
---
```

### Tool Name Mapping

The transformer maps Claude tools to OpenCode equivalents:

| Claude Tool | OpenCode Tool |
|-------------|---------------|
| Task        | agent         |
| Read        | view          |
| Edit        | edit          |
| MultiEdit   | edit          |
| Write       | write         |
| LS          | ls            |
| Grep        | grep          |
| Glob        | glob          |
| Bash        | bash          |
| WebFetch    | fetch         |
| TodoWrite   | todo          |
| WebSearch   | websearch     |
| Search      | search        |
| Agent       | agent         |

## How It Works

### Source Locations
The transformer looks for Claude commands in:
- **Global**: `~/.claude/commands/`
- **Project**: `.claude/commands/`

### Target Format
Commands are transformed to OpenCode format with:
- **Description**: Generic description for auto-converted commands
- **Agent**: Defaults to `"build"` agent
- **Tools**: Mapped to OpenCode tool names

### Automatic Detection
The plugin automatically detects Claude command files by:
1. **Path patterns**: Files matching Claude command directory structures
2. **Frontmatter format**: Presence of `allowed-tools` field
3. **File extension**: `.md` files with YAML frontmatter

## Configuration

### Plugin Loading
The command transformer is automatically loaded as an OpenCode plugin:

```javascript
// In plugin/command-transformer.js
export default function plugin(opencode) {
  // Filesystem interception logic
  patchReadFile();
  patchReadFileSync();
}
```

### Transformation Rules

#### Frontmatter Conversion
- **allowed-tools** → Removed (tools mapped to agent capabilities)
- **title** → **description** (if present)
- **description** → Preserved or generated
- **agent** → Added with default "build"

#### Content Preservation
- Command body content is preserved unchanged
- Markdown formatting maintained
- Dynamic placeholders (like `$ARGUMENTS`) preserved

## Usage Examples

### Automatic Transformation
```bash
# Claude commands work automatically in OpenCode
oc run "/my-claude-command"
opencode run "/my-claude-command"

# No manual conversion needed
oc run "/build" --agent build
opencode run "/deploy" --agent build
```

### Command Discovery
```bash
# List available commands (includes transformed Claude commands)
oc commands
opencode commands

# Commands from both .claude/commands/ and .opencode/command/ are available
```

## Testing

### Manual Testing
```bash
# Test command transformation
oc run "/existing-claude-command"

# Verify command works without errors
opencode run "/existing-claude-command"

# Check command help shows OpenCode format
oc help "/command-name"
```

### Debug Mode
```bash
# Enable debug logging to see transformation
DEBUG_MODE=true oc run "/command"

# Check for transformation messages
DEBUG_MODE=true opencode run "/command" 2>&1 | grep -i "transform"
```

## Troubleshooting

### Command Not Found
**Symptoms**: `Command "/name" not found`
**Solutions**:
1. Check Claude command exists in `.claude/commands/`
2. Verify frontmatter has `allowed-tools` field
3. Ensure OpenCode can read the source file

### Invalid Tool Warnings
**Symptoms**: `Invalid tool "Tool" specified`
**Solutions**:
1. Check tool mapping in transformer configuration
2. Verify tool name exists in OpenCode
3. Update transformer for new tool mappings

### Transformation Not Working
**Symptoms**: Commands load but don't transform
**Solutions**:
1. Check plugin loading logs
2. Verify filesystem patching activated
3. Test with simple command first

### Performance Issues
**Symptoms**: Slow command loading
**Solutions**:
1. Check if multiple transformations occurring
2. Verify caching is working correctly
3. Consider pre-transformation approach

## Integration with Agent Transformation

### Complementary Systems
- **Agent Transformation**: Handles Claude agents → OpenCode agents
- **Command Transformation**: Handles Claude commands → OpenCode commands
- **Shell Function**: Provides universal command coverage

### Unified Experience
```bash
# Both agents and commands work seamlessly
oc run --agent claude-agent "/claude-command"
opencode run --agent claude-agent "/claude-command"
```

## Best Practices

### Command Organization
- Keep Claude commands in standard locations (`.claude/commands/`)
- Use descriptive file names (filename becomes command name)
- Maintain proper frontmatter format

### Tool Usage
- Use Claude tool names in original commands
- Rely on automatic mapping for OpenCode compatibility
- Update transformer for new tool mappings as needed

### Testing
- Test commands after any transformer updates
- Verify both `oc` and `opencode` work identically
- Check command help shows correct OpenCode format

## Maintenance

### Updating Tool Mappings
When new tools are added or renamed:

1. **Update mapping object** in `command-transformer.js`
2. **Test transformation** with affected commands
3. **Update documentation** with new mappings

### Plugin Updates
- Plugin loads automatically with OpenCode
- Changes require OpenCode restart
- Test with sample commands after updates

## Related Systems

- **[AGENT-TRANSFORMATION-ARCHITECTURE.md](AGENT-TRANSFORMATION-ARCHITECTURE.md)** - Agent transformation system
- **[SHELL-FUNCTION-MAINTENANCE.md](SHELL-FUNCTION-MAINTENANCE.md)** - Universal command coverage
- **[TESTING-PROCEDURES.md](TESTING-PROCEDURES.md)** - Testing framework

## Technical Details

### File Structure
```
opencode/.config/opencode/
├── plugin/
│   ├── command-transformer.js     # Main transformation plugin
│   └── agent-transformer.js       # Related agent transformer
└── plugin-util/
    └── command-transformer-core.js # Shared transformation logic (if exists)
```

### Dependencies
- Node.js filesystem modules (`fs`)
- YAML parsing capabilities
- OpenCode plugin system

---

**Last Updated**: September 16, 2025  
**Status**: Runtime plugin system for automatic Claude command transformation  
**Integration**: Works with agent transformation and shell function wrapper for complete Claude → OpenCode compatibility