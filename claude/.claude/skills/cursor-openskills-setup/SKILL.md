---
name: cursor-openskills-setup
description: Set up OpenSkills for Cursor IDE with proper configuration, global user rules, and verification. Use when setting up a new machine or project with Cursor + OpenSkills integration.
---

# Cursor + OpenSkills Setup Skill

## When to Use

- Setting up Cursor IDE to work with Claude Code skills
- Configuring a new project for OpenSkills
- Setting up a new machine with dotfiles
- Troubleshooting OpenSkills integration

## Bundled Resources

This skill includes all necessary scripts and templates:

- `scripts/init-project.sh` - Initialize OpenSkills in any project
- `scripts/sync-user-rules.sh` - Sync user rule to Cursor DB (global setup)
- `scripts/backup-user-rules.sh` - Backup current user rules
- `scripts/restore-user-rules.sh` - Restore from backup
- `scripts/verify-setup.sh` - Automated verification
- `scripts/load-skill.sh` - Manual skill loading helper
- `templates/AGENTS.md.template` - Official AGENTS.md format
- `templates/openskills-user-rule.md` - Global user rule template
- `templates/openskills-loader.mdc` - Optional .mdc helper

**Base directory** is provided when skill loads. Use it to reference bundled resources.

## Prerequisites

1. **Node.js** v20.6+: `node --version`
2. **openskills CLI**: `openskills --version`
3. **Cursor IDE** installed

**If missing:**
```bash
npm i -g openskills
```

## Quick Start

### Project Setup (AGENTS.md)

**Use the bundled script:**
```bash
<base-dir>/scripts/init-project.sh
```

This creates AGENTS.md with proper format and optionally installs skills.

### Global Setup (User Rules)

**For OpenSkills awareness in ALL Cursor projects:**
```bash
<base-dir>/scripts/sync-user-rules.sh
```

Then restart Cursor IDE.

### Verification

**Check everything is configured:**
```bash
<base-dir>/scripts/verify-setup.sh
```

Or with verbose output:
```bash
<base-dir>/scripts/verify-setup.sh --verbose
```

## Setup Workflow

**Ask user:** "What would you like to set up?"

### Option A: Project-Level Only
1. Run `<base-dir>/scripts/init-project.sh` in project directory
2. Creates AGENTS.md with official format
3. Syncs skills via `openskills sync`
4. Scope: Single project only

### Option B: Global User Rule Only
1. Run `<base-dir>/scripts/sync-user-rules.sh`
2. Syncs template to Cursor's SQLite DB
3. Restart Cursor IDE
4. Scope: ALL projects on this machine

### Option C: Both (Recommended)
1. Run project setup in desired project
2. Then run global user rule sync
3. Restart Cursor
4. Complete setup for both project and global

## Testing

**Project setup:**
- Open project in Cursor
- Ask: "What skills are available?"
- Cursor should reference AGENTS.md

**Global setup:**
- Open any project in Cursor
- Cursor has OpenSkills awareness
- When AGENTS.md present, knows how to invoke skills

## Troubleshooting

**AGENTS.md not working:**
```bash
# Verify format
grep "SKILLS_TABLE_START" AGENTS.md

# Re-sync
openskills sync
```

**User rule not working:**
```bash
# Verify in database
sqlite3 "$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb" \
  "SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';" | head -5

# Re-sync
<base-dir>/scripts/sync-user-rules.sh
```

**Restore from backup:**
```bash
<base-dir>/scripts/restore-user-rules.sh <backup-file>
```

## Reference

**Bundled templates:**
- `templates/AGENTS.md.template` - Copy this for manual setup
- `templates/openskills-user-rule.md` - User rule source
- `templates/openskills-loader.mdc` - Optional project helper

**Official spec:** https://github.com/numman-ali/openskills

## Success Criteria

- [ ] openskills CLI installed
- [ ] AGENTS.md has proper markers (if project setup)
- [ ] Skills synced to AGENTS.md
- [ ] User rule synced to Cursor DB (if global setup)
- [ ] Verification script passes
- [ ] Skills invokable in Cursor
