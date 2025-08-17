# CC Status Line Configuration

This directory preserves ccstatusline configuration files.

## Setup

1. Run ccstatusline to configure:
   ```bash
   npx ccstatusline@latest
   ```
   This creates `~/.config/ccstatusline/settings.json` with your preferences.

2. After configuring, copy your settings to dotfiles:
   ```bash
   cp ~/.config/ccstatusline/settings.json ~/dotfiles/ccstatusline/.config/ccstatusline/
   ```

3. Apply with Stow:
   ```bash
   stow ccstatusline
   ```

## Files Managed

- `~/.config/ccstatusline/settings.json` - ccstatusline configuration
- `~/.claude/settings.json` - Claude statusLine integration (managed separately)