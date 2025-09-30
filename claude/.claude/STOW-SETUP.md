# Claude Package Stow Setup

This document describes how the `claude/` stow package is configured for directory-level symlinking.

## Directory Structure

```
~/dotfiles/claude/
└── .claude/
    ├── agents/              # → Symlinked as directory
    ├── commands/            # → Symlinked as directory
    ├── hooks/               # → Symlinked as directory
    ├── profiles/            # → Symlinked as directory
    ├── scripts/             # → Symlinked as directory
    ├── settings.json        # → Individual file symlink
    ├── .mcp.json            # → Individual file symlink
    └── [other files]        # → Individual file symlinks
```

## Current Setup

### Directory-Level Symlinks ✅

These directories are symlinked at the **directory level** (entire directory is a symlink):

```bash
~/.claude/agents -> ../dotfiles/claude/.claude/agents
~/.claude/commands -> ../dotfiles/claude/.claude/commands
~/.claude/hooks -> ../dotfiles/claude/.claude/hooks
~/.claude/profiles -> ../dotfiles/claude/.claude/profiles
~/.claude/scripts -> ../dotfiles/claude/.claude/scripts
```

**Benefits**:
- Edit files in `~/dotfiles/claude/.claude/agents/` → changes immediately available in `~/.claude/agents/`
- Add new files → automatically available (no re-stow needed)
- Cleaner structure (one symlink per directory vs. one per file)

### File-Level Symlinks

Individual files at the root of `.claude/`:

```bash
~/.claude/settings.json -> ../dotfiles/claude/.claude/settings.json
~/.claude/.mcp.json -> ../dotfiles/claude/.claude/.mcp.json
~/.claude/ARCHITECTURE.md -> ../dotfiles/claude/.claude/ARCHITECTURE.md
# ... etc
```

## How Stow Works

### Directory Folding

When stow encounters a directory in the source that doesn't exist in the target:
- It creates a **directory symlink** (not individual file symlinks)
- This is called "directory folding"

Example:
```bash
# Before stow
~/dotfiles/claude/.claude/commands/multi-agent.md
~/.claude/                                      # exists but no commands/ dir

# After stow
~/.claude/commands -> ../dotfiles/claude/.claude/commands/
```

### Why agents/ Was Different

If `~/.claude/agents/` already exists as a regular directory:
- Stow cannot create a directory symlink
- Instead, it creates individual file symlinks inside the directory

**Solution**: Remove existing directory, then re-stow:
```bash
stow -D claude              # Unstow
rm -rf ~/.claude/agents     # Remove directory
stow claude                 # Re-stow (creates directory symlink)
```

## Maintenance

### Adding New Files

**For directory-level symlinked directories** (agents, commands, etc.):

```bash
# 1. Add file in dotfiles
vim ~/dotfiles/claude/.claude/agents/research/new-agent.md

# 2. No re-stow needed! File is immediately available
head ~/.claude/agents/research/new-agent.md

# 3. (Optional) For direct @agent invocation, create root symlink
cd ~/dotfiles/claude/.claude/agents/
ln -s research/new-agent.md new-agent.md
# File is immediately available (no re-stow needed)
```

**For root-level files**:

```bash
# 1. Add file in dotfiles
vim ~/dotfiles/claude/.claude/new-file.json

# 2. Re-stow to create symlink
cd ~/dotfiles && stow -R claude

# 3. Verify
ls -la ~/.claude/new-file.json
```

### Editing Files

**Always edit in dotfiles**, not in home directory:

```bash
# ✅ Correct
vim ~/dotfiles/claude/.claude/agents/research/web-researcher.md

# ❌ Wrong (edit would work but changes not tracked in git)
vim ~/.claude/agents/research/web-researcher.md
```

Since directories are symlinked, both paths point to the same file, but editing in dotfiles makes intent clear.

### Removing Files

```bash
# 1. Remove from dotfiles
rm ~/dotfiles/claude/.claude/agents/obsolete-agent.md

# 2. Re-stow to clean up
cd ~/dotfiles && stow -R claude
```

## Troubleshooting

### "Agents not showing up with @agent syntax"

**Problem**: Agent file in subdirectory (e.g., `agents/research/web-researcher.md`)

**Solution**: Create root-level symlink in dotfiles:
```bash
cd ~/dotfiles/claude/.claude/agents/
ln -s research/web-researcher.md web-researcher.md
# Immediately available (no re-stow needed due to directory symlink)
```

### "Changes not reflected"

**Problem**: Edited file in wrong location or need to re-stow

**Check**:
```bash
# Verify directory is symlinked
readlink ~/.claude/agents
# Should show: ../dotfiles/claude/.claude/agents

# Verify you're editing correct file
ls -la ~/dotfiles/claude/.claude/agents/web-researcher.md
```

**Solution**: If directory is NOT symlinked, re-create it:
```bash
stow -D claude
rm -rf ~/.claude/agents
stow claude
```

### "Stow conflicts"

**Problem**: Files exist in both source and target

**Solution**: Use `--adopt` to move existing files to dotfiles:
```bash
stow --adopt claude
# Then review changes in git to see what was adopted
```

Or manually resolve conflicts:
```bash
# Remove conflicting files from home
rm ~/.claude/conflicting-file.json

# Re-stow
stow -R claude
```

## Verification

To verify the setup is correct:

```bash
# 1. Check directory symlinks
readlink ~/.claude/agents
readlink ~/.claude/commands

# Expected output:
# ../dotfiles/claude/.claude/agents
# ../dotfiles/claude/.claude/commands

# 2. Test file access
head ~/.claude/agents/web-researcher.md
head ~/.claude/commands/multi-agent.md

# 3. Test editing
echo "# Test comment" >> ~/dotfiles/claude/.claude/agents/README.md
tail -1 ~/.claude/agents/README.md
# Should show: # Test comment

# 4. Clean up test
git checkout ~/dotfiles/claude/.claude/agents/README.md
```

## Integration with Git

All changes in `~/dotfiles/claude/.claude/` are tracked by git:

```bash
cd ~/dotfiles

# See changes
git status

# Commit
git add claude/.claude/agents/new-agent.md
git commit -m "Add new agent"
```

Since `~/.claude/agents` is a symlink to `~/dotfiles/claude/.claude/agents/`, any changes made in either location are tracked by git.

## Deployment to New Machine

```bash
# 1. Clone dotfiles
git clone <repo> ~/dotfiles

# 2. Stow claude package
cd ~/dotfiles
stow claude

# 3. Verify
readlink ~/.claude/agents
readlink ~/.claude/commands
```

Everything should work immediately without manual symlink creation!

---

**Last Updated**: 2025-09-30
**Stow Version**: 2.4.0
**Status**: ✅ Directory-level symlinks configured