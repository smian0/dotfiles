# Command Transformation System

## Overview

The OpenCode configuration includes automatic transformation of Claude Code commands to OpenCode format using the same **triple-mechanism hybrid approach** as agents. This provides maximum reliability and user convenience through pre-launch transformation, runtime plugin backup, and universal command coverage.

## Architecture Components

### 1. Pre-Launch Transformation (Primary)
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/scripts/pre-launch-transform.js`
**Triggered by**: `bin/oc` launcher script before OpenCode starts
**Purpose**: Transforms Claude commands to OpenCode format and writes files to disk

```bash
# Triggered automatically by:
./bin/oc [any-command]
```

**Process**:
1. Scans for Claude commands in `~/dotfiles/claude/.claude/commands/` and `.claude/commands/`
2. Checks modification times (only transforms if source is newer)
3. Transforms and writes to `~/.config/opencode/command/` and `.opencode/command/`
4. OpenCode reads the pre-transformed files

### 2. Runtime Plugin (Backup)
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/plugin/command-transformer.js`
**Triggered by**: OpenCode plugin system during startup  
**Purpose**: Provides fallback transformation using shared core logic

**Status**: ✅ **Implemented and configured** - Plugin code uses shared core logic and path calculation has been fixed

**Process**:
1. Detects command file reads during runtime
2. Intercepts requests for `.opencode/command/` files  
3. Redirects to source Claude command files
4. Returns transformed content using shared transformation logic

**Note**: Direct binary calls may have extended execution times; normal shell wrapper usage is recommended

### 3. Shell Function Wrapper (Universal Coverage)
**Location**: `~/.zshrc` shell configuration
**Triggered by**: Direct `opencode` command usage
**Purpose**: Ensures transformation happens regardless of how user invokes OpenCode

```bash
# Shell function in ~/.zshrc
opencode() {
    # Run our wrapper which handles transformation and calls real opencode
    "$HOME/.local/bin/opencode" "$@"
}
```

### 4. Core Transformation Logic
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/plugin-util/command-transformer-core.js`
**Used by**: All transformation mechanisms (pre-launch, runtime plugin, and shell wrapper)

**Transformations**:
```yaml
# Claude Format → OpenCode Format
---                              ---
title: "Build Command"      →    description: "Build Command"
allowed-tools: Read,Bash    →    agent: build
category: deployment        →    category: deployment
---                              ---
```

## Why Triple Mechanisms?

### Reliability Comparison

**Pre-Launch transformation advantages**: ✅ **Verified working** - Files are in correct format when OpenCode starts, providing excellent reliability.

**Runtime Plugin status**: ✅ **Implemented with fixes** - Path calculation corrected, uses shared core logic. Works as backup for edge cases.

**Shell wrapper advantages**: ✅ **Verified working** - Provides universal coverage by ensuring pre-launch transformation runs.

### Architecture Decision Matrix

| Aspect | Runtime Only | Pre-launch Only | Shell Function Only | Triple Hybrid (Current) |
|--------|--------------|-----------------|---------------------|-------------------------|
| **Reliability** | ❌ Timing failures | ✅ High | ✅ High | ✅ Maximum defense in depth |
| **Performance** | ❌ Transform on every read | ✅ No runtime overhead | ✅ No runtime overhead | ✅ Best of all approaches |
| **Debugging** | ❌ Memory-only | ✅ Files visible on disk | ✅ Files visible on disk | ✅ Visible artifacts + logs |
| **User Experience** | ❌ Unreliable | ⚠️ Requires `oc` usage | ✅ Works with `opencode` | ✅ Universal compatibility |
| **Fail-safe** | ❌ Single point of failure | ⚠️ Single point of failure | ⚠️ Single point of failure | ✅ Triple redundancy |

## Implementation Details

### Transformation Logic

The shared core (`command-transformer-core.js`) handles:

**Frontmatter Conversion**:
```yaml
# Claude Format → OpenCode Format
title: "Command Name"        →    description: "Command Name"
allowed-tools: Read,Write    →    agent: build  
category: deployment         →    category: deployment
author: developer           →    author: developer
```

**Content Transformation**:
- `.claude/` → `.opencode/` (directory references)
- `Task tool` → `agent tool` (tool references)
- `Claude Code` → `OpenCode` (product names)
- `claude run` → `opencode run` (command references)

**Tool Name Mapping**:

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
| Notebook    | notebook      |
| Jupyter     | jupyter       |

## File Locations

### Source (Claude Format)
- Global: `~/dotfiles/claude/.claude/commands/*.md`
- Project: `<project>/.claude/commands/*.md`

### Target (OpenCode Format)  
- Global: `~/.config/opencode/command/*.md`
- Project: `<project>/.opencode/command/*.md`

### Core Files
```
opencode/.config/opencode/
├── scripts/
│   └── pre-launch-transform.js         # Enhanced for both agents AND commands
├── plugin/
│   ├── agent-transformer.js            # Agent runtime plugin
│   └── command-transformer.js          # Command runtime plugin (uses shared core)
├── plugin-util/
│   ├── agent-transformer-core.js       # Shared agent logic
│   └── command-transformer-core.js     # NEW: Shared command logic
└── tests/
    ├── test-agent-transformer.js       # Existing agent tests
    ├── test-command-transformer.js     # NEW: Command transformation tests
    └── fixtures/
        ├── claude-test-command.md       # Test command input
        └── claude-test-command-converted-expected.md  # Expected output

Shell Configuration:
~/.zshrc                                 # opencode() shell function

Binary Wrappers:
bin/oc                                   # Original binary wrapper  
~/.local/bin/opencode                    # Universal binary wrapper
```

## Universal Command Coverage

The system now supports **both calling patterns** seamlessly:

### Command Flow Architecture
```
User Command Patterns:
├── oc [args]           → bin/oc wrapper → transformation → real opencode
└── opencode [args]     → shell function → ~/.local/bin/opencode → transformation → real opencode
```

**Key Benefits**:
- ✅ Users can use either `oc` or `opencode` interchangeably
- ✅ Commands transformed before OpenCode starts (no timing issues)
- ✅ Same transformation pipeline for both approaches
- ✅ Visible transformed files for debugging

## How It Works

### Smart Multi-Location Support
The system checks for commands in priority order:
1. **Project-local**: `.claude/commands/` (takes precedence)
2. **Global**: `~/dotfiles/claude/.claude/commands/` (fallback)

### Automatic Detection
Commands are automatically detected by:
1. **File extension**: `.md` files with YAML frontmatter
2. **Frontmatter format**: Presence of `allowed-tools:` field
3. **Directory structure**: Claude command directory patterns

## Smart Caching System

### Efficient Updates
The pre-launch transformation includes smart caching:
- **Timestamp comparison**: Only transforms when source is newer than target
- **Selective processing**: Skips up-to-date commands automatically
- **Performance optimization**: No unnecessary file operations

### Cache Management
```bash
# Force re-transformation of all commands
touch ~/dotfiles/claude/.claude/commands/*.md

# Force re-transformation of specific command
touch ~/dotfiles/claude/.claude/commands/my-command.md
```

## Configuration

### Shared Core Logic
All transformation mechanisms use `command-transformer-core.js`:

```javascript
// Shared transformation logic
import { transformCommand } from '../plugin-util/command-transformer-core.js';

// Used by both pre-launch script and runtime plugin
const result = transformCommand(claudeContent, {
  returnOriginalOnError: true,
  enableLogging: false  // Quiet for startup
});
```

### Transformation Rules

#### Frontmatter Conversion Rules
1. **title** → **description** (priority over description field)
2. **allowed-tools** → **agent: build** (tools mapped to agent capabilities)
3. **Other fields** → Preserved (category, author, version, etc.)

#### Content Preservation
- Command body content preserved with transformations
- Markdown formatting maintained
- Dynamic placeholders (like `$ARGUMENTS`) preserved
- References updated for OpenCode compatibility

## Usage Examples

### Automatic Transformation
```bash
# Claude commands work automatically in OpenCode
oc run "/my-claude-command"
opencode run "/my-claude-command"

# Commands from both global and project locations
oc run "/global-command"           # From ~/dotfiles/claude/.claude/commands/
opencode run "/project-command"    # From .claude/commands/ (project-local)

# No manual conversion needed - fully automatic
oc run "/build-and-deploy" --model gpt-oss:120b
opencode run "/build-and-deploy" --model gpt-oss:120b
```

### Command Discovery
```bash
# List available commands (includes transformed Claude commands)
oc commands
opencode commands

# Both command locations are searched automatically:
# - ~/.config/opencode/command/ (transformed global)
# - .opencode/command/ (transformed project-local)
```

### Development Workflow
```bash
# Create new Claude command
echo '---
title: "Deploy to Production"
allowed-tools: Bash, Read, Write
---
Deploy the application to production.' > .claude/commands/deploy-prod.md

# Automatic transformation on next OpenCode run
oc run "/deploy-prod"  # Automatically transformed and available
```

## Testing

### Comprehensive Test Suite
```bash
# Run complete command transformation tests
node opencode/.config/opencode/tests/test-command-transformer.js

# Test specific command file
node opencode/.config/opencode/tests/test-command-transformer.js /path/to/command.md

# Test pre-launch transformation directly
node opencode/.config/opencode/scripts/pre-launch-transform.js
```

### Manual Testing
```bash
# Test command transformation end-to-end
oc run "/existing-claude-command"
opencode run "/existing-claude-command"

# Test both global and project commands
oc run "/global-command"     # From ~/dotfiles/claude/.claude/commands/
oc run "/project-command"    # From .claude/commands/

# Verify transformation artifacts
ls ~/.config/opencode/command/          # Global transformed commands
ls .opencode/command/                   # Project transformed commands
```

### Debug Mode
```bash
# Enable debug logging to see transformation
DEBUG_MODE=true oc run "/command"

# Check transformation logs
DEBUG_MODE=true opencode run "/command" 2>&1 | grep -i "transform"

# Force re-transformation for testing
touch ~/dotfiles/claude/.claude/commands/command.md
oc run "/command"  # Will re-transform due to newer timestamp
```

### Automated Tests
The test suite provides comprehensive coverage:

**Unit Tests**: Core transformation functions
- `parseCommandYAML()` - Frontmatter parsing
- `transformCommand()` - Full transformation pipeline  
- `validateTransformedCommand()` - Output validation

**Integration Tests**: End-to-end transformation
- File reading and writing
- Smart caching behavior
- Error handling and fallbacks

**Fixtures**: Test data and expected results
- `claude-test-command.md` - Sample Claude command
- `claude-test-command-converted-expected.md` - Expected output

## Troubleshooting

### Command Not Found
**Symptoms**: `Command "/name" not found`
**Solutions**:
1. Check Claude command exists in source location:
   - Global: `~/dotfiles/claude/.claude/commands/`
   - Project: `.claude/commands/`
2. Verify frontmatter has `allowed-tools:` field
3. Check pre-launch transformation logs:
   ```bash
   DEBUG_MODE=true oc run "/command" 2>&1 | grep "Pre-Launch"
   ```
4. Manually trigger transformation:
   ```bash
   touch ~/dotfiles/claude/.claude/commands/command.md
   oc run "/command"
   ```

### Transformation Not Working
**Symptoms**: Commands load but show Claude format
**Solutions**:
1. Check transformation status:
   ```bash
   ls -la ~/.config/opencode/command/
   ls -la .opencode/command/
   ```
2. Verify timestamps (source should be newer):
   ```bash
   stat ~/dotfiles/claude/.claude/commands/command.md
   stat ~/.config/opencode/command/command.md
   ```
3. Test transformation manually:
   ```bash
   node opencode/.config/opencode/tests/test-command-transformer.js /path/to/command.md
   ```

### Performance Issues
**Symptoms**: Slow command loading
**Solutions**:
1. Pre-launch transformation eliminates runtime overhead
2. Smart caching prevents unnecessary re-transformation
3. Check for transformation errors in logs

### Tool Mapping Issues
**Symptoms**: Commands reference unknown tools
**Solutions**:
1. Update tool mapping in `command-transformer-core.js`:
   ```javascript
   export const CLAUDE_TO_OPENCODE_TOOLS = {
     'NewTool': 'mapped-tool',  // Add new mappings
     // ...existing mappings
   };
   ```
2. Test updated mapping:
   ```bash
   node opencode/.config/opencode/tests/test-command-transformer.js
   ```

### Shell Function Issues
**Symptoms**: `opencode` command not using wrapper
**Solutions**:
1. Verify shell function exists: `type opencode`
2. Reload shell configuration: `exec zsh`
3. Check for conflicts: `which -a opencode`
4. Use `oc` as fallback (always works)

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

## Conclusion

The **triple-mechanism hybrid approach** provides maximum reliability and user convenience for Claude→OpenCode command transformation. The combination of pre-launch transformation, runtime plugin, and shell function wrapper ensures:

- ✅ **Universal compatibility**: Both `oc` and `opencode` commands work seamlessly
- ✅ **Maximum reliability**: Triple redundancy prevents failures
- ✅ **User convenience**: No need to learn special commands  
- ✅ **Backward compatibility**: Existing `oc` usage continues to work
- ✅ **Transparent operation**: Users can use OpenCode naturally
- ✅ **Smart caching**: Efficient transformation with timestamp checking
- ✅ **Visible artifacts**: Transformed files available for debugging

This architecture ensures that users can seamlessly use their existing Claude Code commands in OpenCode without manual conversion or configuration changes, regardless of how they invoke the tool.

---

**Last Updated**: September 16, 2025  
**Status**: ✅ **Triple-mechanism implementation complete** with verified pre-launch transformation and shell wrapper functionality  
**Integration**: Command transformation now provides the same reliability approach as agent transformation  
**Verified**: ✅ Pre-launch transformation, ✅ Shell wrapper coverage, ✅ Project precedence, ✅ Smart caching  
**Runtime Plugin**: ✅ Implemented with shared core logic and fixed path calculation