# Cursor Configuration Package

Cursor IDE configuration files managed with GNU Stow, including optional OpenSkills helpers for Claude Code skill compatibility.

## Architecture

- `.cursor/mcp.json` - Model Context Protocol (MCP) server configuration
- `.cursor/rules/openskills-loader.mdc` - **Optional** project-level helper template (not global!)
- Global configuration with project-specific override capability
- Automatic backup preservation system

**For OpenSkills setup**, use the `cursor-openskills-setup` Claude Code skill instead of manual configuration. The skill includes all necessary scripts and templates as a self-contained vertical slice.

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

#### Quick Start - Use the Skill

**In Claude Code:**
```
Use the cursor-openskills-setup skill
```

The skill will guide you through:
1. Installing prerequisites (Node.js, openskills CLI)
2. Creating AGENTS.md with proper format
3. Optionally setting up global user rules
4. Verification and testing

**Direct Usage:**
```bash
# Initialize a project
~/.claude/skills/cursor-openskills-setup/scripts/init-project.sh

# Set up global user rule
~/.claude/skills/cursor-openskills-setup/scripts/sync-user-rules.sh

# Verify setup
~/.claude/skills/cursor-openskills-setup/scripts/verify-setup.sh
```

**All scripts and templates are bundled in the skill** - no external dependencies.

#### Optional Helper (This Package)

- **`.cursor/rules/openskills-loader.mdc`**: Project-level template reminding Cursor about OpenSkills (optional, not required by official spec)

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

➕ **`.cursor/rules/openskills-loader.mdc`** - Project-level helper that reminds Cursor about OpenSkills (helpful but not required by official spec)

This extra improves the experience but isn't part of the official OpenSkills specification. All other setup tools (scripts, templates, AGENTS.md format) are bundled in the `cursor-openskills-setup` skill.

## Global User Rules (Option 3)

For truly global OpenSkills awareness across ALL projects, you can manage User Rules via version control.

### How It Works

Cursor stores User Rules in a SQLite database at:
```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```

We provide scripts to sync version-controlled rules to this database.

### Setup Global User Rule

**Use the skill's bundled script:**

```bash
# Sync the bundled template to Cursor
~/.claude/skills/cursor-openskills-setup/scripts/sync-user-rules.sh
```

This:
- Uses the bundled user rule template from the skill
- Backs up current user rules automatically
- Updates Cursor's SQLite database
- Prompts you to restart Cursor

**Restart Cursor** (or reload: Cmd+Shift+P → "Developer: Reload Window")

### Management Commands

**All commands are in the skill:**

```bash
SKILL_DIR=~/.claude/skills/cursor-openskills-setup

# Sync bundled template to Cursor
$SKILL_DIR/scripts/sync-user-rules.sh

# Or sync a custom rule file
$SKILL_DIR/scripts/sync-user-rules.sh /path/to/custom-rule.md

# Backup current Cursor user rules
$SKILL_DIR/scripts/backup-user-rules.sh [output-file]

# Restore from backup
$SKILL_DIR/scripts/restore-user-rules.sh <backup-file>

# Verify setup
$SKILL_DIR/scripts/verify-setup.sh
```

### Customization

**To customize the user rule:**

1. Copy the template from the skill
2. Edit it
3. Sync your custom version

```bash
# Copy template
cp ~/.claude/skills/cursor-openskills-setup/templates/openskills-user-rule.md ~/my-custom-rule.md

# Edit it
code ~/my-custom-rule.md

# Sync custom version
~/.claude/skills/cursor-openskills-setup/scripts/sync-user-rules.sh ~/my-custom-rule.md
```

### Backups

- Automatic backups created before each sync
- Stored in: `~/.claude/skills/cursor-openskills-setup/.backups/`
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

2025-11-11
