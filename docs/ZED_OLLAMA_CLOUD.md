# Zed Editor + Ollama Cloud Configuration

Guide for configuring Zed editor to use Ollama Cloud models, specifically `deepseek-v3.1:671b-cloud`.

## Quick Setup

### 1. Get Ollama Cloud API Key

```bash
# Sign in to Ollama
ollama signin

# Create API key at: https://ollama.com/settings/keys
# Copy and save your API key
```

### 2. Set Environment Variable

Add to your shell profile (already configured in `zsh/.zshrc`):

```bash
export OLLAMA_API_KEY="your-api-key-here"
```

Then reload your shell:

```bash
source ~/.zshrc
```

### 3. Verify Zed Configuration

The Zed settings have been configured at `~/.config/zed/settings.json`:

```json
{
  "language_models": {
    "ollama": {
      "api_url": "https://ollama.com",
      "available_models": [
        {
          "name": "deepseek-v3.1:671b-cloud",
          "display_name": "deepseek-v3.1:671b-cloud (Turbo)",
          "max_tokens": 128000,
          "max_output_tokens": 8192,
          "supports_tools": true,
          "supports_thinking": true,
          "supports_images": true
        }
      ]
    }
  },
  "agent": {
    "default_model": {
      "provider": "ollama",
      "model": "deepseek-v3.1:671b-cloud"
    }
  }
}
```

### 4. Restart Zed

Close and reopen Zed editor for the changes to take effect.

## Configuration Details

### Critical Settings

- **API URL**: `https://ollama.com` (NOT `http://localhost:11434`)
- **Model Name**: `deepseek-v3.1:671b-cloud` (exact spelling required)
- **Context Window**: 128K tokens
- **Output Tokens**: 8K default (conservative)

### Model Capabilities

- ✅ Tool calling (function calling)
- ✅ Thinking mode (hybrid reasoning)
- ✅ Vision support (image understanding)
- ✅ 671B parameters (37B active per token)

## Troubleshooting

### "Failed to connect to Ollama"

```bash
# Check if API key is set
echo $OLLAMA_API_KEY

# Verify API key at: https://ollama.com/settings/keys
# Restart Zed after setting the key
```

### "Model not found"

Ensure exact model name: `deepseek-v3.1:671b-cloud`

### Slow responses

This is expected - the 671B cloud model runs on datacenter hardware with network latency.

### Still using localhost

Check that `api_url` in Zed settings is `https://ollama.com` not `http://localhost:11434`

## Advanced Configuration

### Increase Output Token Limit

For longer responses (up to 64K tokens):

```json
{
  "max_output_tokens": 65536
}
```

**Note**: Longer outputs may have cost implications.

### Alternative: UI Configuration

Instead of editing `settings.json`:

1. Open Agent Panel → Settings
2. Add Ollama provider
3. Paste API key
4. Add custom model `deepseek-v3.1:671b-cloud`

## Security Notes

- Never commit `OLLAMA_API_KEY` to version control
- Store in shell profile or secure credential manager
- Rotate keys periodically at https://ollama.com/settings/keys

## References

- [Zed LLM Providers Documentation](https://zed.dev/docs/ai/llm-providers)
- [Ollama Cloud Documentation](https://docs.ollama.com/cloud)
- [DeepSeek V3.1 Model Page](https://ollama.com/library/deepseek-v3.1:671b-cloud)

---
Last Updated: 2025-10-11
