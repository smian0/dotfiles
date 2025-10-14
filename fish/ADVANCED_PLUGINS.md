# Advanced Fish Shell Plugins

Powerful plugins to supercharge your fish shell experience.

## 🤖 AI-Powered Tools

### 1. GitHub Copilot CLI
AI-powered command suggestions from GitHub Copilot.

```fish
# Install
npm install -g @githubnext/github-copilot-cli

# Setup (one-time)
github-copilot-cli auth

# Usage
gh copilot suggest "find all large files"  # AI suggests command
gh copilot explain "tar -xzf file.tar.gz"  # Explains commands

# Fish aliases
alias '??'='gh copilot suggest -t shell'
alias 'git?'='gh copilot suggest -t git'
alias 'explain'='gh copilot explain'
```

**Features:**
- Natural language → shell command conversion
- Explains complex commands
- Context-aware suggestions
- Works with git, shell, gh commands

### 2. Atuin - Magical Shell History
AI-powered shell history with sync across machines.

```fish
# Install
brew install atuin

# Setup in fish
atuin init fish | source

# Add to config.fish
echo "atuin init fish | source" >> ~/.config/fish/config.fish
```

**Features:**
- SQLite-based history (never lose commands)
- Full-text search with fuzzy finding
- Sync history across machines (encrypted)
- Statistics and insights
- Replaces Ctrl+R with supercharged search
- Context-aware history (per directory)

**Usage:**
- `Ctrl+R` - Open atuin search
- `atuin search <query>` - Search history
- `atuin stats` - View command statistics
- `atuin sync` - Sync across machines

### 3. AI Shell Assistant (aichat)
Terminal-based AI assistant for shell commands.

```fish
# Install
cargo install aichat

# Or with brew
brew install aichat

# Usage
aichat "how to find files modified in last 24 hours"
aichat -e "git command to undo last commit"

# Fish function for easy access
function ai
    aichat $argv
end
```

**Features:**
- Multiple AI backends (OpenAI, Claude, local models)
- Shell-specific responses
- Code generation
- Command explanation

## 🚀 Productivity Plugins

### 4. Zoxide - Smarter Directory Navigation
Learn your habits and jump to directories intelligently.

```fish
# Install
brew install zoxide

# Setup
zoxide init fish | source
echo "zoxide init fish | source" >> ~/.config/fish/config.fish

# Usage
z dotfiles      # Jump to ~/dotfiles
z foo bar       # Jump to directory matching "foo" and "bar"
zi              # Interactive selection with fzf
```

**Better than `z` plugin:**
- Learns from your habits
- Frecency algorithm (frequency + recency)
- Faster and more accurate
- Works across all shells

### 5. Done - Notifications for Long Commands
Get desktop notifications when long-running commands finish.

```fish
# Install
fisher install franciscolourenco/done

# Configuration (optional)
set -U __done_min_cmd_duration 10000  # 10 seconds
set -U __done_notification_urgency_level normal
```

**Features:**
- Auto-detects long-running commands
- Desktop notifications (macOS/Linux)
- Only notifies when terminal is unfocused
- Customizable duration threshold

### 6. Autopair - Auto-close Brackets
Automatically close quotes, brackets, and parentheses.

```fish
# Install
fisher install jorgebucaran/autopair.fish
```

**Features:**
- Auto-closes: () [] {} "" '' ``
- Smart detection (doesn't double-close)
- Works with fish syntax highlighting

### 7. Colored Man Pages
Beautiful syntax-highlighted man pages.

```fish
# Install
fisher install patrickf1/colored-man-pages.fish
```

**Features:**
- Syntax highlighting for man pages
- Easier to read documentation
- Customizable colors

### 8. Bass - Run Bash Scripts in Fish
Execute bash/zsh scripts and utilities from fish.

```fish
# Install
fisher install edc/bass

# Usage
bass source ~/.nvm/nvm.sh    # Run bash script
bass export FOO=bar          # Run bash commands
```

**Useful for:**
- Running bash-only tools
- Sourcing bash configuration
- Compatibility with bash scripts

## 🎨 Enhanced Prompt Alternatives

### 9. Starship - Universal Prompt
Ultra-fast, customizable prompt (alternative to tide).

```fish
# Install
brew install starship

# Setup
starship init fish | source
echo "starship init fish | source" >> ~/.config/fish/config.fish

# Create config
mkdir -p ~/.config && starship preset nerd-font-symbols > ~/.config/starship.toml
```

**Features:**
- Blazingly fast (written in Rust)
- Shows git status, versions, cloud context
- 100+ integrations
- Works in any shell
- Highly customizable

**Presets:**
```fish
# Try different presets
starship preset bracketed-segments  # Like powerlevel10k
starship preset pure-preset         # Minimalist
starship preset tokyo-night         # Colorful
```

## 🛠️ Developer Tools Integration

### 10. Enhanced Git Plugin
Better git integration beyond basic aliases.

```fish
# Install
fisher install jhillyerd/plugin-git

# Features
- Git status in prompt
- Branch completion
- Git alias expansion
- Submodule support
```

### 11. Kubectl Integration
Enhanced Kubernetes completions and aliases.

```fish
# Install
fisher install evanlucas/fish-kubectl-completions

# Usage
k get pods              # kubectl alias
kgp                     # kubectl get pods
kdp                     # kubectl describe pod
```

### 12. Docker Completions
Enhanced Docker and Docker Compose completions.

```fish
# Install
fisher install barnybug/docker-fish-completion
```

## 📦 Modern CLI Tool Replacements

These aren't fish plugins but modern tools that work great with fish:

### Bat - Better Cat
Syntax highlighting and Git integration.

```fish
# Install
brew install bat

# Aliases
alias cat='bat'
alias less='bat --paging=always'

# Usage
bat file.js           # Syntax highlighted
bat -l json data.txt  # Force JSON syntax
```

### Eza - Better Ls
Modern replacement for ls with git integration.

```fish
# Install
brew install eza

# Aliases
alias ls='eza --icons'
alias ll='eza -la --icons --git'
alias tree='eza --tree --icons'

# Usage
ll           # List with git status
tree -L 3    # Tree view 3 levels deep
```

### Fd - Better Find
Faster, user-friendly alternative to find.

```fish
# Install
brew install fd

# Usage
fd pattern              # Find files
fd -e js                # Find .js files
fd -t d config          # Find directories named config
```

### Ripgrep - Better Grep
Blazingly fast text search.

```fish
# Install
brew install ripgrep

# Usage
rg pattern              # Search recursively
rg -i pattern           # Case insensitive
rg -t js pattern        # Search only .js files
```

### Delta - Better Git Diff
Beautiful git diff viewer.

```fish
# Install
brew install git-delta

# Configure git to use delta
git config --global core.pager delta
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.navigate true
git config --global delta.side-by-side true
```

## 🔧 Installation Script

Create an enhanced setup with all the best tools:

```fish
#!/usr/bin/env fish
# Enhanced Fish Setup Script

echo "🚀 Installing Enhanced Fish Plugins"

# Fisher plugins
fisher install franciscolourenco/done
fisher install jorgebucaran/autopair.fish
fisher install patrickf1/colored-man-pages.fish
fisher install edc/bass
fisher install jhillyerd/plugin-git

# Modern CLI tools
brew install atuin zoxide starship bat eza fd ripgrep git-delta

# AI tools (optional)
brew install aichat
# npm install -g @githubnext/github-copilot-cli  # Requires GitHub Copilot access

# Initialize in fish
atuin init fish | source
zoxide init fish | source
starship init fish | source

# Add to config.fish
echo "
# Enhanced tools
atuin init fish | source
zoxide init fish | source
starship init fish | source
" >> ~/.config/fish/config.fish

echo "✅ Enhanced setup complete!"
```

## 📋 Recommended Plugin Combination

### Minimal Enhanced Setup
```fish
fisher install franciscolourenco/done      # Notifications
fisher install jorgebucaran/autopair.fish  # Auto-close brackets
brew install zoxide bat eza                # Better navigation & viewing
zoxide init fish | source
alias cat='bat'
alias ls='eza --icons'
```

### Full Power User Setup
```fish
# All fisher plugins
fisher install franciscolourenco/done
fisher install jorgebucaran/autopair.fish
fisher install patrickf1/colored-man-pages.fish
fisher install edc/bass
fisher install jhillyerd/plugin-git

# All modern tools
brew install atuin zoxide starship bat eza fd ripgrep git-delta aichat

# Initialize
atuin init fish | source
zoxide init fish | source
starship init fish | source

# AI tools
npm install -g @githubnext/github-copilot-cli
```

### AI-Focused Setup
```fish
# AI completions and suggestions
npm install -g @githubnext/github-copilot-cli
brew install aichat atuin

# Setup
atuin init fish | source

# Aliases
alias '??'='gh copilot suggest -t shell'
alias 'git?'='gh copilot suggest -t git'
alias 'explain'='gh copilot explain'
alias 'ai'='aichat'
```

## 🎯 My Recommendation

Based on your setup, I'd add:

1. **Atuin** - Game-changing shell history (must-have)
2. **Zoxide** - Better than the current `z` plugin
3. **Done** - Helpful for long-running tasks
4. **GitHub Copilot CLI** - Best AI integration (if you have Copilot)
5. **Bat + Eza** - Much better file viewing
6. **Starship** - Alternative to tide (optional, tide is great too)

## 📚 Resources

- [Awesome Fish Plugins](https://github.com/jorgebucaran/awsm.fish)
- [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/)
- [Atuin Documentation](https://atuin.sh/)
- [Zoxide GitHub](https://github.com/ajeetdsouza/zoxide)
- [Starship Documentation](https://starship.rs/)

---
Last Updated: 2025-10-10
