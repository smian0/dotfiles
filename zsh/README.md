# Zsh Configuration Package

Comprehensive Zsh shell environment with AI tool integration, MCP management, and AGENTS.md standardization.

## Package Structure

```
zsh/
├── .zshrc                  # Main Zsh configuration file
├── agents-md.zsh           # AGENTS.md standardization support
├── install.sh             # Package installation script
├── llm-tools.zsh          # LLM/AI tools configuration
├── mcp-config.zsh         # MCP (Model Context Protocol) management
└── README.md              # This documentation
```

## Key Features

- **Oh My Zsh Integration**: Auto-installation with essential plugins
- **AI Tool Integration**: Kimi, GLM, DeepSeek, Claude assistants
- **MCP Management**: Claude CLI-based server extraction with fallback
- **AGENTS.md Support**: Unified AI agent configuration standard
- **Smart Completion**: Enhanced tab completion with caching
- **Auto-Discovery**: Detects and links configurations on directory change

## Installation

```bash
# From dotfiles root
make install        # Development profile (includes zsh)
# or
./zsh/install.sh    # Direct installation
# or
stow --target=$HOME zsh  # Manual stow
```

## Core Commands

### AI Assistants
```bash
kimi "explain this error"     # Kimi AI (interactive/one-shot)
glm "optimize this function"  # ChatGLM assistant  
deep "debug this code"        # DeepSeek AI
claude "write docs"           # Claude assistant
```

### MCP Configuration Management
```bash
mcpls                         # List available MCP servers
mcps                          # Quick setup (extract global + symlinks)
mcpg [output-file]           # Extract global servers only
mcp-status                   # Show configuration status
```

### AGENTS.md Standardization
```bash
agents-init                  # Initialize or migrate to AGENTS.md
agents-status               # View configuration status
agents-sync                 # Force sync CLAUDE.md symlink
```

## Configuration Files

### `.zshrc` - Main Configuration
- Environment variables, PATH management
- Oh My Zsh setup with plugin management  
- Completion system and welcome message

### `mcp-config.zsh` - MCP Management
Two-approach system with Claude CLI (default) and Python script fallback for configuration extraction.

### `agents-md.zsh` - AGENTS.md Support
Implements AGENTS.md standard for unified AI agent configuration.

### `llm-tools.zsh` - AI Tool Integration
Shell integration for multiple AI assistants with API key management via password store.

## Integration Features

- **Auto-linking**: Creates .cursor/mcp.json symlinks from .mcp.json
- **Directory monitoring**: Automatic detection on `cd`
- **Symlink management**: Maintains compatibility across tools
- **Configuration validation**: Built-in status checking

## Dependencies

**Required**: Zsh, Oh My Zsh (auto-installed), Git, Curl
**Optional**: Homebrew, Claude CLI, jq, pass