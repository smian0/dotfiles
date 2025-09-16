# OpenCode Models Reference

## Overview

This document provides a consolidated reference for all AI models available in this OpenCode configuration. Use this as the source of truth for model information across all documentation.

## Provider Configuration

### Ollama Providers

#### Local Ollama (ollama)
- **Provider ID**: `ollama`
- **Base URL**: `http://localhost:3304/v1`
- **NPM Package**: `@ai-sdk/openai-compatible`
- **Authentication**: None (local)
- **Use Case**: Local inference, privacy, offline usage

#### Hosted Ollama (ollamat)
- **Provider ID**: `ollamat`
- **Base URL**: `https://ollama.com/api`
- **NPM Package**: `ollama-ai-provider-v2`
- **Authentication**: `OLLAMA_API_KEY` environment variable
- **Use Case**: Cloud inference, hosted models

#### ZhipuAI
- **Provider ID**: `zhipuai`
- **Base URL**: `https://api.z.ai/api/coding/paas/v4`
- **Authentication**: API key required
- **Use Case**: Default for transformed agents

## Available Models

### Confirmed Available (Ollama.com Hosted)
*Last verified: September 16, 2025*

#### gpt-oss:20b
- **Full ID**: `ollamat/gpt-oss:20b` (hosted) | `ollama/gpt-oss:20b` (local)
- **Name**: GPT-OSS 20B
- **Size**: 20 billion parameters
- **Characteristics**: Fast, efficient, good for quick tasks
- **Context Window**: Variable (check provider)
- **Best For**: 
  - Quick responses
  - Simple queries
  - Real-time interactions
  - When speed > quality

#### gpt-oss:120b
- **Full ID**: `ollamat/gpt-oss:120b` (hosted) | `ollama/gpt-oss:120b` (local)
- **Name**: GPT-OSS 120B
- **Size**: 120 billion parameters
- **Characteristics**: High quality, balanced performance
- **Context Window**: Variable (check provider)
- **Best For**:
  - Complex tasks
  - Code generation
  - Detailed analysis
  - Most general purpose work
- **Note**: Recommended default for most tasks

#### deepseek-v3.1:671b
- **Full ID**: `ollamat/deepseek-v3.1:671b` (hosted) | `ollama/deepseek-v3.1:671b` (local)
- **Name**: DeepSeek V3.1 671B
- **Size**: 671 billion parameters
- **Characteristics**: Very large, advanced reasoning capabilities
- **Context Window**: Variable (check provider)
- **Best For**:
  - Complex reasoning tasks
  - Advanced analysis
  - Research and exploration
  - When quality is paramount

### Additional Models (Configuration Ready)

#### qwen3-coder:480b
- **Full ID**: `ollamat/qwen3-coder:480b`
- **Name**: Qwen3 Coder 480B
- **Size**: 480 billion parameters
- **Characteristics**: Specialized for coding tasks
- **Context Window**: Variable (check provider)
- **Best For**:
  - Code generation
  - Programming tasks
  - Software development
  - Technical documentation
- **Availability**: May not be available on all providers

#### zhipuai/glm-4.5
- **Full ID**: `zhipuai/glm-4.5`
- **Name**: GLM-4.5
- **Provider**: ZhipuAI
- **Characteristics**: Default model for transformed agents
- **Best For**:
  - Automatic agent transformation
  - General purpose tasks
  - When using Claude → OpenCode agent conversion

## Model Selection Guidelines

### By Task Type

#### Quick Tasks / Chat
- **Recommended**: `gpt-oss:20b`
- **Settings**: Lower temperature (0.3-0.5), smaller context
- **Use Cases**: Simple questions, quick responses, real-time chat

#### General Purpose / Balanced
- **Recommended**: `gpt-oss:120b`
- **Settings**: Medium temperature (0.6-0.8), standard context
- **Use Cases**: Most tasks, code review, documentation, analysis

#### Complex Reasoning / Research
- **Recommended**: `deepseek-v3.1:671b`
- **Settings**: Lower temperature (0.3-0.6), large context
- **Use Cases**: Research, complex analysis, strategic planning

#### Coding / Development
- **Recommended**: `qwen3-coder:480b` (if available) or `gpt-oss:120b`
- **Settings**: Low temperature (0.1-0.4), large context
- **Use Cases**: Code generation, debugging, refactoring

### By Performance Requirements

#### Speed Priority
1. `gpt-oss:20b` - Fastest
2. `gpt-oss:120b` - Balanced
3. `deepseek-v3.1:671b` - Slower but higher quality

#### Quality Priority
1. `deepseek-v3.1:671b` - Highest quality
2. `gpt-oss:120b` - Good quality
3. `gpt-oss:20b` - Basic quality

## Model Configuration Examples

### Basic Usage
```bash
# Quick task
oc run "simple question" --model ollamat/gpt-oss:20b

# Balanced task
oc run "analyze this code" --model ollamat/gpt-oss:120b

# Complex task
oc run "deep analysis needed" --model ollamat/deepseek-v3.1:671b
```

### With Agents
```bash
# Use specific model with agent
oc run --agent claude-test-agent "message" --model ollamat/gpt-oss:120b

# Let agent use default model (zhipuai/glm-4.5 for transformed agents)
oc run --agent claude-test-agent "message"
```

### Provider Selection
```bash
# Use hosted models (requires API key)
oc run "message" --model ollamat/gpt-oss:120b

# Use local models (if running locally)
oc run "message" --model ollama/gpt-oss:120b
```

## Configuration Settings

### Recommended Settings by Model

#### gpt-oss:20b (Fast)
```json
{
  "temperature": 0.5,
  "num_ctx": 8192,
  "top_k": 30,
  "repeat_penalty": 1.1
}
```

#### gpt-oss:120b (Balanced)
```json
{
  "temperature": 0.7,
  "num_ctx": 16384,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "think": true
}
```

#### deepseek-v3.1:671b (Quality)
```json
{
  "temperature": 0.6,
  "num_ctx": 32768,
  "top_k": 50,
  "repeat_penalty": 1.1,
  "think": true
}
```

## Checking Model Availability

### Command Line
```bash
# List all available models
oc models

# List models from specific provider
oc models | grep ollamat
oc models | grep ollama

# Test specific model
oc run "test" --model ollamat/gpt-oss:120b
```

### Environment Check
```bash
# Check API key for hosted models
launchctl getenv OLLAMA_API_KEY

# Verify environment loading
DEBUG_MODE=true oc --version 2>&1 | grep "API_KEY"
```

## Troubleshooting

### Model Not Found
```bash
# Error: Model "model-name" not found
# Solutions:
1. Check available models: oc models
2. Verify provider prefix (ollamat/ vs ollama/)
3. Check API key for hosted models
4. Try alternative model
```

### Authentication Errors
```bash
# Error: Unauthorized
# Solutions:
1. Check API key: launchctl getenv OLLAMA_API_KEY
2. Verify environment setup
3. Test with local models first
```

### Performance Issues
```bash
# Slow responses
# Solutions:
1. Use smaller model (gpt-oss:20b vs 120b)
2. Reduce context size (num_ctx)
3. Lower temperature
4. Use local provider if available
```

## Provider Comparison

| Feature | Local (ollama) | Hosted (ollamat) | ZhipuAI |
|---------|----------------|------------------|---------|
| **API Key Required** | No | Yes | Yes |
| **Internet Required** | No | Yes | Yes |
| **Privacy** | High | Medium | Medium |
| **Speed** | Variable | Fast | Variable |
| **Model Selection** | Limited | Full | Limited |
| **Cost** | Hardware only | Usage-based | Usage-based |

## Updates and Maintenance

### Adding New Models
1. **Update this reference** first
2. **Test availability** with command line
3. **Update other documentation** files
4. **Test with agents** and commands

### Model Deprecation
1. **Check provider announcements**
2. **Update availability status**
3. **Provide migration recommendations**
4. **Update default configurations**

### Version History
- **September 16, 2025**: Created consolidated reference
- **September 10, 2025**: Original model list (README.md)

---

**Last Updated**: September 16, 2025  
**Source**: Ollama.com API, provider documentation, testing  
**Status**: 3 confirmed models, 2 additional configured  
**Default**: `gpt-oss:120b` for general use, `zhipuai/glm-4.5` for transformed agents