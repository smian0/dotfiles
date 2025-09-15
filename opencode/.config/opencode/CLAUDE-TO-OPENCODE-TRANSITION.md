# Claude Code → OpenCode Transition Guide

Quick migration guide for existing Claude Code users transitioning to OpenCode.

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

### 6. Create Framework Documentation
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
# Test a basic command (replace with your actual commands)
opencode run "/help"

# Test with arguments (example)
opencode run "/build --target production"

# Test interactive command
opencode run "/setup"
```

### Verify No Warnings
Commands should execute without "Invalid Tool" warnings. If you see warnings:
- Check frontmatter format in command files
- Verify agent tool names are correct
- Ensure all referenced scripts exist

## Usage Patterns

### Daily Workflow
```bash
# Start OpenCode TUI
opencode

# Run specific command
opencode run "/your-command"

# Continue previous session
opencode --continue

# Use specific model/agent
opencode --model "provider/model" run "/command"
```

### Examples (adapt to your project)
```bash
# Development commands
opencode run "/dev:start"
opencode run "/test:run"
opencode run "/build:prod"

# Project management  
opencode run "/status"
opencode run "/deploy"
opencode run "/docs:generate"
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

## Migration Checklist

- [ ] Install OpenCode CLI
- [ ] Create `.opencode/` directory structure  
- [ ] Copy commands to `command/` (singular)
- [ ] Convert `settings.local.json` → `opencode.json`
- [ ] Update all command frontmatter
- [ ] Fix agent tool names
- [ ] Update script paths in commands
- [ ] Test key commands work without warnings
- [ ] Verify both CLIs produce same results

## Migration Complete

Your project now supports both systems:
- **Claude Code**: `claude /command` 
- **OpenCode**: `opencode run "/command"`

Both CLIs will execute identically with full backward compatibility.