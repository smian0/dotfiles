# Agent Transformation Architecture

## Overview

This document describes the on-the-fly transformation system that converts Claude Code agent files to OpenCode format. The system uses a **triple-mechanism hybrid approach** with universal command coverage for maximum reliability and user convenience.

## Architecture Components

### 1. Pre-Launch Transformation (Primary)
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/scripts/pre-launch-transform.js`
**Triggered by**: `bin/oc` launcher script before OpenCode starts
**Purpose**: Transforms Claude agents to OpenCode format and writes files to disk

```bash
# Triggered automatically by:
./bin/oc [any-command]
```

**Process**:
1. Scans for Claude agents in `~/dotfiles/claude/.claude/agents/`
2. Checks modification times (only transforms if source is newer)
3. Transforms and writes to `~/.config/opencode/agent/`
4. OpenCode reads the pre-transformed files

### 2. Runtime Plugin (Backup)
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/plugin/agent-transformer.js`
**Triggered by**: OpenCode plugin system during startup
**Purpose**: Patches Node.js filesystem functions to transform files in-memory

**Process**:
1. Patches `fs.readFileSync` and `fs.readFile` globally
2. Intercepts agent file reads and transforms content on-the-fly
3. Returns transformed content without writing to disk

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

**Process**:
1. Intercepts all direct `opencode` command calls
2. Redirects to the binary wrapper at `~/.local/bin/opencode`
3. Binary wrapper runs pre-launch transformation
4. Calls real OpenCode binary with transformed agents

### 4. Core Transformation Logic
**Location**: `/Users/smian/dotfiles/opencode/.config/opencode/plugin-util/agent-transformer-core.js`
**Used by**: All transformation mechanisms (pre-launch, runtime plugin, and shell wrapper)

**Transformations**:
```yaml
# Claude Format → OpenCode Format
---                          ---
name: agent-name       →     description: "Agent description."
description: "Long..."  →     mode: all
category: news         →     model: zhipuai/glm-4.5
tools: Read,Write,Bash  →     
---                          ---
```

## Why Triple Mechanisms?

### Critical Test Results

**Runtime Plugin ALONE fails**:
```
ERROR: TypeError: undefined is not an object (evaluating 'agent.model')
```

**Root Cause**: OpenCode validates agent files during startup **before** the filesystem patches take effect, reading the original Claude format that lacks the required `model` field.

**Pre-Launch transformation SUCCESS**: ✅ Works reliably because files are already in correct format when OpenCode starts.

### Architecture Decision Matrix

| Aspect | Pre-launch Only | Runtime Only | Shell Function Only | Triple Hybrid (Current) |
|--------|-----------------|--------------|---------------------|-------------------------|
| **Reliability** | ✅ High | ❌ Timing failures | ✅ High | ✅ Maximum defense in depth |
| **Performance** | ✅ No runtime overhead | ❌ Transform on every read | ✅ No runtime overhead | ✅ Best of all approaches |
| **Debugging** | ✅ Files visible on disk | ❌ Memory-only | ✅ Files visible on disk | ✅ Visible artifacts + logs |
| **User Experience** | ⚠️ Requires `oc` usage | ❌ Unreliable | ✅ Works with `opencode` | ✅ Universal compatibility |
| **Fail-safe** | ⚠️ Single point of failure | ❌ Unreliable | ⚠️ Single point of failure | ✅ Triple redundancy |
| **Maintenance** | ✅ Simple | ❌ Complex patching | ✅ Simple shell function | ⚠️ Multiple components |

## Implementation Details

### Pre-Launch Script Features
- **Smart caching**: Only transforms when source files are newer
- **Multi-location support**: Checks global and project-local Claude agents
- **Error handling**: Graceful degradation if transformation fails
- **Logging**: Clear feedback about transformation status

### Runtime Plugin Features
- **Global patching**: Intercepts all Node.js file reads
- **Path detection**: Identifies agent file requests
- **Format detection**: Skips files already in OpenCode format
- **Fallback**: Provides backup if pre-launch fails

### Shell Function Wrapper Features
- **Universal coverage**: Works regardless of how user invokes OpenCode
- **Transparent operation**: Users can use `opencode` directly without knowing about `oc`
- **Zero configuration**: Automatically enabled through shell function
- **Consistent behavior**: Same transformation pipeline as `oc` binary

### Symlink Issue Resolution

**Problem**: Originally `~/.config/opencode/agent/` was symlinked to Claude agents directory, preventing writes.

**Solution**: 
```bash
rm ~/.config/opencode/agent           # Remove symlink
mkdir -p ~/.config/opencode/agent     # Create real directory
```

This allows pre-launch script to write transformed files without overwriting originals.

## File Locations

### Source (Claude Format)
- Global: `~/dotfiles/claude/.claude/agents/*.md`
- Project: `<project>/.claude/agents/*.md`

### Target (OpenCode Format)  
- Global: `~/.config/opencode/agent/*.md`
- Project: `<project>/.opencode/agent/*.md`

### Core Files
```
opencode/.config/opencode/
├── scripts/
│   └── pre-launch-transform.js         # Pre-launch transformation
├── plugin/
│   └── agent-transformer.js            # Runtime plugin
├── plugin-util/
│   └── agent-transformer-core.js       # Shared transformation logic
└── tests/
    └── test-agent-transformer.js       # Comprehensive tests

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
- ✅ No need to train users on special commands
- ✅ Backward compatibility maintained
- ✅ Same transformation pipeline for both approaches

## Testing

### Manual Test
```bash
# Test pre-launch transformation script
node opencode/.config/opencode/scripts/pre-launch-transform.js

# Test end-to-end with oc binary wrapper
./bin/oc run --agent claude-test-agent "hello"

# Test end-to-end with opencode shell function (requires shell reload)
exec zsh  # Reload shell to activate function
opencode run --agent claude-test-agent "hello"

# Test both commands produce identical results
rm ~/.config/opencode/agent/*.md  # Clean slate
./bin/oc run --agent claude-test-agent "test oc" &
opencode run --agent claude-test-agent "test opencode" &
wait  # Both should work identically
```

### Automated Tests
```bash
# Comprehensive transformation test
node opencode/.config/opencode/tests/test-agent-transformer.js

# Test specific agent file
node opencode/.config/opencode/tests/test-agent-transformer.js /path/to/agent.md
```

## Monitoring & Debugging

### Pre-Launch Logs
The `oc` binary shows transformation status:
```
[Pre-Launch Transform] Starting pre-launch agent transformation...
[Pre-Launch Transform] ✅ Transformed claude-test-agent.md
[Pre-Launch Transform] Pre-launch transformation complete ✅
```

### Runtime Plugin Logs
The plugin logs filesystem interception:
```
[Agent Transformer] Patching filesystem at module load time
[Agent Transformer] Intercepting readFileSync: /path/to/agent.md
[Agent Transformer] ✅ Transformed in memory
```

### Troubleshooting

**Issue**: Agent not found
- Check if Claude agent exists in `claude/.claude/agents/`
- Verify pre-launch transformation ran successfully
- Check `~/.config/opencode/agent/` for transformed file

**Issue**: Agent loads but fails
- Check OpenCode logs for transformation errors
- Verify transformed file has correct OpenCode format
- Test transformation manually with test script

**Issue**: Transformation not updating
- Touch source file to update timestamp: `touch claude/.claude/agents/agent.md`
- Run pre-launch script manually to force re-transformation

**Issue**: `opencode` command not using wrapper
- Verify shell function exists: `type opencode`
- Reload shell configuration: `exec zsh` or `source ~/.zshrc`
- Check for shell function conflicts: `which -a opencode`

**Issue**: Shell function not working in scripts
- Shell functions only work in interactive shells
- Use `./bin/oc` for non-interactive/script usage
- Scripts should use absolute paths to avoid function interference

## Maintenance

### Shell Function Dependencies
The `opencode` shell function relies on:
1. **Shell configuration**: Function must be defined in `~/.zshrc`
2. **Binary wrapper**: `~/.local/bin/opencode` must exist and be executable
3. **Transform script**: Pre-launch transformation script must be accessible

### Updating the System
When updating the transformation system:
1. **Test both commands**: Verify both `oc` and `opencode` work after changes
2. **Shell reload**: Users need to reload their shell after `.zshrc` changes
3. **Binary permissions**: Ensure `~/.local/bin/opencode` remains executable
4. **Path integrity**: Verify shell function points to correct binary wrapper

### Distribution Considerations
For distributing this system to other users:
1. **Shell function**: Must be added to user's shell configuration
2. **Binary wrapper**: Must be placed in user's `~/.local/bin/`
3. **Permissions**: Both shell function and binary must be executable
4. **Testing**: Both command patterns should be tested after installation

### Backup and Recovery
If the shell function breaks:
1. **Fallback**: `./bin/oc` always works as original wrapper
2. **Function check**: `type opencode` shows if function is defined
3. **Manual reload**: `exec zsh` or `source ~/.zshrc` reloads function
4. **Reset function**: Remove and re-add function definition if corrupted

## Conclusion

The **triple-mechanism hybrid approach** provides maximum reliability and user convenience for Claude→OpenCode agent transformation. The combination of pre-launch transformation, runtime plugin, and shell function wrapper ensures:

- ✅ **Universal compatibility**: Both `oc` and `opencode` commands work seamlessly
- ✅ **Maximum reliability**: Triple redundancy prevents failures
- ✅ **User convenience**: No need to learn special commands
- ✅ **Backward compatibility**: Existing `oc` usage continues to work
- ✅ **Transparent operation**: Users can use OpenCode naturally

This architecture ensures that users can seamlessly use their existing Claude Code agents in OpenCode without manual conversion or configuration changes, regardless of how they invoke the tool.