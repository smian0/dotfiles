# CC Status Line Configuration

ccstatusline configuration files for status line customization.

## Setup

1. Run ccstatusline to configure:
   ```bash
   npx ccstatusline@latest
   ```

2. Copy your settings to dotfiles:
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