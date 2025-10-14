# Droid (Factory AI CLI) Configuration

This package configures the Factory AI CLI (droid) with custom models including Ollama cloud models and Z.AI's GLM-4.6 for local development.

## Models Configured

### Ollama Cloud Models (Local Gateway)
- **qwen3-coder [Online]** - 480B parameters (Factory recommended)
- **Kimi K2 [Online]** - 1T parameters (largest available) 
- **DeepSeek v3.1 [Online]** - 671B parameter model

### Hosted Models
- **GLM 4.6 Coding Plan** - High-performance coding model via Z.AI API (requires API key)

All models are configured with optimal settings for agentic coding tasks.

## Structure

```
droid/.factory/
└── config.json
```

## Setup

### Prerequisites

1. Install Ollama: https://ollama.com/download
2. Pull the Ollama cloud models: `ollama pull qwen3-coder:480b-cloud kimi-k2:1t-cloud deepseek-v3.1:671b-cloud`
3. Start Ollama: `ollama serve`
4. For GLM-4.6 model: Get API key from https://z.ai/ and replace "YOUR_ZAI_API_KEY" in config.json`

### Stow Installation

```bash
# Add this package to your dotfiles
stow droid
```

### Post-Installation

1. Open droid interactively: `droid`
2. Type `/model` to see the custom models list
3. Select your preferred model

## Models

### qwen3-coder:480b-cloud
Factory's recommended cloud model for agentic coding tasks. Excellent performance on software engineering problems.

### kimi-k2:1t-cloud  
The largest available cloud model with 1 trillion parameters. Best for the most complex reasoning tasks.

### deepseek-v3.1:671b-cloud
DeepSeek's flagship model optimized for coding and mathematical reasoning.

### glm-4.6 (GLM 4.6 Coding Plan)
High-performance coding model from Z.AI offering excellent coding performance comparable to Anthropic Sonnet 4. Requires Z.AI API key.

## Configuration

Each model is configured according to its requirements:

### Ollama Cloud Models (Local Gateway):
- Base URL: `http://localhost:11434/v1/`
- Provider: `generic-chat-completion-api`
- Max tokens: `128000` (128K context window)
- API key: `not-needed` (placeholder for local Ollama)

### GLM 4.6 Model (Remote API):
- Base URL: `https://api.z.ai/api/anthropic`
- Provider: `zai"
- Uses Z.AI's Claude-compatible API
- API key: Required (configured for GLM Coding Plan as noted in the blog)

## Troubleshooting

If models don't appear:
1. Ensure Ollama is running: `ollama serve`
2. Verify model is available: `ollama list`
3. Check config syntax: `python3 -m json.tool ~/.factory/config.json`
4. Restart droid to load new models

## Notes

- Cloud models are accessed through your local Ollama instance
- Models use Ollama's cloud compute infrastructure
- No API keys required for local Ollama setup
- Custom models only available in Factory CLI, not web platform
- GLM 4.6 model uses Z.AI's hosted service instead of Ollama
