# Skill Organization & Symlink Pattern

This guide explains the recommended directory structure and symlink pattern for organizing skills.

## Core Principle: Source + Symlinks

**All skills use the symlink pattern** for optimal organization:

- **Source files** live in `.claude/skills/<skill-name>/`
- **Symlinks** in `.claude/agents/` and `.claude/commands/` point to source directories
- **Benefits**: Easy development, runtime compatibility, no duplication, clean git history

## Directory Structure

### Standard Skill Structure

```
.claude/
├── skills/<skill-name>/          # SOURCE FILES (edit here)
│   ├── SKILL.md                  # Main skill instructions
│   ├── scripts/                  # Executable scripts
│   │   ├── README.md
│   │   └── *.py, *.sh
│   ├── references/               # Documentation loaded as needed
│   │   └── *.md
│   ├── assets/                   # Templates, boilerplate, resources
│   │   └── templates/
│   ├── agents/                   # Agent source files (if skill needs agents)
│   │   └── agent-name.md
│   └── commands/                 # Command source files (if skill needs commands)
│       └── command-name.md
│
├── agents/
│   └── <skill-name> → ../skills/<skill-name>/agents/     # SYMLINK
│
└── commands/
    └── <skill-name> → ../skills/<skill-name>/commands/   # SYMLINK
```

### Why Symlinks?

**Problem without symlinks**:
- Files scattered across `.claude/agents/`, `.claude/commands/`, `.claude/skills/`
- Duplication if copying files to multiple locations
- Hard to maintain and version control
- Unclear which files belong to which skill

**Solution with symlinks**:
- All skill files in one location (`.claude/skills/<skill-name>/`)
- Symlinks provide runtime discovery for Claude Code
- Single source of truth
- Easy to version control, backup, or share

## Creating the Structure

### Step 1: Create Source Directory

```bash
# Create all subdirectories at once
mkdir -p .claude/skills/<skill-name>/{scripts,references,assets,agents,commands}

# Create the main SKILL.md
touch .claude/skills/<skill-name>/SKILL.md
```

### Step 2: Create Symlinks (If Needed)

**Only create symlinks if the skill needs agents or commands:**

```bash
# If skill has agents
ln -s ../skills/<skill-name>/agents .claude/agents/<skill-name>

# If skill has commands
ln -s ../skills/<skill-name>/commands .claude/commands/<skill-name>
```

**Verify symlinks**:
```bash
# Check that symlinks point to correct locations
ls -la .claude/agents/<skill-name>
ls -la .claude/commands/<skill-name>
```

### Step 3: Initialize SKILL.md

```yaml
---
name: skill-name
description: When to use this skill (be specific and action-oriented)
---

# Skill Name

Brief description of what this skill does.

## When to Use

Describe when Claude should invoke this skill.

## Workflow

Step-by-step instructions...
```

## Benefits of This Pattern

### 1. Easy Development
Edit source files directly in the skill directory:
```bash
# Edit any file in the source location
code .claude/skills/skill-creator/SKILL.md
code .claude/skills/skill-creator/scripts/setup.sh
```

### 2. Runtime Compatibility
Claude Code discovers agents and commands via symlinks:
```bash
# Claude Code looks here for agents
.claude/agents/<skill-name>/  → symlink to skills/<skill-name>/agents/

# Claude Code looks here for commands
.claude/commands/<skill-name>/ → symlink to skills/<skill-name>/commands/
```

### 3. No Duplication
Single source of truth prevents drift:
- Change file once in source location
- All symlinks automatically reflect changes
- No need to manually sync multiple locations

### 4. Clean Git History
Version control tracks only source files:
```bash
# Commit only source files
git add .claude/skills/skill-creator/

# Symlinks don't change, so they rarely need commits
# (Only commit symlinks once when first created)
```

### 5. Transparent Access
Navigating symlinks shows all source files:
```bash
# Navigate via symlink
cd .claude/agents/skill-creator
ls -la
# Shows all files from skills/skill-creator/agents/
```

### 6. Organized Structure
All skill components packaged together:
- Easy to backup entire skill
- Simple to share with others
- Clear ownership of files
- Grouped by skill, not by type

## Directory-Level vs File-Level Symlinks

**We use directory-level symlinks (RECOMMENDED)**:
```bash
# One symlink to entire agents directory
ln -s ../skills/<skill-name>/agents .claude/agents/<skill-name>
```

**Not file-level symlinks**:
```bash
# Don't do this - creates many symlinks
ln -s ../skills/<skill-name>/agents/agent1.md .claude/agents/<skill-name>/agent1.md
ln -s ../skills/<skill-name>/agents/agent2.md .claude/agents/<skill-name>/agent2.md
```

**Why directory-level is better**:
- Fewer symlinks to manage
- Adding new files doesn't require new symlinks
- Simpler to understand and maintain
- Less clutter in `.claude/agents/` and `.claude/commands/`

## Working with Symlinks

### Creating Symlinks

**Relative paths (RECOMMENDED)**:
```bash
cd .claude/agents
ln -s ../skills/skill-creator/agents skill-creator
```

**Absolute paths (avoid)**:
```bash
# Don't do this - breaks portability
ln -s /Users/username/.claude/skills/skill-creator/agents .claude/agents/skill-creator
```

### Checking Symlinks

```bash
# List with details showing symlink targets
ls -la .claude/agents/

# Example output:
# lrwxr-xr-x  skill-creator -> ../skills/skill-creator/agents
```

### Removing Symlinks

```bash
# Remove symlink (doesn't affect source files)
rm .claude/agents/skill-creator
rm .claude/commands/skill-creator

# Source files remain intact
ls .claude/skills/skill-creator/agents/  # Still there
```

### Updating Symlinks

```bash
# If you need to recreate a symlink
rm .claude/agents/skill-creator
ln -s ../skills/skill-creator/agents .claude/agents/skill-creator
```

## Common Patterns

### Simple Skill (Level 1)
No agents or commands needed:
```
.claude/skills/skill-creator/
├── SKILL.md
├── scripts/
│   └── helper.py
├── references/
│   └── guide.md
└── assets/
    └── template.md

# No symlinks needed
```

### Skill with Delegation (Level 2)
Usually no dedicated agents, uses Task() to delegate:
```
.claude/skills/tech-stack-advisor/
├── SKILL.md                    # Contains Task() delegation code
├── references/
│   └── research-template.md
└── assets/
    └── comparison-matrix.md

# No symlinks needed (uses existing agents via Task())
```

### Skill with Custom Agents
Needs its own specialized agents:
```
.claude/skills/advanced-skill/
├── SKILL.md
├── agents/
│   ├── specialist-1.md
│   └── specialist-2.md
└── commands/
    └── workflow-cmd.md

# Symlinks required:
.claude/agents/advanced-skill → ../skills/advanced-skill/agents/
.claude/commands/advanced-skill → ../skills/advanced-skill/commands/
```

## Troubleshooting

### Symlink Not Working

**Symptom**: Claude Code doesn't find agents or commands

**Check**:
```bash
# Verify symlink exists
ls -la .claude/agents/<skill-name>

# Verify symlink target exists
ls -la .claude/skills/<skill-name>/agents/

# Verify symlink points to correct location
readlink .claude/agents/<skill-name>
```

**Fix**:
```bash
# Remove broken symlink
rm .claude/agents/<skill-name>

# Recreate with correct path
cd .claude/agents
ln -s ../skills/<skill-name>/agents <skill-name>
```

### Files Not Appearing

**Symptom**: Files in source directory don't appear via symlink

**Check**:
```bash
# List source directory
ls .claude/skills/<skill-name>/agents/

# List via symlink
ls .claude/agents/<skill-name>/
```

**Cause**: Usually the symlink points to wrong location

**Fix**: Recreate symlink with correct path

### Git Issues

**Symptom**: Symlinks show as modified in git

**Check**:
```bash
git status
```

**Fix**:
```bash
# If symlink target changed, commit it
git add .claude/agents/<skill-name>
git commit -m "Update symlink for <skill-name>"

# If symlink shouldn't be tracked
echo ".claude/agents/<skill-name>" >> .gitignore
```

## Migration Guide

### From Flat Structure to Symlinks

If you have an existing skill with flat structure:

**Before**:
```
.claude/agents/agent-name.md
.claude/commands/command-name.md
.claude/skills/skill-name/SKILL.md
```

**Migration steps**:
```bash
# 1. Create subdirectories in skill
mkdir -p .claude/skills/skill-name/{agents,commands}

# 2. Move existing files
mv .claude/agents/agent-name.md .claude/skills/skill-name/agents/
mv .claude/commands/command-name.md .claude/skills/skill-name/commands/

# 3. Create symlinks
ln -s ../skills/skill-name/agents .claude/agents/skill-name
ln -s ../skills/skill-name/commands .claude/commands/skill-name

# 4. Verify
ls -la .claude/agents/skill-name
ls -la .claude/commands/skill-name
```

## Best Practices

1. **Always use relative symlinks** - Makes skills portable
2. **Create symlinks at directory level** - Not file level
3. **Keep all skill files together** - In `.claude/skills/<skill-name>/`
4. **Document symlinks in README** - Help others understand structure
5. **Commit symlinks to git** - Track the relationship
6. **Test symlinks after creation** - Verify they work
7. **Use consistent naming** - Symlink name = skill name

## Example: Complete Setup

```bash
# Create skill structure
mkdir -p .claude/skills/my-skill/{scripts,references,assets,agents,commands}

# Create SKILL.md
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Example skill with agents and commands
---

# My Skill

Example skill showing symlink pattern.
EOF

# Create sample agent
cat > .claude/skills/my-skill/agents/helper.md << 'EOF'
---
name: my-skill-helper
description: Helper agent for my-skill
tools: [Read, Write]
---

Agent instructions here...
EOF

# Create sample command
cat > .claude/skills/my-skill/commands/run.md << 'EOF'
---
name: run
description: Run my-skill workflow
---

Command instructions here...
EOF

# Create symlinks
ln -s ../skills/my-skill/agents .claude/agents/my-skill
ln -s ../skills/my-skill/commands .claude/commands/my-skill

# Verify
echo "Checking agents symlink:"
ls -la .claude/agents/my-skill

echo "Checking commands symlink:"
ls -la .claude/commands/my-skill

echo "All files in skill directory:"
find .claude/skills/my-skill -type f
```

---

**Remember**: The symlink pattern provides the best of both worlds - organized development in a single location, with runtime discovery via symlinks.
