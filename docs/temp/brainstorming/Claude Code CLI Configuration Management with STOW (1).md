<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Claude Code CLI Configuration Management with STOW: Complete Setup Guide

Based on comprehensive research and analysis of current Claude Code CLI configurations, here's a detailed guide for managing Claude Code CLI settings consistently across multiple machines using GNU STOW.

### **Key Configuration Files and Locations**

Claude Code CLI uses a **dual configuration system** that's evolved over time:[^1][^2][^3]

**Primary Configuration Files:**

- `~/.claude/settings.json` - **Official settings file** (documented)[^1]
- `~/.claude.json` - **Legacy global config** (contains MCP servers and metadata)[^2][^4]
- `~/.claude/` directory - **User-level configuration directory**[^1]

**The Challenge:** Documentation shows `~/.claude/settings.json` as the primary configuration, but in practice, many users find that `~/.claude.json` contains the actual working configuration, leading to confusion.[^3]

### **Complete STOW Directory Structure**

Here's the optimal structure for managing Claude Code CLI with STOW:

```
~/.dotfiles/
├── claude/                           # Main Claude Code package for STOW
│   ├── .claude/                      # User-level configuration directory
│   │   ├── settings.json             # Official global user settings
│   │   ├── CLAUDE.md                 # Global user instructions
│   │   ├── commands/                 # Custom commands directory
│   │   │   ├── stow-audit.md         # STOW maintenance command
│   │   │   ├── dotfiles-sync.md      # Dotfiles synchronization command
│   │   │   └── dev-setup.md          # Development environment setup
│   │   ├── agents/                   # Custom subagents
│   │   │   ├── code-reviewer.md      # Code review specialist
│   │   │   └── config-optimizer.md   # Configuration optimization agent
│   │   ├── statusline.sh             # Custom status line script
│   │   └── anthropic_key_helper.sh   # API key helper script
│   └── .claude.json                  # Legacy global config (MCP servers)
├── install.sh                        # STOW installation script
├── scripts/
│   └── validate-claude.sh            # Configuration validation
└── README.md                         # Setup instructions
```


### **Essential Configuration Files**

#### **Global User Settings (`~/.claude/settings.json`)**[^1]

```json
{
  "apiKeyHelper": "~/.claude/anthropic_key_helper.sh",
  "model": "claude-3-5-sonnet-20241022",
  "cleanupPeriodDays": 30,
  "includeCoAuthoredBy": true,
  "env": {
    "CLAUDE_CODE_DISABLE_TELEMETRY": "1",
    "BASH_DEFAULT_TIMEOUT_MS": "60000"
  },
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(npm run *)",
      "Bash(stow *)",
      "Read(~/.zshrc)",
      "Read(~/.gitconfig)"
    ],
    "deny": [
      "Read(./.env*)",
      "Read(./secrets/**)",
      "Bash(curl *)",
      "Bash(sudo *)"
    ],
    "defaultMode": "acceptEdits"
  },
  "hooks": {
    "PreToolUse": {
      "Bash": "echo 'Executing command...'"
    }
  },
  "statusLine": {
    "type": "command", 
    "command": "~/.claude/statusline.sh"
  }
}
```


#### **Legacy Global Config (`~/.claude.json`)**[^4][^2]

```json
{
  "numStartups": 1,
  "theme": "dark-daltonized",
  "hasCompletedOnboarding": true,
  "customApiKeyResponses": {
    "approved": ["<last-20-chars-of-api-key>"],
    "rejected": []
  },
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    },
    "github": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    }
  },
  "parallelTasksCount": "2",
  "autoUpdates": true,
  "verbose": false
}
```


### **Custom Commands for STOW Integration**

#### **STOW Configuration Audit (`~/.claude/commands/stow-audit.md`)**

```markdown
# STOW Configuration Audit

## Task
Perform comprehensive audit of STOW dotfiles setup:

1. **Check Current Status**
   - Run `stow -n -v .` to see all stowed packages
   - Identify any conflicts or broken symlinks
   - Verify all expected packages are properly stowed

2. **Validate Symlinks** 
   - Check that ~/.claude/ points to ~/.dotfiles/claude/.claude/
   - Verify ~/.claude.json symlink if managed by STOW
   - Test that all configuration files are properly linked

3. **Security Check**
   - Ensure no sensitive information in dotfiles repository
   - Verify .stow-global-ignore is properly configured
   - Check that API keys use environment variables or helpers

4. **Provide Recommendations**
   - Suggest any missing configurations
   - Recommend optimizations for current setup
   - Identify potential improvements for cross-machine consistency

Report findings with actionable next steps.
```


#### **Dotfiles Synchronization Command (`~/.claude/commands/dotfiles-sync.md`)**

```markdown
# Dotfiles Synchronization

## Task
Synchronize and maintain dotfiles repository:

1. **Check Repository Status**
   - Navigate to ~/.dotfiles
   - Run `git status` to see uncommitted changes
   - Review any modified configuration files

2. **Commit Management**
   - Stage appropriate changes with descriptive commit messages
   - Avoid committing temporary or machine-specific modifications
   - Group related configuration changes together

3. **Repository Maintenance**
   - Push changes to remote repository  
   - Pull any updates from other machines
   - Resolve any merge conflicts

Focus on maintaining clean, organized dotfile structure.
```


### **Security and API Key Management**

#### **API Key Helper Script (`~/.claude/anthropic_key_helper.sh`)**[^5]

```bash
#!/bin/bash
# API key helper script for Claude Code
# This allows Claude Code to retrieve API keys from environment variables
echo "${ANTHROPIC_API_KEY}"
```

**Key Security Practices:**

- **Never commit API keys** directly to dotfiles repository[^6][^4]
- Use the `apiKeyHelper` configuration to source keys from environment variables[^6][^1]
- Add sensitive patterns to `.stow-global-ignore`
- Configure `permissions.deny` to block access to sensitive files[^1]


### **Installation and Setup Scripts**

#### **Main Installation Script (`install.sh`)**

```bash
#!/usr/bin/env bash
# ~/.dotfiles/install.sh - STOW-based dotfiles installer

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Ensure we're in dotfiles directory
[[ -d "$(pwd)/.git" ]] || error "Must run from dotfiles repository root"

# Check dependencies
command -v stow >/dev/null 2>&1 || error "GNU STOW is required"
command -v claude >/dev/null 2>&1 || warn "Claude Code CLI not installed"

# Core packages (always install)
CORE_PACKAGES=("git" "zsh" "claude")

# Install core packages
log "Installing core packages..."
for package in "${CORE_PACKAGES[@]}"; do
    if [[ -d "$package" ]]; then
        log "Stowing $package..."
        stow "$package"
    else
        warn "Package $package not found, skipping"
    fi
done

# Claude Code specific setup
if [[ -x ~/.claude/anthropic_key_helper.sh ]]; then
    log "Making API key helper executable..."
    chmod +x ~/.claude/anthropic_key_helper.sh
fi

log "✅ STOW dotfiles installation completed!"
log "ℹ️  You may need to restart your shell"

if command -v claude >/dev/null 2>&1; then
    log "🤖 Run 'claude doctor' to verify Claude Code configuration"
else
    warn "⚠️  Install Claude Code CLI: npm install -g @anthropic-ai/claude-code"
fi
```


#### **Configuration Validation Script (`scripts/validate-claude.sh`)**

```bash
#!/usr/bin/env bash
# Validate Claude Code STOW configuration

echo "🔍 Validating Claude Code STOW configuration..."

# Check if Claude Code is installed
if ! command -v claude >/dev/null 2>&1; then
    echo "❌ Claude Code CLI not installed"
    exit 1
fi

# Check STOW symlinks
if [[ -L ~/.claude ]] && [[ -d ~/.claude ]]; then
    echo "✅ ~/.claude directory properly stowed"
    echo "   → $(readlink ~/.claude)"
else
    echo "❌ ~/.claude not properly stowed"
fi

# Check configuration files
if [[ -f ~/.claude/settings.json ]]; then
    echo "✅ Global settings.json found"
else
    echo "⚠️  No global settings.json found"
fi

# Run Claude Code diagnostics
echo ""
echo "🏥 Running Claude Code diagnostics..."
claude doctor

echo ""
echo "✅ Claude Code STOW validation completed"
```


### **Advanced Setup: Automated Configuration**[^5]

For **fully automated setup** (useful for CI/CD or scripted installations):

```bash
#!/usr/bin/env bash
# Automated Claude Code configuration setup

# Create API key helper script
mkdir -p ~/.claude
echo 'echo ${ANTHROPIC_API_KEY}' > ~/.claude/anthropic_key_helper.sh
chmod +x ~/.claude/anthropic_key_helper.sh

# Get last 20 characters of API key for approval
ANTHROPIC_API_KEY_LAST_20_CHARS=${ANTHROPIC_API_KEY: -20}

# Create initial .claude.json configuration
cat <<EOM > ~/.claude.json
{
  "customApiKeyResponses": {
    "approved": ["$ANTHROPIC_API_KEY_LAST_20_CHARS"],
    "rejected": []
  },
  "hasCompletedOnboarding": true,
  "theme": "dark-daltonized"
}
EOM

# Configure API key helper
claude config set --global apiKeyHelper ~/.claude/anthropic_key_helper.sh

# Set useful global configurations
claude config set --global parallelTasksCount 2
claude config set --global theme dark-daltonized
```


### **Best Practices for Multi-Machine Consistency**

#### **1. Separation of Concerns**[^1]

- **Global settings** (consistent across machines) → STOW managed in `~/.claude/settings.json`
- **Project settings** (team shared) → Git repository in `.claude/settings.json`
- **Local settings** (machine specific) → `.claude/settings.local.json` (git ignored)


#### **2. Environment-Specific Handling**

- Use **environment variables** for machine-specific paths and credentials
- Maintain **separate install scripts** for different platforms (macOS/Linux/Windows)
- **Test configurations** on multiple environments before committing


#### **3. Security Considerations**[^6][^1]

- **Never commit API keys** directly to version control
- Use `apiKeyHelper` scripts with environment variables
- Configure **strict permissions** with `permissions.deny` for sensitive directories
- Regular security audits using custom commands


#### **4. Maintenance Workflow**

- **Regular STOW audits** using `/stow-audit` command
- **Automated configuration validation** on new machine setup
- **Version control** all shareable settings with meaningful commit messages
- **Cross-machine testing** before pushing configuration changes


### **Integration with Development Workflow**[^5]

This STOW + Claude Code CLI setup provides several advantages:

1. **Consistent Environment**: Identical Claude Code configurations across all development machines
2. **Automated Setup**: New machines ready in minutes with single script execution
3. **Security**: API keys managed through environment variables, not committed to git
4. **Team Collaboration**: Shareable configurations and custom commands
5. **Maintenance**: Built-in tools for auditing and synchronizing dotfiles

The configuration system supports **hierarchical settings** where enterprise policies override user settings, ensuring both flexibility and compliance in team environments.[^1]

<div style="text-align: center">⁂</div>

[^1]: https://docs.anthropic.com/en/docs/claude-code/settings

[^2]: https://scottspence.com/posts/configuring-mcp-tools-in-claude-code

[^3]: https://github.com/anthropics/claude-code/issues/1202

[^4]: https://www.reddit.com/r/ClaudeAI/comments/1lwuo4i/add_claudejson_to_your_dotfiles_repo/

[^5]: https://www.anthropic.com/engineering/claude-code-best-practices

[^6]: https://ainativedev.io/news/configuring-claude-code

[^7]: https://claude.ai/public/artifacts/03a4aa0c-67b2-427f-838e-63770900bf1d

[^8]: https://www.reddit.com/r/ClaudeAI/comments/1llwc8b/how_to_run_multiple_claude_code_instances_and/

[^9]: https://docs.anthropic.com/en/docs/claude-code/setup

[^10]: https://www.youtube.com/watch?v=hpMrTabldEY\&vl=en

[^11]: https://www.claudelog.com/configuration/

