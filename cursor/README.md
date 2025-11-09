# Cursor Configuration Package

Cursor IDE configuration files managed with GNU Stow, including optional OpenSkills helpers for Claude Code skill compatibility.

## Architecture

- `.cursor/mcp.json` - Model Context Protocol (MCP) server configuration
- `.cursor/rules/openskills-loader.mdc` - **Optional** project-level helper (not global!)
- `scripts/load-skill.sh` - **Optional** CLI helper for loading skills
- `user-rules/openskills.md` - **Version-controlled User Rule** for global OpenSkills awareness
- `scripts/sync-user-rules.sh` - Sync user rules to Cursor's database
- `scripts/backup-user-rules.sh` - Backup current user rules
- `scripts/restore-user-rules.sh` - Restore from backup
- Global configuration with project-specific override capability
- Automatic backup preservation system

**Note**: The `.mdc` file is project-level only (not read globally). For global awareness, use User Rules instead.

## Installation

```bash
# Install using Stow
cd ~/dotfiles
stow cursor

# Verify OpenSkills is installed
npm i -g openskills
```

This symlinks:
- `~/.cursor/mcp.json` - Global MCP configuration
- `~/.cursor/rules/openskills-loader.mdc` - Skill system bridge

## Uninstallation

```bash
stow --delete cursor
```

## Features

### 1. MCP Integration

Provides global MCP server configuration that serves as fallback for all projects. Project-specific configurations can override global settings through the MCP auto-linking system.

### 2. OpenSkills Integration

Brings Claude Code's skill system to Cursor IDE via [OpenSkills](https://github.com/numman-ali/openskills).

#### Official OpenSkills Requirements

According to the [official documentation](https://github.com/numman-ali/openskills), you only need:

1. **AGENTS.md** in your project root (with proper `<!-- SKILLS_TABLE_START -->` markers)
2. **openskills CLI** installed globally (`npm i -g openskills`)
3. Skills invoked in Cursor via: `Bash("openskills read <skill-name>")`

**That's it!** No `.mdc` files, no special Cursor configuration required.

#### Quick Start (Official Method)

**Initialize a project:**

```bash
cd /path/to/your/project
~/dotfiles/scripts/init-cursor-openskills.sh
```

This creates:
- `AGENTS.md` - Skill registry with official format
- Optionally installs skills from Anthropic marketplace

**Use skills in Cursor:**

In Cursor chat, the AI will invoke skills via:
```bash
openskills read <skill-name>
```

This is handled automatically when Cursor reads AGENTS.md.

#### Optional Helpers (This Dotfiles Package)

The `.mdc` file and helper script are **convenience additions**:

- **`.cursor/rules/openskills-loader.mdc`**: Reminds Cursor about OpenSkills (not required)
- **`scripts/load-skill.sh`**: Manual CLI helper for copying skill content (optional)

#### Available Skills

After initialization, check your project's `AGENTS.md` or run:

```bash
openskills list
```

Common skills include:
- **research**: Multi-source research with citations
- **pdf-analysis**: Privacy-preserving PDF extraction
- **mcp-builder**: Create MCP servers
- **skill-creator**: Build new skills
- **brainstorming**: Socratic method for refinement
- **test-driven-development**: TDD workflow
- **systematic-debugging**: Four-phase debugging
- **code-reviewer**: Pre-merge code review

#### How It Works

1. **Cursor starts** → Reads `.cursor/rules/*.mdc` files
2. **openskills-loader.mdc loads** → Tells Cursor about skill system
3. **Cursor reads AGENTS.md** → Discovers available skills
4. **You request a skill** → Cursor loads `.agent/skills/<name>/SKILL.md`
5. **Skill activates** → Cursor follows skill's workflow

#### Cursor vs Claude Code

| Feature | Claude Code | Cursor + OpenSkills |
|---------|-------------|---------------------|
| Skill format | SKILL.md | Same format |
| Discovery | `Skill` tool | Read AGENTS.md |
| Loading | Automatic | Manual file read |
| Progressive disclosure | ✓ | ✓ |
| Cross-IDE | ✗ | ✓ |

**Key difference**: Cursor requires explicit skill loading via file reading, while Claude Code auto-invokes based on context.

## What's Required vs Optional

### Required (Official OpenSkills)

✅ **AGENTS.md** in project root (with proper markers)
✅ **openskills CLI** installed globally
✅ Skills invoked via: `Bash("openskills read <skill-name>")`

That's the complete official setup. Cursor reads AGENTS.md and automatically knows how to invoke skills.

### Optional (This Package Adds)

➕ **`.cursor/rules/openskills-loader.mdc`** - Reminds Cursor about OpenSkills (helpful but not required)
➕ **`scripts/load-skill.sh`** - Manual CLI helper for copying skill content
➕ **Enhanced AGENTS.md template** - Includes additional context and examples

These extras improve the experience but aren't part of the official spec.

## Global User Rules (Option 3)

For truly global OpenSkills awareness across ALL projects, you can manage User Rules via version control.

### How It Works

Cursor stores User Rules in a SQLite database at:
```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```

We provide scripts to sync version-controlled rules to this database.

### Setup Global User Rule

**1. Edit the version-controlled rule:**
```bash
# Edit the source of truth
code ~/dotfiles/cursor/user-rules/openskills.md
```

**2. Sync to Cursor:**
```bash
~/dotfiles/cursor/scripts/sync-user-rules.sh
```

This:
- Backs up current user rules automatically
- Updates the SQLite database
- Prompts you to restart Cursor

**3. Restart Cursor** (or reload: Cmd+Shift+P → "Developer: Reload Window")

### Management Commands

```bash
# Sync version-controlled rule to Cursor
~/dotfiles/cursor/scripts/sync-user-rules.sh [rule-file]

# Backup current Cursor user rules
~/dotfiles/cursor/scripts/backup-user-rules.sh [output-file]

# Restore from backup
~/dotfiles/cursor/scripts/restore-user-rules.sh <backup-file>
```

### Version Control Workflow

**When you make changes:**
```bash
# 1. Edit the rule
code ~/dotfiles/cursor/user-rules/openskills.md

# 2. Test locally
~/dotfiles/cursor/scripts/sync-user-rules.sh

# 3. Commit to git
cd ~/dotfiles
git add cursor/user-rules/openskills.md
git commit -m "Update OpenSkills user rule"

# 4. On other machines, pull and sync
git pull
~/dotfiles/cursor/scripts/sync-user-rules.sh
```

### Backups

- Automatic backups created before each sync
- Stored in: `cursor/user-rules/.backups/`
- `.gitignore`'d (may contain sensitive data)

### Pros & Cons

✅ **Pros:**
- Truly global - works in ALL projects
- Version-controlled source of truth
- Portable across machines
- Automatic backups

⚠️ **Cons:**
- Requires manual sync after edits
- Must restart Cursor to see changes
- Stored in binary SQLite (not plain text)
- More complex than project-level .mdc files

## Resources

- [OpenSkills GitHub](https://github.com/numman-ali/openskills) - Official documentation
- [Claude Code Skills Docs](https://docs.claude.com/en/docs/claude-code/skills)
- [Cursor IDE Docs](https://docs.cursor.com)

## Last Updated

2025-11-09
