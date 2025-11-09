# Cursor + OpenSkills Setup Skill

Self-contained skill for setting up OpenSkills in Cursor IDE.

## What This Is

A **vertical slice** skill that bundles everything needed to configure Cursor IDE for OpenSkills:

- Official AGENTS.md template
- User rule template for global setup
- Automated setup scripts
- Verification tools
- No external dependencies (except Node.js and openskills CLI)

## Structure

```
cursor-openskills-setup/
├── SKILL.md                        # Main skill instructions
├── README.md                       # This file
├── .gitignore                       # Ignore backups
├── scripts/
│   ├── init-project.sh             # Initialize AGENTS.md in any project
│   ├── sync-user-rules.sh          # Sync user rule to Cursor DB
│   ├── backup-user-rules.sh        # Backup current user rules
│   ├── restore-user-rules.sh       # Restore from backup
│   ├── verify-setup.sh             # Automated verification
│   └── load-skill.sh               # Manual skill loading helper
└── templates/
    ├── AGENTS.md.template          # Official OpenSkills format
    ├── openskills-user-rule.md     # Global user rule template
    └── openskills-loader.mdc       # Optional .mdc helper
```

## Self-Contained Design

All scripts use relative paths to reference bundled templates:

```bash
# Scripts determine their own location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$SKILL_DIR/templates"

# Then reference bundled resources
cp "$TEMPLATE_DIR/AGENTS.md.template" ./AGENTS.md
```

**Benefits:**
- Portable: Can be copied/shared independently
- No external file dependencies
- Works in any location
- Version-controlled as a unit

## Quick Start

### In Claude Code

```
Use the cursor-openskills-setup skill
```

### Direct Usage

```bash
# Get the skill's base directory
SKILL_DIR="$(openskills list | grep cursor-openskills-setup | awk '{print $NF}')"

# Or if installed at ~/.claude/skills/
SKILL_DIR="$HOME/.claude/skills/cursor-openskills-setup"

# Initialize a project
$SKILL_DIR/scripts/init-project.sh

# Set up global user rule
$SKILL_DIR/scripts/sync-user-rules.sh

# Verify setup
$SKILL_DIR/scripts/verify-setup.sh
```

## Installation

This skill should be installed to `~/.claude/skills/` for global availability.

**Via dotfiles** (if using the dotfiles repository):
```bash
# Skills are at ~/dotfiles/claude/.claude/skills/
# Symlinked to ~/.claude/skills/ when stowed
```

**Standalone installation:**
```bash
# Copy to global skills directory
cp -r cursor-openskills-setup ~/.claude/skills/
```

## Dependencies

**Required:**
- Node.js v20.6+
- openskills CLI (`npm i -g openskills`)
- Cursor IDE (for user rule sync)

**No other dependencies.** All templates and scripts are bundled.

## Version Control

When using this skill in a dotfiles repository:

- **Do commit**: SKILL.md, scripts/, templates/
- **Don't commit**: .backups/ (gitignored, may contain sensitive data)

## Official Spec

This skill follows the OpenSkills official specification:
https://github.com/numman-ali/openskills

## Last Updated

2025-11-09
