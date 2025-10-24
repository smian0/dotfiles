# Session Management Quick Reference

Essential commands for Claude Code sessions, navigation, and mobile access.

## 🎯 Core Concepts

**Claude sessions are directory-based:**
- Same directory = same Claude session
- Different directories = different Claude sessions
- Use ccmanager to create git worktrees (separate dirs) for separate sessions

## 📋 Essential Commands

### Navigation
```bash
z <project>          # Jump to directory (learns over time)
zi                   # Interactive directory search
z -                  # Go to previous directory
```

### Session Management
```bash
ss                   # Switch sessions (fzf picker)
sl                   # List all sessions
sk <name>            # Kill session
sc                   # Session in current dir
```

### Tmux
```bash
Ctrl+b d             # Detach (keep running)
Ctrl+b c             # New window
Ctrl+b "             # Split horizontal
Ctrl+b %             # Split vertical
Ctrl+b arrow         # Navigate panes
```

### Separate Claude Sessions (Git Repos)
```bash
cd ~/repo
ccm                  # Visual TUI
# Press 'n' → create worktree → separate Claude session
# Enter → switch to worktree
# 'd' → delete worktree
# 'q' → quit
```

## 🔄 Common Workflows

### Daily Work
```bash
z myproject          # Jump to project
sc                   # Start/resume session
claude               # Work in Claude
Ctrl+b d             # Detach when done
ss                   # Resume later
```

### Multiple Branches
```bash
z repo               # Jump to repo
ccm                  # Launch ccmanager
# Create worktrees for different branches
# Each = separate Claude session
```

### Mobile SSH
```bash
ssh mac              # Or: mosh mac
z project            # Jump quickly
claude               # Work
Ctrl+b d             # Detach
exit                 # Disconnect
```

## 🐛 Quick Fixes

```bash
# Commands not found
source ~/.zshrc

# ccmanager error
npm uninstall -g ccmanager && npm install -g ccmanager --force

# List what's running
sl

# Clean up sessions
sk <old-session>
```

## 💡 Quick Tips

- **zoxide** learns your paths → `z` becomes faster over time
- **tmux sessions** persist → detach freely, reconnect anytime
- **ccmanager** = separate Claude sessions per git branch
- **mosh** = better than SSH on mobile networks

---

*Configuration: `~/dotfiles/zsh/navigation-session.zsh`*
