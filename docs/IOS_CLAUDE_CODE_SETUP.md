# iPhone Claude Code Setup Guide

Quick reference for using Claude Code from iPhone based on [clay.fyi's setup](https://clay.fyi/blog/iphone-claude-code-context-coding/).

## Prerequisites (Status in Your Dotfiles)

✅ **Already Configured:**
- Mosh installed and configured (`mosh/` package)
- Session management (tmux via sesh: `ss`, `sc`, `sl`, `sk`)
- Git and GitHub CLI
- Claude Code with global config (`claude/` package)

📋 **Need to Install on iPhone:**
- Terminal app with mosh support (Blink Shell or Termius)
- Tailscale (for secure private networking)
- ntfy app (optional: for Claude Code notifications)
- GitHub app (optional: for PR management)

## Quick Setup Steps

### 1. Tailscale Network Setup (5 min)

Install Tailscale on both your laptop and iPhone:
```bash
# On Mac (via dotfiles or Homebrew)
brew install tailscale

# Start Tailscale
sudo tailscale up
```

On iPhone: Install Tailscale app from App Store and sign in with same account.

Your laptop will get a private Tailscale IP (e.g., `100.x.x.x`)

### 2. Connect from iPhone

```bash
# From iPhone terminal app
mosh your-username@100.x.x.x

# Or use your existing session commands
ss   # Select existing session
sc   # Create session in current directory
```

### 3. Mobile-Optimized Workflow

**Shell Aliases (add to your .zshrc if desired):**
```bash
# Git shortcuts
alias gs='git status'
alias gp='git pull'
alias gc='git commit'

# Claude shortcuts
alias cc='claude'
```

**Session Management:**
Use your existing sesh commands:
- `ss` - Select/create session (already configured)
- `sc` - Session in current directory
- `sl` - List sessions
- `sk` - Kill session

## Key Mobile Tips

### Input Efficiency
- Use Claude Code slash commands: `/check`, `/test`, `/commit`
- Create keyboard shortcuts in iOS for common prompts like `[ultrathink]`
- Keep prompts concise for mobile typing

### Notifications (Optional)
Set up ntfy for alerts when Claude Code waits for input:
- Prevents need to constantly monitor screen
- Allows switching between apps

### Project Initialization
- **Do initial project setup on laptop** - use full keyboard and screen
- Once scaffolded, mobile coding becomes viable
- Leverage your global Claude config (hooks, commands, agents)

### Network Resilience
Mosh handles:
- ✅ Network switching (WiFi → Cellular)
- ✅ Sleep/wake cycles
- ✅ Airplane WiFi
- ✅ 3G/4G/5G connections

## Usage Monitoring

Your dotfiles already have Claude Code configured. Consider adding a status check:

```bash
# Monitor Claude usage in separate tmux window
claude --usage
```

## Current Dotfiles Integration

Your setup already includes:
- **Mosh**: `mosh/` package with LaunchAgent configuration
- **SSH**: Proper SSH agent configuration for GitHub
- **Claude**: Global settings, hooks, agents, commands
- **Sessions**: `sesh` integration via `navigation-session.zsh`
- **Git**: Full configuration with GPG signing

**Just add:**
1. Tailscale on both devices
2. iPhone terminal app (Blink Shell recommended)
3. Optional: ntfy for notifications

## Quick Reference

**Connect:**
```bash
mosh your-username@tailscale-ip
```

**Session Commands:**
```bash
ss    # Select session (interactive)
sc    # Session in current dir
sl    # List sessions
sk    # Kill session
```

**Claude Code:**
```bash
claude          # Standard Anthropic
glm            # Z.AI/ChatGLM
kimi           # Moonshot AI
deep           # DeepSeek
```

## Resources

- Original guide: https://clay.fyi/blog/iphone-claude-code-context-coding/
- Your mosh config: `~/dotfiles/mosh/`
- Your Claude config: `~/dotfiles/claude/.claude/`
- Session management: `~/dotfiles/zsh/navigation-session.zsh`

---
*Last Updated: 2025-10-20*
