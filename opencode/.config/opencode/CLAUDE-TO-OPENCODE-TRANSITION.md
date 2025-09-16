# Claude Code → OpenCode Transition Guide

Quick migration guide for existing Claude Code users transitioning to OpenCode.

## ⚡ Automatic Transformation Available

**NEW**: If you're using the OpenCode configuration in this directory, Claude agents and commands are **automatically transformed** to OpenCode format. You may not need manual migration!

### Automatic Agent Transformation
- **Claude agents** in `~/dotfiles/claude/.claude/agents/` work automatically in OpenCode
- **No manual conversion required** for agents
- Uses triple-mechanism transformation system (pre-launch + runtime + shell function)
- Both `oc` and `opencode` commands supported

### Quick Test
```bash
# Test if automatic transformation works
oc run --agent claude-test-agent "test message"
opencode run --agent claude-test-agent "test message"

# If this works, you're already set up! No manual migration needed.
```

### Automatic Command Transformation
- **Claude commands** are also automatically transformed
- Command-transformer plugin handles `.claude/commands/` → `.opencode/command/` conversion
- Frontmatter automatically updated from Claude format to OpenCode format

For complete details see: **[AGENT-TRANSFORMATION-ARCHITECTURE.md](AGENT-TRANSFORMATION-ARCHITECTURE.md)**

## Manual Migration (If Needed)

If automatic transformation is not available or you prefer manual control:

## Installation

```bash
# Install OpenCode
npm install -g @opencode/cli

# Verify installation
opencode --version
```

## Key Differences

### Command Syntax
| Claude Code | OpenCode |
|-------------|----------|
| `claude /command:name` | `opencode run "/command:name"` |
| `claude /help` | `opencode run "/help"` |
| `claude /build` | `opencode run "/build"` |

### Configuration Files
| Claude Code | OpenCode |
|-------------|----------|
| `.claude/settings.local.json` | `.opencode/opencode.json` |
| `.claude/commands/` | `.opencode/command/` (singular) |
| `.claude/agents/` | `.opencode/agents/` |

### Tool Names & Schema
| Claude Code | OpenCode |
|-------------|----------|
| `allowed-tools: view, ls, fetch` | `agent: build` |
| `fetch` | `webfetch` |
| `view` | `read` |
| `ls` | `glob` |

## Migration Steps

### 1. Project Setup
```bash
# In your existing Claude Code project
mkdir .opencode
cd .opencode
```

### 2. Copy Core Structure
```bash
# Copy commands with renamed directory (note: singular "command")
cp -r ../.claude/commands/ ./command/

# Copy other directories (adapt to your project structure)
cp -r ../.claude/agents/ ./
cp -r ../.claude/rules/ ./
cp -r ../.claude/scripts/ ./

# Copy any project-specific directories
# cp -r ../.claude/context/ ./
# cp -r ../.claude/workflows/ ./
```

### 3. Convert Configuration
Transform your `.claude/settings.local.json` to `.opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "opencode",
  "model": "your-provider/your-model",
  "provider": {
    "your-provider": {
      "npm": "provider-package",
      "name": "Provider Name",
      "options": {
        "baseURL": "your-api-url",
        "headers": {
          "Authorization": "Bearer {env:API_KEY}"
        }
      },
      "models": {
        "your-model": {
          "name": "Model Display Name"
        }
      }
    }
  },
  "permission": {
    "edit": "allow",
    "bash": "allow",
    "webfetch": "allow"
  },
  "agent": {
    "build": { "model": "your-provider/your-model" },
    "plan": { "model": "your-provider/your-model" }
  }
}
```

### 4. Update Command Frontmatter
Convert from Claude Code format to OpenCode format:

**Before (Claude Code):**
```yaml
---
allowed-tools: Bash, Read, Write
---
```

**After (OpenCode):**
```yaml
---
description: Command description
agent: build
---
```

**Bulk conversion script:**
```bash
cd command
find . -name "*.md" -exec sed -i '' '1,/^---$/c\
---\
description: Auto-converted command\
agent: build\
---' {} \;
```

### 5. Update Agent Tool Names
Fix agent configurations to use OpenCode tool names:

```bash
cd agents
# Replace Claude tools with OpenCode equivalents
sed -i '' 's/view/read/g' *.md
sed -i '' 's/fetch/webfetch/g' *.md
sed -i '' 's/ls/glob/g' *.md
```

### 6. Set Up Universal Command Coverage (Optional)
```bash
# Add shell function for direct opencode command support
cat >> ~/.zshrc << 'EOF'

# OpenCode Agent Transformation Support
opencode() {
    "$HOME/.local/bin/opencode" "$@"
}
EOF

# Copy universal binary wrapper
mkdir -p ~/.local/bin
cp /path/to/dotfiles/bin/oc ~/.local/bin/opencode
chmod +x ~/.local/bin/opencode

# Reload shell
exec zsh

# Test both commands work identically
oc --version
opencode --version
```

### 7. Create Framework Documentation
```bash
# Copy project-specific docs
cp ../.claude/CLAUDE.md ./

# Create OpenCode framework docs
cat > OPENCODE.md << 'EOF'
# OpenCode Configuration

Generic OpenCode framework documentation for this project.

## Agent Schemas
- `build`: General implementation and execution agent
- `plan`: Planning, analysis, and strategy agent

## Available Tools
- `read`: File reading and content access
- `webfetch`: Web requests and API calls
- `bash`: Shell command execution
- `glob`: File pattern matching and discovery
- `grep`: Text search across files

## Command Structure
Commands stored in `command/` directory with frontmatter:
```yaml
---
description: Brief command description
agent: build
---
```
EOF
```

## Verification

### Test Your Commands
```bash
# Test a basic command with both wrappers
oc run "/help"
opencode run "/help"

# Test with arguments (example)
oc run "/build --target production"
opencode run "/build --target production"

# Test interactive command
oc run "/setup"
opencode run "/setup"

# Test agent functionality (if using transformation)
oc run --agent build "test agent"
opencode run --agent build "test agent"
```

### Verify No Warnings
Commands should execute without "Invalid Tool" warnings. If you see warnings:
- Check frontmatter format in command files
- Verify agent tool names are correct
- Ensure all referenced scripts exist

## Usage Patterns

### Daily Workflow
```bash
# Start OpenCode TUI (either command works)
oc
opencode

# Run specific command
oc run "/your-command"
opencode run "/your-command"

# Continue previous session
oc --continue
opencode --continue

# Use specific model/agent
oc --model "provider/model" run "/command"
opencode --model "provider/model" run "/command"
```

### Examples (adapt to your project)
```bash
# Development commands (both work identically)
oc run "/dev:start" | opencode run "/dev:start"
oc run "/test:run" | opencode run "/test:run"
oc run "/build:prod" | opencode run "/build:prod"

# Project management  
oc run "/status" | opencode run "/status"
oc run "/deploy" | opencode run "/deploy"
oc run "/docs:generate" | opencode run "/docs:generate"
```

## Troubleshooting

### "Invalid Tool" Warnings
- **Cause**: Outdated frontmatter format
- **Fix**: Update to `agent: build` format
- **Check**: Ensure no `allowed-tools:` remnants

### Command Not Found
- **Cause**: Missing files or incorrect paths
- **Fix**: Verify command exists in `.opencode/command/`
- **Check**: Ensure frontmatter is present and valid

### Configuration Issues
- **Cause**: JSON syntax or schema errors  
- **Fix**: Validate `opencode.json` syntax
- **Check**: Provider names and model paths match your setup

### Script Path Errors
- **Cause**: Commands reference `.claude/scripts/` paths
- **Fix**: Update paths to `.opencode/scripts/` in command files
- **Check**: Ensure scripts exist in new location

### Automatic Transformation Issues
- **Cause**: Agents not transforming automatically
- **Fix**: Check transformation logs with debug mode
- **Check**: Verify Claude agents exist in source directory

### `opencode` Command Not Found
- **Cause**: Shell function not defined or binary wrapper missing
- **Fix**: Run setup script again or reload shell with `exec zsh`
- **Check**: `type opencode` should show shell function

### Both Commands Don't Work Identically
- **Cause**: Different environment variables or transformation issues
- **Fix**: Check both wrappers load environment correctly
- **Check**: Compare output with `DEBUG_MODE=true`

## Migration Checklist

### Automatic Transformation Setup
- [ ] Test automatic transformation: `oc run --agent claude-test-agent "test"`
- [ ] Verify shell function works: `type opencode` shows shell function
- [ ] Test universal coverage: `opencode run --agent claude-test-agent "test"`
- [ ] If automatic works, **skip manual migration below** ✅

### Manual Migration (if needed)
- [ ] Install OpenCode CLI
- [ ] Create `.opencode/` directory structure  
- [ ] Copy commands to `command/` (singular)
- [ ] Convert `settings.local.json` → `opencode.json`
- [ ] Update all command frontmatter
- [ ] Fix agent tool names
- [ ] Update script paths in commands
- [ ] Set up shell function for universal `opencode` command
- [ ] Test key commands work without warnings
- [ ] Verify both `oc` and `opencode` commands produce same results

## Migration Complete

Your project now supports multiple command patterns:
- **Claude Code**: `claude /command` (existing)
- **OpenCode (oc wrapper)**: `oc run "/command"` (secure wrapper)
- **OpenCode (direct)**: `opencode run "/command"` (shell function)

All patterns execute identically with automatic agent transformation and full backward compatibility.

### Related Documentation
- **[AGENT-TRANSFORMATION-ARCHITECTURE.md](AGENT-TRANSFORMATION-ARCHITECTURE.md)** - Complete transformation system
- **[SHELL-FUNCTION-MAINTENANCE.md](SHELL-FUNCTION-MAINTENANCE.md)** - Shell function maintenance
- **[TESTING-PROCEDURES.md](TESTING-PROCEDURES.md)** - Testing all command patterns