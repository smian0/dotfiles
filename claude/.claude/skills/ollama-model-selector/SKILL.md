---
name: ollama-model-selector
description: Recommend optimal Ollama cloud models based on task requirements (coding, reasoning, vision). Auto-loads when users ask about model selection.
---

# Ollama Model Selector

**Purpose**: Recommend the best Ollama cloud model for a given task by analyzing requirements and matching to verified model capabilities.

## When to Use This Skill

**Auto-trigger** when users ask questions like:
- "Which Ollama model should I use?"
- "What's the best model for [coding/reasoning/vision/etc.]?"
- "Which model is fastest/most accurate?"
- "Compare model A vs model B"
- "I need a model with large context"

**Manual invocation** for standalone CLI use:
```bash
openskills read ollama-model-selector
```

## How It Works

This skill provides two modes of operation:

### 1. Claude Consultation Mode (Primary)

When Claude loads this skill to answer user questions:

**Step 1: Run the selector with JSON output**
```bash
python3 selector.py --task <task> --priority <priority> --format json
```

**Step 2: Parse the JSON response**
- `recommendations[]`: Top 3 models ranked by score
- `all_models[]`: Full model table for reference
- `reasoning`: Explanation of selection criteria

**Step 3: Present to user**
- Lead with the top recommendation
- Explain WHY it was chosen (speed, context, capabilities)
- Show alternatives for different trade-offs
- Reference the model table from `performance_data.json`

### 2. Standalone CLI Mode (Secondary)

Users can run the selector directly for quick lookups:

```bash
# Find best model for a task
python3 selector.py --task coding --priority speed

# List all available models
python3 selector.py --list

# Compare specific models
python3 selector.py --compare "glm-4.6:cloud" "qwen3-coder:480b-cloud"

# Refresh model data from Ollama API
python3 selector.py --update
```

## Selection Criteria

The skill evaluates models using three weighted factors:

1. **Task Matching (40%)**: How well the model's capabilities align with the task
2. **Context Window (20%)**: Whether the context size meets requirements
3. **Performance Priority (40%)**: Speed vs. accuracy trade-offs

See [model-selection-criteria.md](./references/model-selection-criteria.md) for detailed algorithm and scoring.

## Data Source

**Primary**: `performance_data.json`
- Verified token speeds from actual testing
- Maintained and version-controlled
- Fast local access

**Secondary**: Ollama API via `model_fetcher.py`
- Fetch latest model availability
- Use `--update` flag to refresh cache
- Merges API data with verified performance metrics

## Command Options

| Option | Values | Description |
|--------|--------|-------------|
| `--task` | coding, reasoning, vision, general | Task type to optimize for |
| `--priority` | speed, accuracy, balanced | Performance priority |
| `--context` | small, medium, large | Context window requirement |
| `--format` | text, json | Output format (json for Claude) |
| `--list` | flag | List all models with specs |
| `--compare` | model1 model2 ... | Compare specific models |
| `--update` | flag | Refresh data from Ollama API |

## Example Recommendations

**User: "Which model should I use for full-stack coding?"**

Claude loads skill → Runs:
```bash
python3 selector.py --task coding --priority balanced --format json
```

Returns:
```json
{
  "recommendations": [
    {"model": "glm-4.6:cloud", "score": 0.88, "reason": "Highest speed (69 tok/s), optimized for full-stack development"},
    {"model": "qwen3-coder:480b-cloud", "score": 0.82, "reason": "Best coding specialist, large context (256K)"},
    {"model": "gpt-oss:120b-cloud", "score": 0.76, "reason": "Fastest overall (60 tok/s), good for general coding"}
  ]
}
```

**User: "I need a model with a large context window for analyzing a huge codebase"**

Claude loads skill → Runs:
```bash
python3 selector.py --task coding --context large --format json
```

Returns models with 256K context: `kimi-k2:1t-cloud`, `qwen3-coder:480b-cloud`, `kimi-k2-thinking:cloud`

## Integration with Claude

When this skill is loaded:

1. Claude checks if the question is about model selection
2. Maps user intent to selector parameters (task, priority, context)
3. Runs `selector.py` with `--format json`
4. Parses the structured response
5. Presents recommendations with clear reasoning
6. References the full model table from `performance_data.json`

This ensures recommendations are:
- ✅ Data-driven (verified performance metrics)
- ✅ Explainable (clear reasoning provided)
- ✅ Current (refreshable from API)
- ✅ Comprehensive (shows trade-offs and alternatives)

## Files

- `selector.py`: Main recommendation engine
- `model_fetcher.py`: Ollama API integration for updates
- `performance_data.json`: Verified model performance data
- `references/model-selection-criteria.md`: Detailed selection algorithm
- `scripts/benchmark_models.py`: Performance testing tool

## Benchmarking

**Verify model speeds with actual testing**:

```bash
# Test all models (takes ~5-10 minutes)
python3 scripts/benchmark_models.py

# Test specific models only
python3 scripts/benchmark_models.py --models "glm-4.6:cloud" "qwen3-coder:480b-cloud"

# Run multiple times for accuracy (takes longer)
python3 scripts/benchmark_models.py --runs 3

# Update performance_data.json with new measurements
python3 scripts/benchmark_models.py --update
```

The benchmark script:
- Connects to Ollama at `localhost:11434`
- Sends a consistent test prompt to each model
- Measures actual tokens/second performance
- Compares with current data in `performance_data.json`
- Optionally updates the data file

**When to benchmark**:
- After Ollama updates
- When performance seems different
- To verify new cloud models
- Monthly maintenance check

See [scripts/README.md](./scripts/README.md) for detailed usage, example output, and accuracy tips.

## Maintenance

**To update model availability from Ollama API**:
```bash
python3 selector.py --update
```

This fetches latest models from Ollama API and merges with verified performance data in `performance_data.json`.
