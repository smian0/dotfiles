# AI Assistant Instructions

> **Note:** This CLAUDE.md file provides instructions for ANY AI assistant (Claude, GitHub Copilot, Cursor, GPT, etc.). The filename remains CLAUDE.md for compatibility but applies universally.

## File Roles & Distinctions

### README.md (For Humans)
**Purpose:** User-facing documentation  
**Content:** What it is, how to use it, features, installation  
**Updates:** Only when user requests or features change  

### CLAUDE.md (For AI Assistants)
**Purpose:** AI maintenance instructions  
**Content:** Automation rules, update triggers, verification steps  
**Never:** Duplicate README content - reference it instead  

## README Management Rules

### Never
- Create READMEs without explicit request
- Auto-update without permission  
- Add content that belongs in CLAUDE.md

### Always
- Preserve existing style when editing
- Test commands before documenting
- Add "Last Updated" timestamp

### Update Triggers
1. User explicitly requests
2. Critical info outdated (ask first)
3. Structure significantly changed (ask first)

## Automated Monitoring

### Watch for Changes
Monitor dependency files (e.g., package.json for Node, requirements.txt for Python), build configs, CI/CD files, and directory structure changes. Use language-appropriate patterns.

### On Change Detection
1. Identify project type and language
2. Check if README needs updating
3. Alert user if mismatch found
4. Suggest fix (don't auto-apply)

## Package-Specific Rules

### AI Configuration Package (Example: Claude)
When configuration files change:
```bash
# Run verification script if exists
bash ~/dotfiles/scripts/verify-*-stow.sh
# Update README status section with results
# Alert if symlinks/configs broken
```

### Status Section Format
```markdown
## Current Status
- **Last Verified:** YYYY-MM-DD HH:MM  
- **Status:** ✅ Working / ⚠️ Issues  
- **Details:** See [CLAUDE.md] for maintenance
```

## Cross-References

### In README.md
```markdown
*For maintenance instructions, see [CLAUDE.md]*
```

### In CLAUDE.md  
```markdown
*For user documentation, see [README.md]*
```

## Quick Decision Tree

**User asks about feature?** → Point to README  
**User asks about maintenance?** → Point to CLAUDE.md  
**Need to document for users?** → Update README  
**Need to add automation?** → Update CLAUDE.md  
**Content could go either place?** → README for what, CLAUDE for how  

## README Quality Standards

### Universal Structure
```markdown
# Project Name
One-line description

## Quick Start / TLDR
Fastest way to get running (3-5 lines max)

## Features / What's Included
- Bullet points
- Key capabilities
- What makes it unique

## Installation
Step-by-step, tested commands

## Usage
Most common use cases with examples

## Configuration (if needed)
Only essential settings

## Troubleshooting (if needed)
Common issues only

---
Last Updated: DATE
```

### Quality Checklist
- [ ] Title describes what it does
- [ ] Quick start works in <30 seconds
- [ ] All commands copy-pasteable
- [ ] Examples show real usage
- [ ] No duplicate of code comments
- [ ] Links work
- [ ] No user-specific paths

### By Project Type

**CLI Tool:**
Focus on: Commands, flags, examples, output samples

**Library/Package:**
Focus on: API, imports, code examples, types

**Application:**
Focus on: Screenshots, features, requirements, deployment

**Configuration (dotfiles, etc):**
Focus on: What it configures, prerequisites, effects

### Length Guidelines
- **Small project:** 50-100 lines
- **Medium project:** 100-200 lines  
- **Large project:** 200-300 lines max
- **Complex:** Link to docs/ folder

### Never Include
- Implementation details (that's code comments)
- Internal architecture (unless contributing guide)
- Changelog (separate file)
- Personal information
- Untested commands

## Emergency Recovery

If README deleted/corrupted:
1. Check `git log README.md`
2. Restore from git history
3. If no backup, ask before recreating
4. Use CLAUDE.md rules to rebuild

---
*Remember: README = What (users), CLAUDE = How (AI)*