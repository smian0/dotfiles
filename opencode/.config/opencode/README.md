# OpenCode with Ollama AI Provider v2 Configuration

This directory contains OpenCode configuration with advanced Ollama integration using `ollama-ai-provider-v2`.

## Current Setup

- **OpenCode Version**: 0.6.8
- **Provider**: ollama-ai-provider-v2@1.3.1 (latest)
- **Secure Wrapper**: `oc` command loads environment variables from system launchctl
- **Environment**: System-wide API key management via LaunchAgent
- **Direct Testing**: `test-ollama-turbo/` directory for provider experimentation

## Configuration Structure

```json
{
  "provider": {
    "ollamat": {
      "npm": "ollama-ai-provider-v2",
      "name": "Ollama (turbo)",
      "options": {
        "baseURL": "https://ollama.com/api",
        "headers": {
          "Authorization": "Bearer {env:OLLAMA_API_KEY}"
        },
        "options": {
          // Ollama-specific parameters here
        }
      },
      "models": {
        // Model definitions
      }
    }
  }
}
```

## Complete Provider Options Reference

### Core Provider Configuration

#### Base Connection Options
```json
{
  "baseURL": "https://ollama.com/api",  // Remote Ollama server
  "headers": {
    "Authorization": "Bearer {env:OLLAMA_API_KEY}",
    "X-Custom-Header": "value"
  }
}
```

#### Reasoning Mode (ollama-ai-provider-v2 Specific)
```json
{
  "options": {
    "think": true  // Enables chain-of-thought reasoning for supported models
  }
}
```

### Ollama Native Parameters (options.options)

#### Generation Control
```json
{
  "temperature": 0.7,        // Creativity (0.0-1.0, default: 0.8)
  "seed": 42,               // Deterministic output (any integer)
  "num_predict": 1024,      // Max tokens to generate (-1 = unlimited)
  "stop": ["END", "\n\n"]   // Stop sequences (array of strings)
}
```

#### Context & Memory
```json
{
  "num_ctx": 32768,         // Context window size (default: 2048-4096)
  "repeat_last_n": 64,      // Look-back for repetition check (default: 64)
  "repeat_penalty": 1.1     // Penalize repetition (default: 1.1)
}
```

#### Advanced Sampling
```json
{
  "top_k": 40,              // Top-k sampling (1-100, limits token choices)
  "top_p": 0.9,             // Top-p sampling (0.1-0.9, cumulative probability)
  "min_p": 0.05,            // Minimum probability threshold
  "tfs_z": 1.0,             // Tail-free sampling parameter
  "typical_p": 1.0          // Typical sampling parameter
}
```

#### Mirostat Sampling (Alternative to top_k/top_p)
```json
{
  "mirostat": 0,            // Enable Mirostat (0=disabled, 1=enabled, 2=v2)
  "mirostat_tau": 5.0,      // Target entropy (controls perplexity)
  "mirostat_eta": 0.1       // Learning rate for entropy adjustment
}
```

#### Penalty Controls
```json
{
  "presence_penalty": 0.0,   // Penalty for token presence (-2.0 to 2.0)
  "frequency_penalty": 0.0,  // Penalty for token frequency (-2.0 to 2.0)
  "penalize_newline": true   // Apply penalties to newlines
}
```

#### Performance & Hardware
```json
{
  "num_thread": 8,          // CPU threads (auto-detected if not set)
  "num_batch": 512,         // Batch size for processing
  "num_gpu": 1,             // Number of GPUs to use
  "main_gpu": 0,            // Primary GPU index
  "low_vram": false,        // Enable low VRAM mode
  "numa": false,            // Enable NUMA optimization
  "use_mmap": true,         // Use memory mapping
  "use_mlock": false,       // Lock memory pages
  "vocab_only": false       // Load vocabulary only
}
```

## Current Configuration Breakdown

### Our Optimized Settings
```json
{
  "options": {
    "seed": 42,               // Reproducible outputs
    "num_ctx": 32768,         // Large context window (32K tokens)
    "repeat_penalty": 1.1,    // Reduce repetition
    "top_k": 40,              // Quality sampling
    "min_p": 0.05,            // Probability filtering
    "temperature": 0.7,       // Balanced creativity
    "think": true             // Enhanced reasoning
  }
}
```

### Available Models
- **gpt-oss:20b** - GPT-OSS 20B (Fast)
- **gpt-oss:120b** - GPT-OSS 120B (High Quality)
- **deepseek-v3.1:671b** - DeepSeek V3.1 671B (Very Large)
- **deepseek-r1:7b** - DeepSeek R1 7B (Reasoning)*
- **deepseek-r1:1.5b** - DeepSeek R1 1.5B (Reasoning)*
- **deepseek-r1:8b** - DeepSeek R1 8B (Reasoning)*

*Reasoning models may not be available on hosted ollama.com service yet.

## Usage Examples

### Basic Usage
```bash
oc run 'Hello, world!' --model ollamat/gpt-oss:120b
```

### With Reasoning Mode
```bash
oc run 'Solve step by step: 2x + 5 = 17' --model ollamat/gpt-oss:120b
```

### Interactive Mode
```bash
oc  # Start interactive session
```

## Direct Provider Testing

The `test-ollama-turbo/` directory contains a standalone testing suite for experimenting with ollama-ai-provider-v2 without OpenCode overhead.

```bash
# Navigate to testing directory
cd test-ollama-turbo/

# Basic testing
node test-ollama.mjs "Your prompt here"

# Test different presets
node test-ollama.mjs "Solve 2x + 5 = 17" reasoning
node test-ollama.mjs "Write a creative story" creative
node test-ollama.mjs "Debug this function" code
node test-ollama.mjs "Quick answer" fast

# Use npm scripts
npm run test-reasoning
npm run test-creative
npm run test-code
npm run help
```

**Benefits:**
- 🚀 Direct provider access (faster than OpenCode)
- ⚙️ All 50+ configuration options available
- 📊 Performance metrics (response time, length)
- 🧪 6 presets for different use cases
- 📝 Easy experimentation by editing presets

## Environment Setup

### System-wide Environment Variables
Managed via LaunchAgent (`/Users/smian/dotfiles/mcp-launcher/Library/LaunchAgents/com.smian.mcp-env.plist`):

- `OLLAMA_API_KEY` - Ollama.com hosted API key
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GITHUB_TOKEN` - GitHub API token
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `GLM_API_KEY` - GLM API key
- `KIMI_API_KEY` - Kimi API key
- `BRAVE_API_KEY` - Brave Search API key

### Secure Wrapper Script
The `oc` command (`/Users/smian/dotfiles/bin/oc`) automatically loads environment variables from system launchctl before launching OpenCode.

## Customization Tips

### For Coding Tasks
```json
{
  "temperature": 0.3,       // More deterministic
  "repeat_penalty": 1.2,    // Reduce code repetition
  "num_ctx": 16384          // Large context for code
}
```

### For Creative Writing
```json
{
  "temperature": 0.9,       // More creative
  "top_p": 0.8,             // Diverse sampling
  "repeat_penalty": 1.05    // Allow some repetition
}
```

### For Analysis/Reasoning
```json
{
  "think": true,            // Enable reasoning mode
  "temperature": 0.6,       // Balanced
  "num_ctx": 32768,         // Large context
  "seed": 42                // Reproducible results
}
```

## Troubleshooting

### Common Issues

1. **"Unauthorized" Error**
   - Check: `launchctl getenv OLLAMA_API_KEY`
   - Solution: Run MCP environment setup script

2. **"Not Found" Model Error**
   - Check: `oc models | grep model-name`
   - Solution: Use available models or switch to local Ollama

3. **Slow Responses**
   - Reduce `num_ctx` for faster responses
   - Use smaller models (gpt-oss:20b vs 120b)

### Debug Mode
Enable debug output in `oc` script:
```bash
# Edit /Users/smian/dotfiles/bin/oc
DEBUG_MODE=true
```

## Links & References

- [ollama-ai-provider-v2 GitHub](https://github.com/nordwestt/ollama-ai-provider-v2)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenCode Documentation](https://opencode.ai/docs/)
- [AI SDK Documentation](https://sdk.vercel.ai/docs)

---

**Last Updated**: September 10, 2025  
**Configuration Path**: `/Users/smian/dotfiles/opencode/.config/opencode/opencode.json`  
**Environment Script**: `/Users/smian/dotfiles/scripts/mcp-env/mcp-env/set-mcp-env-system.sh`