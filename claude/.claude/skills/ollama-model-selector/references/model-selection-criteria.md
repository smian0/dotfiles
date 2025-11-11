# Ollama Model Selection Criteria

This document details the algorithm and criteria used to recommend Ollama cloud models based on user requirements.

## Selection Algorithm

The skill uses a weighted scoring algorithm with three main factors:

### 1. Task Matching (40% weight)

Evaluates how well a model's capabilities align with the task type:

**Coding Tasks**
- Prioritizes: `qwen3-coder:480b-cloud`, `glm-4.6:cloud`
- Weights: coding=1.0, reasoning=0.6, vision=0.0

**Reasoning Tasks**
- Prioritizes: `deepseek-v3.1:671b-cloud`, `kimi-k2:1t-cloud`
- Weights: coding=0.4, reasoning=1.0, vision=0.0

**Vision Tasks**
- Prioritizes: `qwen3-vl:235b-cloud`
- Weights: coding=0.2, reasoning=0.4, vision=1.0

**General Tasks**
- Balanced across capabilities
- Weights: coding=0.5, reasoning=0.7, vision=0.3

### 2. Context Window Matching (20% weight)

Considers the model's context window size relative to requirements:

- **Small context** (<128K): Suitable for short conversations, quick queries
- **Medium context** (128K-198K): Suitable for most tasks
- **Large context** (≥256K): Required for long documents, complex codebases, multi-turn analysis

**Scoring:**
- 256K+ models: Full score for large context requirements
- 128K-198K models: Partial score (0.5) for all requirements
- <128K models: Score only for explicitly small context needs

### 3. Performance Priority (40% weight)

Balances speed vs. accuracy based on user priority:

**Speed Priority**
- Favors high tok/s models: `glm-4.6:cloud` (69 tok/s), `gpt-oss:120b-cloud` (60 tok/s)
- Weights: speed=1.0, accuracy=0.6

**Accuracy Priority**
- Favors larger, more capable models (inverse correlation with speed)
- Weights: speed=0.4, accuracy=1.0

**Balanced Priority** (default)
- Equal consideration for both
- Weights: speed=0.7, accuracy=0.7

## Scoring Formula

```
final_score = (task_score × 0.4) + (context_score × 0.2) + (priority_score × 0.4)
```

Where:
- `task_score`: Model's capability match for the task type
- `context_score`: Context window adequacy
- `priority_score`: Speed vs. accuracy alignment

## Model Capability Matrix

| Model | Speed | Context | Best For | Strengths |
|-------|-------|---------|----------|-----------|
| `gpt-oss:120b-cloud` | 60 tok/s | 128K | General purpose | Fastest for high-throughput tasks |
| `glm-4.6:cloud` | 69 tok/s | 198K | Advanced coding | Highest speed, excellent for full-stack dev |
| `deepseek-v3.1:671b-cloud` | 50 tok/s | 160K | Reasoning | Hybrid thinking mode, balanced |
| `kimi-k2:1t-cloud` | 39 tok/s | 256K | Complex reasoning | 1T MoE, largest context |
| `kimi-k2-thinking:cloud` | 22 tok/s | 256K | Autonomous tasks | Tool orchestration, 200-300 tool calls |
| `qwen3-coder:480b-cloud` | 34 tok/s | 256K | Code generation | Best for real-time coding help |
| `minimax-m2:cloud` | 25 tok/s | 204K | Development workflows | Cost-effective, good tool support |
| `qwen3-vl:235b-cloud` | 14 tok/s | 256K | Vision tasks | Multimodal, 32-language OCR |

## Speed vs. Accuracy Trade-offs

**High Speed (50+ tok/s)**
- `glm-4.6:cloud`, `gpt-oss:120b-cloud`, `deepseek-v3.1:671b-cloud`
- Best for: Interactive coding, rapid prototyping, time-sensitive tasks
- Trade-off: May sacrifice some depth for speed

**Balanced (25-40 tok/s)**
- `kimi-k2:1t-cloud`, `qwen3-coder:480b-cloud`, `minimax-m2:cloud`
- Best for: Most production workflows, balanced quality and speed
- Trade-off: Moderate wait times for better accuracy

**High Accuracy (14-22 tok/s)**
- `kimi-k2-thinking:cloud`, `qwen3-vl:235b-cloud`
- Best for: Complex reasoning, autonomous agents, vision analysis
- Trade-off: Slower but more thorough and capable

## Context Window Considerations

**When to Use Large Context (256K)**
- Multi-file codebase analysis
- Long document comprehension (technical docs, research papers)
- Multi-turn conversations requiring full history
- Complex planning requiring extensive context

**When Medium Context (128K-198K) Is Sufficient**
- Single-file or module-level code analysis
- Standard conversations
- Most API documentation lookups
- Typical development tasks

**When Small Context (<128K) Works**
- Quick queries and lookups
- Single-function implementations
- Fast research and content generation

## Use Case Examples

**Full-Stack Development Project**
- Recommended: `glm-4.6:cloud`
- Reasoning: Highest speed (69 tok/s), 198K context, optimized for full-stack work

**Large Codebase Refactoring**
- Recommended: `kimi-k2:1t-cloud` or `qwen3-coder:480b-cloud`
- Reasoning: 256K context for seeing full codebase, specialized for code

**Multi-Step Agentic Workflow**
- Recommended: `kimi-k2-thinking:cloud`
- Reasoning: Tool orchestration capabilities, autonomous problem-solving

**Image Analysis & OCR**
- Recommended: `qwen3-vl:235b-cloud`
- Reasoning: Only multimodal model, 32-language OCR support

## Data Source & Freshness

**Primary Source**: `performance_data.json`
- Verified token speeds from actual testing
- Last updated: Check file metadata
- Refresh via: `selector.py --update`

**API Source**: Ollama API
- Fetches latest model availability
- Use for: Discovering new models
- Merge with verified performance data

## Recommendations Output Format

When consulted by Claude, the skill outputs:

1. **Top 3 Recommendations**: Ranked by score with explanation
2. **Full Model Table**: All models with specs for reference
3. **Selection Reasoning**: Why each model was chosen/rejected

This allows Claude to make informed decisions while providing transparency to the user.
