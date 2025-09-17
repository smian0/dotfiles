# Ollama Provider v2 Configuration Guide

This guide explains how to configure Ollama Provider v2 options for models like `gpt-oss:20b`, `gpt-oss:120b`, and `deepseek` in your OpenCode JSON configuration.

## Provider Configuration Translation

### From Nix to JSON Structure

The Nix configuration structure translates to JSON as follows:

**Nix Configuration:**
```nix
ollama-turbo = {
  name = "Ollama Turbo";
  npm = "ollama-ai-provider-v2";
  options = {
    baseURL = "https://ollama.com/api";
    headers = {
      Authorization = "Bearer ${keys.ollama}";
    };
  };
};
```

**JSON Configuration:**
```json
{
  "provider": {
    "ollama-turbo": {
      "name": "Ollama Turbo",
      "npm": "ollama-ai-provider-v2",
      "options": {
        "baseURL": "https://ollama.com/api",
        "headers": {
          "Authorization": "Bearer {env:OLLAMA_API_KEY}"
        }
      }
    }
  }
}
```

## Model Configuration Options

### Base Model Structure

Each model in the Ollama Provider v2 can have these configuration options:

```json
{
  "models": {
    "model-name": {
      "id": "actual-model-id",
      "name": "Display Name",
      "options": {
        "reasoningEffort": "low|medium|high",
        "think": "low|medium|high",
        "effort": "low|medium|high",
        "reasoning_effort": "low|medium|high"
      },
      "limit": {
        "context": 131072,
        "output": 131072
      },
      "attachment": false,
      "reasoning": true,
      "temperature": true,
      "tool_call": true
    }
  }
}
```

### Reasoning Effort Options

The reasoning effort can be controlled through multiple equivalent parameters:
- `reasoningEffort`: Standard parameter
- `think`: Alias for reasoning effort  
- `effort`: Another alias
- `reasoning_effort`: Snake_case variant

**Values:** `"low"`, `"medium"`, `"high"`

## Complete Model Configurations

### GPT-OSS 20B Configuration

```json
{
  "provider": {
    "ollama-turbo": {
      "models": {
        "gpt-oss:20b": {
          "id": "gpt-oss:20b",
          "name": "GPT-OSS 20B (High Effort)",
          "options": {
            "reasoningEffort": "high",
            "think": "high",
            "effort": "high",
            "reasoning_effort": "high"
          },
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        }
      }
    }
  }
}
```

### GPT-OSS 120B Configuration

```json
{
  "provider": {
    "ollama-turbo": {
      "models": {
        "gpt-oss:120b": {
          "id": "gpt-oss:120b", 
          "name": "GPT-OSS 120B (High Effort)",
          "options": {
            "reasoningEffort": "high",
            "think": "high",
            "effort": "high", 
            "reasoning_effort": "high"
          },
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        }
      }
    }
  }
}
```

### DeepSeek V3.1 Configuration

```json
{
  "provider": {
    "ollama-turbo": {
      "models": {
        "deepseek-v3.1:671b": {
          "id": "deepseek-v3.1:671b",
          "name": "DeepSeek V3.1 671B",
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        }
      }
    }
  }
}
```

### Qwen3 Coder Configuration (Ollama Turbo)

```json
{
  "provider": {
    "ollama-turbo": {
      "models": {
        "qwen3-coder:480b": {
          "id": "qwen3-coder:480b",
          "name": "Qwen3 Coder 480B",
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        }
      }
    }
  }
}
```

## Alternative Provider Configurations

### ZhipuAI Provider (GLM Models)

```json
{
  "provider": {
    "zhipuai": {
      "name": "ZhipuAI",
      "api": "https://api.z.ai/api/coding/paas/v4",
      "options": {
        "apiKey": "{env:ZAI_API_KEY}"
      },
      "models": {
        "glm-4.5": {
          "name": "GLM-4.5",
          "limit": {
            "context": 131072,
            "output": 98304
          },
          "temperature": true,
          "tool_call": true,
          "reasoning": true
        }
      }
    }
  }
}
```

### Cerebras Provider (Qwen3 Models)

```json
{
  "provider": {
    "cerebras": {
      "name": "Cerebras",
      "options": {
        "apiKey": "{env:CEREBRAS_API_KEY}"
      },
      "models": {
        "qwen-3-coder-480b": {
          "name": "Qwen 3 Coder 480B",
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "temperature": true,
          "tool_call": true,
          "reasoning": true
        }
      }
    }
  }
}
```

## Small vs Big Model Strategy

The Nix configuration uses a smart **small/big model strategy** with different reasoning efforts:

- **Small Model (20B)**: Fast responses, lower compute cost, good for quick tasks
- **Big Model (120B)**: Higher quality responses, more reasoning power, better for complex tasks
- **Effort Levels**: `low`, `medium`, `high` - controls reasoning depth

### Model Selection Strategy

```javascript
// Use cases for different model sizes:
"gpt-oss:20b"  → Quick responses, simple tasks, iteration speed
"gpt-oss:120b" → Complex reasoning, detailed analysis, final outputs
```

### ❌ Custom Model Names Don't Work

**Tested Approaches That FAIL:**

```json
// ❌ This shows in UI but API returns "Not Found"
"gpt-oss:20b-fast": {
  "id": "gpt-oss:20b",        // API doesn't recognize custom names
  "options": { "reasoningEffort": "low" }
}

// ❌ This also fails - API looks at model name, not ID
"gpt-oss:20b-test": {  
  "id": "gpt-oss:20b",        // Same issue
  "options": { "reasoningEffort": "medium" }
}
```

**Why This Doesn't Work:**
- Ollama.com API only recognizes exact model names: `gpt-oss:20b`, `gpt-oss:120b`
- Custom names in OpenCode config get passed directly to API
- API doesn't look at the `"id"` field - it uses the model name from the URL

### ✅ Working Solution: Agent-Based Configuration

Instead of custom model names, use **agent-level reasoning configuration**:

```json
{
  "agent": {
    "fast": {
      "model": "ollamat/gpt-oss:20b",
      "reasoningEffort": "low",
      "system": "Quick, direct responses"
    },
    "reasoning": {
      "model": "ollamat/gpt-oss:120b", 
      "reasoningEffort": "high",
      "system": "Step-by-step mathematical reasoning"
    },
    "general": {
      "model": "ollamat/gpt-oss:20b",
      "reasoningEffort": "medium", 
      "system": "Balanced responses"
    }
  }
}
```

## Complete Provider Configuration Example

Here's how to add the complete Ollama Turbo provider with the small/big strategy to your `opencode.json`:

```json
{
  "provider": {
    "ollama-turbo": {
      "name": "Ollama Turbo",
      "npm": "ollama-ai-provider-v2", 
      "options": {
        "baseURL": "https://ollama.com/api",
        "headers": {
          "Authorization": "Bearer {env:OLLAMA_API_KEY}"
        }
      },
      "models": {
        "gpt-oss:20b": {
          "id": "gpt-oss:20b",
          "name": "GPT-OSS 20B (High Effort)",
          "options": {
            "reasoningEffort": "high",
            "think": "high",
            "effort": "high",
            "reasoning_effort": "high"
          },
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        },
        "gpt-oss:120b": {
          "id": "gpt-oss:120b",
          "name": "GPT-OSS 120B (High Effort)", 
          "options": {
            "reasoningEffort": "high",
            "think": "high",
            "effort": "high",
            "reasoning_effort": "high"
          },
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        },
        "deepseek-v3.1:671b": {
          "id": "deepseek-v3.1:671b",
          "name": "DeepSeek V3.1 671B",
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        },
        "qwen3-coder:480b": {
          "id": "qwen3-coder:480b",
          "name": "Qwen3 Coder 480B",
          "limit": {
            "context": 131072,
            "output": 131072
          },
          "attachment": false,
          "reasoning": true,
          "temperature": true,
          "tool_call": true
        }
      }
    }
  }
}
```

## Model Capability Flags

- `attachment`: Whether model supports file attachments (typically `false`)
- `reasoning`: Whether model supports reasoning modes (`true`)
- `temperature`: Whether model supports temperature control (`true`)  
- `tool_call`: Whether model supports function calling (`true`)

## Using Models in Agent Configuration

The **small/big model strategy** works perfectly with agent specialization. Here's how to map your Nix agent pattern to JSON:

### From Nix Agent Strategy
```nix
agent = {
  plan = { model = gpt; };           # gpt = "ollama-turbo/gpt-oss:120b" 
  build = { model = glm; };          # glm = "zhipuai/glm-4.5"
  general = { model = qwen; };       # qwen = "cerebras/qwen-3-coder-480b"
};
```

### To JSON Agent Strategy
```json
{
  "agent": {
    "plan": {
      "model": "ollama-turbo/gpt-oss:120b",
      "description": "Strategic planning with deep reasoning",
      "reasoningEffort": "high"
    },
    "build": {
      "model": "zhipuai/glm-4.5",
      "description": "Code generation and building"
    },
    "general": {
      "model": "cerebras/qwen-3-coder-480b", 
      "description": "General purpose coding tasks"
    },
    "fast": {
      "model": "ollama-turbo/gpt-oss:20b-fast",
      "description": "Quick responses and iterations"
    },
    "reasoning": {
      "model": "ollama-turbo/gpt-oss:120b",
      "description": "Complex analysis and problem solving",
      "reasoningEffort": "high"
    },
    "debug": {
      "model": "ollama-turbo/gpt-oss:120b-balanced",
      "description": "Debugging with balanced speed/quality"
    }
  }
}
```

### Smart Model Selection by Task Type

**Fast Tasks** (`gpt-oss:20b-fast`):
- Quick iterations
- Simple questions  
- Code formatting
- Basic explanations

**Balanced Tasks** (`gpt-oss:20b` or `gpt-oss:120b-balanced`):
- Code reviews
- Documentation
- Refactoring
- Testing

**Deep Analysis** (`gpt-oss:120b`):
- Architecture decisions
- Complex debugging
- Strategic planning
- Performance optimization

## Environment Variables Required

Make sure to set the appropriate API keys:

```bash
# For Ollama Turbo
export OLLAMA_API_KEY="your-ollama-api-key"

# For ZhipuAI (GLM models)
export ZAI_API_KEY="your-zai-api-key"

# For Cerebras (Qwen models)  
export CEREBRAS_API_KEY="your-cerebras-api-key"
```

## Agent File Configuration

### Proper Agent File Pattern

Agent files (`.opencode/agent/*.md`) **cannot reference other agent configurations** in the model field. They must use direct provider/model format with explicit parameters.

#### ❌ This Doesn't Work
```yaml
---
description: Fast agent
model: fast  # Cannot reference agent config
---
```

#### ✅ Correct Agent File Patterns

**Fast Model Configuration:**
```yaml
---
description: Fast responses with low reasoning effort
model: ollamat/gpt-oss:20b
reasoningEffort: low
---
You are a fast assistant. Provide quick, direct answers.
```

**High-Quality Reasoning Configuration:**
```yaml
---
description: Deep reasoning with high effort
model: ollamat/gpt-oss:120b
reasoningEffort: high
---
You are a reasoning assistant. Provide step-by-step analysis.
```

**Balanced Configuration:**
```yaml
---
description: Balanced performance
model: ollamat/gpt-oss:20b
reasoningEffort: medium
---
You provide balanced responses with moderate reasoning depth.
```

### Agent File Small/Big Model Strategy

To implement the small/big model strategy in agent files, create separate agents for different use cases:

**agents/fast.md:**
```yaml
---
description: Quick responses for simple tasks
model: ollamat/gpt-oss:20b
reasoningEffort: low
temperature: 0.3
---
You are optimized for speed. Give concise, direct answers.
```

**agents/reasoning.md:**
```yaml
---
description: Deep analysis for complex problems  
model: ollamat/gpt-oss:120b
reasoningEffort: high
temperature: 0.5
---
You provide thorough step-by-step reasoning and detailed analysis.
```

**agents/coding.md:**
```yaml
---
description: Code generation and debugging
model: ollamat/gpt-oss:120b
reasoningEffort: medium
temperature: 0.2
---
You are a precise coding assistant focused on clean, working code.
```

### Usage Examples

```bash
# Use fast agent for quick tasks
oc run --agent fast "What's 2+2?"

# Use reasoning agent for complex problems
oc run --agent reasoning "Analyze the trade-offs between microservices and monolithic architecture"

# Use coding agent for development
oc run --agent coding "Write a Python function to validate email addresses"
```

### Key Rules for Agent Files

1. **Direct Model References**: Always use `provider/model` format
2. **Explicit Parameters**: Include `reasoningEffort`, `temperature` directly in frontmatter  
3. **No Agent Inheritance**: Cannot reference other agents in configuration
4. **Parameter Override**: Agent-level parameters override provider defaults

## Verification: reasoningEffort Parameter Works

### Test Results Confirming Parameter Effectiveness

**Tested Configuration:**
```yaml
---
description: Test agent using fast model (20B with low effort)
model: ollamat/gpt-oss:20b
reasoningEffort: low  # vs high
---
```

**Test Query:** *"What are the pros and cons of using microservices vs monolithic architecture? Consider scalability, maintenance, and team coordination."*

### Response Quality Comparison

| Aspect | `reasoningEffort: low` | `reasoningEffort: high` |
|--------|------------------------|-------------------------|
| **Response Length** | ~1,200 words | ~2,500+ words |
| **Structure** | 6 main categories | 9+ comprehensive categories |
| **Detail Level** | Focused, practical points | In-depth analysis with sub-categories |
| **Additional Content** | Basic comparison table | + Governance, Compliance, Speed to Market, Cost analysis |
| **Recommendations** | Simple bottom-line advice | Detailed decision matrix + migration guidance |
| **Tables** | 3 clean comparison tables | 4+ tables including decision framework |
| **Depth** | Surface-level coverage | Deep architectural considerations |

### Key Findings

✅ **Parameter is Respected**: The Ollama API correctly processes `reasoningEffort` settings

✅ **Significant Quality Difference**: Same model (`gpt-oss:20b`) produces notably different response depths

✅ **Both Responses Useful**: Even "low" effort provides structured, valuable information - just more focused

✅ **Consistent Behavior**: Multiple test queries showed consistent effort-level differences

### Practical Implications

**For Fast Tasks** (`reasoningEffort: low`):
- Quick iterations and brainstorming
- Simple questions with direct answers
- When response time matters more than depth
- Code formatting, basic explanations

**For Complex Tasks** (`reasoningEffort: high`):
- Architectural decisions requiring thorough analysis
- Comprehensive comparisons and trade-off discussions
- Strategic planning and detailed problem-solving
- Documentation requiring complete coverage

**Performance vs Quality Trade-off:**
```bash
# Fast responses for quick tasks
oc run --agent fast "What's the difference between REST and GraphQL?"

# Deep analysis for complex decisions  
oc run --agent reasoning "Should we migrate from REST to GraphQL? Consider our current architecture..."
```

### Mathematical Verification Example

**Low Effort Response:**
```
7 × 8 = 56
- Standard multiplication: 7 × 8 = 56
- Alternative: 7 + 7 + 7 + 7 + 7 + 7 + 7 + 7 = 56
```

**High Effort Response:**
```
5-step detailed explanation with:
- Conceptual understanding of multiplication
- Grouped addition methodology  
- Cross-verification using commutativity
- Mathematical notation formatting
- Multiple solution approaches
```

This confirms that the small/big model strategy with reasoning effort levels provides precise control over response depth and processing time.

## Key Differences from Local Ollama

- **URL**: Uses `https://ollama.com/api` instead of `http://localhost:3304/v1`
- **Authentication**: Requires Bearer token via `Authorization` header
- **NPM Package**: Uses `ollama-ai-provider-v2` instead of `@ai-sdk/openai-compatible`
- **Advanced Options**: Supports reasoning effort and other advanced parameters