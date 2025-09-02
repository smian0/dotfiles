# Crystal Configuration

Crystal application configuration managed by GNU Stow.

## Files Managed

- `~/.crystal/config.json` - Crystal application settings

## Installation

```bash
# From dotfiles directory
cd ~/.dotfiles
stow crystal

# Or using Makefile
make install-crystal
```

## Configuration

The config file includes:
- Git repository path
- API settings
- Notification preferences  
- Development mode settings
- Claude executable path

## Backup Existing Configuration

Before installing with Stow, backup your existing configuration:

```bash
cp ~/.crystal/config.json ~/.crystal/config.json.backup
```

## Notes

- Sessions database (`sessions.db`) is NOT managed by Stow (remains local)
- Logs directory is NOT managed by Stow (remains local)
- Sockets directory is NOT managed by Stow (remains local)
- Only the `config.json` is version controlled