---
name: cursor-openskills-setup
description: Set up OpenSkills for Cursor IDE with proper configuration, global user rules, and verification. Use when setting up a new machine or project with Cursor + OpenSkills integration.
---

# Cursor + OpenSkills Setup Skill

## Purpose

Guide users through complete setup of OpenSkills for Cursor IDE, including:
- Installing prerequisites
- Creating proper AGENTS.md format
- Optionally syncing global user rules (version-controlled)
- Verification and testing

## When to Use

Use this skill when:
- Setting up Cursor IDE to work with Claude Code skills
- Configuring a new project for OpenSkills
- Setting up a new machine with dotfiles
- Troubleshooting OpenSkills integration in Cursor

## Prerequisites Check

Before starting, verify:

1. **Node.js installed** (v20.6+):
   ```bash
   node --version
   ```

2. **openskills CLI installed**:
   ```bash
   openskills --version
   ```

3. **Cursor IDE installed**

If any are missing, install them first.

## Workflow

### Phase 1: Install OpenSkills CLI

**If openskills not installed:**

```bash
npm i -g openskills
```

**Verify:**
```bash
openskills --version
# Should show 1.2.1 or higher
```

### Phase 2: Choose Setup Type

Ask the user:

**"What would you like to set up?"**

**A. Project-Level Setup** (AGENTS.md in current project)
- For: Setting up one specific project
- Creates: AGENTS.md with proper format
- Scope: Single project only

**B. Global User Rule Setup** (All Cursor projects)
- For: OpenSkills awareness across ALL projects
- Creates: Version-controlled user rule synced to Cursor DB
- Scope: Global (all projects on this machine)

**C. Both** (Recommended for new machines)
- Complete setup with both project and global config

### Phase 3: Project-Level Setup

**If user chose A or C:**

1. **Check current directory:**
   ```bash
   pwd
   ```

   Confirm this is the project where AGENTS.md should be created.

2. **Check for existing AGENTS.md:**
   ```bash
   ls -la AGENTS.md
   ```

3. **If AGENTS.md exists:**
   - Ask: "AGENTS.md already exists. Overwrite? (y/N)"
   - If no, skip to Phase 4

4. **Create AGENTS.md with official format:**

   **Use the init script if dotfiles are available:**
   ```bash
   ~/dotfiles/scripts/init-cursor-openskills.sh
   ```

   **Or create manually:**

   Create AGENTS.md with this exact structure:

   ```markdown
   # AI Agent Instructions

   <skills_system priority="1">

   ## Available Skills

   <!-- SKILLS_TABLE_START -->
   <usage>
   When users ask you to perform tasks, check if any of the available
   skills below can help complete the task more effectively.

   How to use skills:
   - Invoke: Bash("openskills read <skill-name>")
   - The skill content will load with detailed instructions
   - Base directory provided in output for resolving bundled resources

   Usage notes:
   - Only use skills listed in <available_skills> below
   - Do not invoke a skill that is already loaded in your context
   </usage>

   <available_skills>
   <!-- Skills will be added here by 'openskills sync' -->
   </available_skills>
   <!-- SKILLS_TABLE_END -->

   </skills_system>
   ```

5. **Sync skills to AGENTS.md:**

   **Ask user:** "Do you want to install skills from Anthropic marketplace? (y/N)"

   **If yes:**
   ```bash
   openskills install anthropics/skills
   ```

   **Otherwise:**
   - Skills at `~/.claude/skills/` will be discovered automatically

6. **Run sync:**
   ```bash
   openskills sync
   ```

   This populates AGENTS.md with skill metadata.

7. **Verify AGENTS.md:**
   ```bash
   grep "<skill>" AGENTS.md
   ```

   Should show skill entries.

### Phase 4: Global User Rule Setup

**If user chose B or C:**

1. **Check if dotfiles cursor package exists:**
   ```bash
   ls -la ~/dotfiles/cursor/user-rules/openskills.md
   ```

2. **If missing:**
   - Inform user they need the cursor package from dotfiles
   - Ask if they want to skip global setup

3. **If exists, backup current user rules:**
   ```bash
   ~/dotfiles/cursor/scripts/backup-user-rules.sh
   ```

4. **Sync the version-controlled rule:**
   ```bash
   ~/dotfiles/cursor/scripts/sync-user-rules.sh
   ```

5. **Prompt user to restart Cursor:**
   - "Restart Cursor IDE or reload window (Cmd+Shift+P → 'Developer: Reload Window')"

### Phase 5: Verification

**Verify the setup works:**

1. **List available skills:**
   ```bash
   openskills list
   ```

   Should show skills from `~/.claude/skills/` (global).

2. **Test skill loading:**
   ```bash
   openskills read research | head -30
   ```

   Should output the research skill's SKILL.md content.

3. **Check AGENTS.md format:**
   ```bash
   grep -A 2 "SKILLS_TABLE_START" AGENTS.md
   ```

   Verify proper markers are present.

4. **If global user rule was set up:**

   **Verify it's in Cursor DB:**
   ```bash
   sqlite3 "$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb" \
     "SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';" | head -5
   ```

   Should show OpenSkills content.

### Phase 6: Testing in Cursor IDE

**Provide testing instructions:**

**If project-level setup:**

1. Open the project in Cursor IDE
2. In Cursor chat, ask: "What skills are available?"
3. Cursor should reference AGENTS.md
4. Try invoking a skill: "Use the research skill to analyze React hooks"
5. Cursor should invoke: `Bash("openskills read research")`

**If global user rule setup:**

1. Open ANY project in Cursor (even without AGENTS.md)
2. Cursor should have basic OpenSkills awareness
3. When a project HAS AGENTS.md, Cursor knows how to use it

### Phase 7: Troubleshooting

**If AGENTS.md sync fails:**

- Check markers are present: `grep SKILLS_TABLE AGENTS.md`
- Ensure openskills is installed: `openskills --version`
- Try running sync with verbose output

**If Cursor doesn't see skills:**

- Verify AGENTS.md is at project root
- Check AGENTS.md has proper XML format
- Restart Cursor IDE
- Try reading AGENTS.md manually in Cursor chat

**If global user rule doesn't work:**

- Verify sync completed: Check backup file was created
- Restart Cursor (not just reload)
- Check database: Run verification command from Phase 5

## Summary Checklist

At completion, verify:

- [ ] openskills CLI installed (`openskills --version`)
- [ ] AGENTS.md created with proper format (if project setup)
- [ ] AGENTS.md contains `<!-- SKILLS_TABLE_START -->` markers
- [ ] Skills synced to AGENTS.md (`grep "<skill>" AGENTS.md`)
- [ ] Global user rule synced (if global setup chosen)
- [ ] Backup created (check `.backups/` directory)
- [ ] Cursor restarted
- [ ] Tested in Cursor (skills invokable)

## Post-Setup Notes

**For the user:**

**Project-level setup:**
- AGENTS.md is now at project root
- Version-control it: `git add AGENTS.md && git commit -m "Add OpenSkills"`
- Other team members can use the same AGENTS.md

**Global user rule:**
- Changes persist across ALL projects
- To update: Edit `~/dotfiles/cursor/user-rules/openskills.md` and re-sync
- Version-controlled in dotfiles git repo
- Sync on other machines after git pull

**Adding more skills:**
```bash
openskills install <org>/<repo>
openskills sync
```

## Reference

- Official OpenSkills: https://github.com/numman-ali/openskills
- Dotfiles cursor package: `~/dotfiles/cursor/README.md`
- User rule scripts: `~/dotfiles/cursor/scripts/`

## Success Criteria

Setup is complete when:

1. User can run `openskills list` and see skills
2. User can run `openskills read <skill>` and see content
3. AGENTS.md exists with proper format (if project setup)
4. Cursor recognizes skills in AGENTS.md (if project setup)
5. Cursor has OpenSkills awareness globally (if user rule setup)
6. User knows how to add more skills and update config
