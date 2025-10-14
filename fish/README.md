# Fish Shell Configuration

Modern shell configuration using fish shell as a replacement for oh-my-zsh.

## Features

- 🐟 **Fish Shell**: Modern, user-friendly shell with better defaults
- 🎨 **Tide Prompt**: Beautiful, customizable prompt (similar to robbyrussell theme)
- 📦 **Fisher**: Lightweight plugin manager
- 🔍 **FZF Integration**: Fuzzy finder for files, history, and more
- 🚀 **Better Tab Completion**: Intelligent, context-aware completions
- ✨ **Syntax Highlighting**: Built-in, no plugins needed
- 💡 **Autosuggestions**: Built-in command suggestions from history
- 🔗 **Full dotfiles integration**: All LLM tools, AGENTS.md, MCP configs migrated

## What's Included

### Core Configuration
- `config.fish` - Main configuration file with all environment variables and aliases
- `fish_plugins` - Plugin list managed by fisher
- `functions/` - Custom fish functions (all zsh functions converted)
- `conf.d/` - Auto-loaded configuration files

### Migrated Features
All your zsh functionality has been migrated:
- ✅ LLM tools (kimi, glm, deep, claude)
- ✅ AGENTS.md auto-linking
- ✅ MCP configuration management
- ✅ SSH agent auto-start
- ✅ Pass integration
- ✅ Git safety wrapper
- ✅ All aliases and helper functions
- ✅ Development environment (pyenv, nvm, cargo, etc.)
- ✅ Custom welcome message

### Fish Plugins
- **fisher**: Plugin manager
- **tide**: Modern, customizable prompt
- **fzf.fish**: Fuzzy finder integration (Ctrl+R for history, Ctrl+F for files)
- **z**: Smart directory jumping
- **nvm.fish**: Node version management

## Installation

### Quick Install

```bash
# From dotfiles directory
cd ~/dotfiles
stow fish

# Run installation script
./fish/install.sh
```

### Manual Install

```bash
# Install fish
brew install fish

# Stow fish configuration
cd ~/dotfiles && stow fish

# Add fish to allowed shells
echo $(which fish) | sudo tee -a /etc/shells

# Install fisher and plugins
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
fisher update
```

### Set as Default Shell

```bash
chsh -s $(which fish)
```

Then log out and log back in.

## Key Differences from Zsh

### Better Defaults
Fish has many features built-in that required plugins in zsh:
- Syntax highlighting (no plugin needed)
- Autosuggestions (no plugin needed)
- Better tab completion (no plugin needed)

### Cleaner Syntax
Fish has more intuitive syntax:
```fish
# Variables
set -gx MY_VAR value        # Instead of: export MY_VAR=value

# Conditionals
if test -f file.txt         # Instead of: if [[ -f file.txt ]]; then
    echo "exists"
end

# Functions
function myfunction         # Instead of: myfunction() {
    echo $argv[1]          # Instead of: echo $1
end
```

### No Implicit Features
Fish is explicitly designed to be user-friendly:
- No .bashrc or .zshrc-style scripting tricks needed
- Configuration is simple and obvious
- Everything is a function (no aliases needed, but still supported)

## Fish-Specific Features

### FZF Integration
- `Ctrl+R` - Search command history
- `Ctrl+F` - Search files
- `Alt+C` - Change directory fuzzy finder

### Z Directory Jumper
```fish
z dotfiles     # Jump to ~/dotfiles
z fish         # Jump to fish config directory
```

### Tide Prompt Configuration
```fish
tide configure  # Interactive prompt customization
```

### Fish Config UI
```fish
fish_config     # Opens web-based configuration interface
```

## Useful Commands

```fish
# Plugin management
fisher list                 # List installed plugins
fisher install owner/repo   # Install a plugin
fisher remove owner/repo    # Remove a plugin
fisher update              # Update all plugins

# Help and documentation
help                       # Open fish documentation
help set                   # Help for specific command
man fish                   # Fish manual page

# Configuration
fish_config                # Web-based configuration
set -U fish_greeting ""    # Disable greeting (persist across sessions)
```

## Migrated Aliases

All your zsh aliases work exactly the same:
- Git shortcuts: `g`, `ga`, `gc`, `gst`, etc.
- Docker shortcuts: `d`, `dc`, `dps`, etc.
- LLM tools: `kimi`, `glm`, `deep`, `claude`
- Dotfiles: `dotfiles`, `dots`, `dotadd`, `dotremove`, `dotstatus`
- MCP tools: `mcpls`, `mcps`, `mcpm`
- AGENTS.md: `agents-init`, `agents-status`, `agents-sync`

## Troubleshooting

### Plugin Issues
```fish
# Reinstall fisher
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher

# Reinstall all plugins
fisher update
```

### Reset Configuration
```fish
# Remove fish config
rm -rf ~/.config/fish

# Re-stow from dotfiles
cd ~/dotfiles && stow fish
```

### Shell Not Changing
```fish
# Check if fish is in allowed shells
cat /etc/shells | grep fish

# If not, add it
echo $(which fish) | sudo tee -a /etc/shells

# Change shell
chsh -s $(which fish)
```

## Uninstall

To switch back to zsh:
```bash
# Change shell back to zsh
chsh -s $(which zsh)

# Unstow fish configuration
cd ~/dotfiles && stow -D fish

# Log out and log back in
```

Your zsh configuration remains intact in the `zsh/` package.

## Resources

- [Fish Documentation](https://fishshell.com/docs/current/)
- [Fisher Plugin Manager](https://github.com/jorgebucaran/fisher)
- [Tide Prompt](https://github.com/IlanCosman/tide)
- [FZF Fish Integration](https://github.com/PatrickF1/fzf.fish)
- [Awesome Fish](https://github.com/jorgebucaran/awsm.fish) - Curated list of fish plugins

---
Last Updated: 2025-10-10
