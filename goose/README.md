# Goose Configuration

Configuration files for [Goose](https://github.com/block/goose), an open-source AI agent by Block/Square.

## What's Included

- `config.yaml` - Main Goose configuration (model, provider, extensions)
- `permission.yaml` - Permission settings for Goose operations

## Installation

This package is managed via GNU Stow as part of the dotfiles repository.

```bash
# From the dotfiles directory
stow goose
```

## Configuration

The main configuration file is located at `~/.config/goose/config.yaml` after stowing.

### Current Setup

- **Provider**: Ollama (local)
- **Model**: kimi-k2:1t-cloud
- **Enabled Extensions**: 
  - Developer
  - Computer Controller
  - Memory
  - Auto Visualiser
  - Fetch (web content)
  - Streamable MCP Server (Chrome)

### Changing Models

Edit `config.yaml` to change the model or provider:

```yaml
GOOSE_PROVIDER: "anthropic"  # or "openai", "ollama", "google", "groq"
GOOSE_MODEL: "claude-3.5-sonnet"
```

See [Goose Providers Documentation](https://block.github.io/goose/docs/getting-started/providers/) for more options.

## Notes

- Cache and log files are **not** included in this stow package
- Custom providers directory should be managed separately if needed
- This package only manages core configuration files

## Links

- [Goose GitHub](https://github.com/block/goose)
- [Goose Documentation](https://block.github.io/goose/)

---
Last Updated: 2025-10-14
