# Claude Configuration Package

This package manages Claude Code configuration files using GNU Stow for consistent setup across machines.

## Current Status
- **Last Verified:** 2025-01-18 14:37
- **Verification Method:** verify-claude-stow.sh
- **Status:** ✅ Fully Stowed
- **Total Items:** 22
- **Direct Symlinks:** 17
- **Tree-folded Directories:** 2 (agents/, mcp_servers/)
- **Statusline:** ✅ Active and working
- **Verification Result:** All checks passed
## Quick Start

### Installation
```bash
cd ~/dotfiles
stow claude
```

### Verification
```bash
# Run comprehensive verification
bash ~/dotfiles/scripts/verify-claude-stow.sh

# Quick statusline test
echo '{"workspace": {"current_dir": "."}, "model": {"display_name": "test"}}' | ~/.claude/scripts/statusline.sh
```

### Troubleshooting
```bash
# If issues occur, restow the package
cd ~/dotfiles && stow -R claude
```

## What's Included

### Core Configuration Files
- **settings.json** - Main Claude settings, statusline config, hooks
- **.mcp.json** - MCP server configurations
- **CLAUDE.md** - Package-specific Claude instructions

### Directories
| Directory | Type | Description |
|-----------|------|-------------|
| `agents/` | Tree-folded | Custom AI agents (4 items) |
| `commands/` | Symlinked | Custom commands |
| `hooks/` | Symlinked | Event hooks (SessionStart, UserPromptSubmit) |
| `mcp_servers/` | Tree-folded | MCP server implementations (3 items) |
| `output-styles/` | Symlinked | Output formatting styles |
| `profiles/` | Symlinked | Configuration profiles (minimal, backend, full) |
| `scripts/` | Symlinked | Helper scripts including statusline.sh |

### Documentation
- **README.md** - This file (package overview and status)
- **STOW-SETUP.md** - Detailed stow configuration guide
- **CLAUDE.md** - Instructions for Claude to maintain this package
- **CLAUDE-CONFIG-REFERENCE.md** - Configuration reference
- **CLAUDE_BEST_PRACTICES.md** - Best practices guide
- **PROFILE_USAGE_GUIDE.md** - Profile usage documentation
- **SYSTEM-PROMPT-CONFIG.md** - System prompt configuration

## Features

### ✨ Statusline
Displays current context in Claude Code:
- User@host:path
- Git branch and status
- Active model
- Claude version
- Output style
- Current prompt preview

### 🪝 Hooks
- **SessionStart** - Initializes context on new sessions
- **UserPromptSubmit** - Processes user prompts before submission

### 🔧 MCP Servers
- Custom MCP server implementations
- Markdown processing server
- Extensible architecture

### 👤 Profiles
Multiple configuration profiles for different use cases:
- **minimal** - Essential configuration
- **backend** - Backend development focused
- **full** - Complete feature set

## Recent Changes

### 2025-01-18
- ✅ Fixed statusline not showing issue
- ✅ Resolved stow symlink conflicts
- ✅ Created comprehensive verification script
- ✅ Added STOW-SETUP.md documentation
- ✅ Added CLAUDE.md maintenance instructions
- ✅ Updated README with current status

## Maintenance

### Automated Checks
Claude Code automatically verifies stow status when:
- Files are modified in this package
- Configuration issues are reported
- After stow commands are run

### Manual Verification
```bash
# Full verification
~/dotfiles/scripts/verify-claude-stow.sh

# Quick check for critical files
ls -la ~/.claude/settings.json ~/.claude/scripts/statusline.sh
```

### Adding New Files
1. Add to `~/dotfiles/claude/.claude/`
2. Run `cd ~/dotfiles && stow claude`
3. Verify with verification script
4. Update this README's status section

## Technical Details

For detailed technical information:
- **Stow setup and troubleshooting:** See [STOW-SETUP.md](./STOW-SETUP.md)
- **Package maintenance:** See [CLAUDE.md](./CLAUDE.md)

## Support

### Common Issues
1. **Statusline not showing** - Settings.json not symlinked properly
2. **Hooks not running** - Check hooks directory symlink
3. **MCP servers not found** - Verify .mcp.json symlink

### Quick Fixes
```bash
# Nuclear option - complete reinstall
cd ~/dotfiles
stow -D claude  # Remove all symlinks
stow claude     # Recreate symlinks
```

---
*This README is automatically maintained by Claude Code following instructions in CLAUDE.md*

**Package Version:** 1.0.0  
**Stow Version:** GNU Stow 2.3.1  
**Compatible with:** Claude Code 1.0.111+