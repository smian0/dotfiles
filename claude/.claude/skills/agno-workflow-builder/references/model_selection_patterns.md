# Data-Driven Model Selection for Workflows

## Overview

Choose optimal Ollama models for each workflow agent based on **task type, speed requirements, and context needs**. 

Use the `ollama-model-selector` skill for data-driven recommendations instead of guessing.

---

## CRITICAL: Consult ollama-model-selector Skill

**Before hardcoding models, ALWAYS consult:**

```bash
# Skill location
@ollama-model-selector

# Or direct path
/Users/smian/dotfiles/claude/.claude/skills/ollama-model-selector/SKILL.md
```

**Why:** 
- Provides **data-driven** recommendations based on actual performance metrics
- Considers speed (tok/s), context windows, and task-specific strengths
- Keeps you updated with latest model releases
- Prevents suboptimal choices

---

## General Guidelines

### Task-Based Model Selection

| Task Type | Recommended Model | Speed | Context | Why |
|-----------|-------------------|-------|---------|-----|
| **Parsing/Extraction** | `glm-4.6:cloud` | 192 tok/s | 198K | Fastest, excellent for quick parsing |
| **Validation/Reasoning** | `deepseek-v3.1:671b-cloud` | 76 tok/s | 160K | Hybrid thinking mode, balanced |
| **Tool Execution** | `glm-4.6:cloud` | 192 tok/s | 198K | Fast tool calling, good context |
| **Complex Reasoning** | `deepseek-v3.1:671b-cloud` | 76 tok/s | 160K | Deep analysis, multi-step thinking |
| **Code Generation** | `qwen3-coder:480b-cloud` | 54 tok/s | 256K | Best for coding tasks |
| **High Throughput** | `gpt-oss:120b-cloud` | 114 tok/s | 128K | Fastest for volume processing |

---

## Real-World Pattern: 3-Step Workflow

**Example:** Xero API Operations (Parse → Validate → Execute)

### Agent 1: Parser (Speed Priority)
```python
parser = Agent(
    name="Query Parser",
    model=Ollama(
        id="glm-4.6:cloud",      # 192 tok/s - fastest
        options={"num_ctx": 198000}
    ),
    output_schema=ParsedQuery,
    instructions="Parse user query into structured operation..."
)
```

**Why `glm-4.6:cloud`:**
- ✅ Fastest model (192 tok/s)
- ✅ Large context (198K) handles complex queries
- ✅ Simple extraction task doesn't need deep reasoning
- ✅ First step - speed matters for user experience

### Agent 2: Validator (Reasoning Priority)
```python
validator = Agent(
    name="Parameter Validator",
    model=Ollama(
        id="deepseek-v3.1:671b-cloud",  # 76 tok/s - reasoning
        options={"num_ctx": 160000}
    ),
    output_schema=ValidationResult,
    instructions="Validate operation against API requirements..."
)
```

**Why `deepseek-v3.1:671b-cloud`:**
- ✅ Hybrid thinking mode for validation logic
- ✅ Balanced reasoning for complex rule checking
- ✅ 160K context handles API schemas
- ✅ Worth slower speed for correctness

### Agent 3: Executor (Tool Calling Priority)
```python
executor = Agent(
    name="API Executor",
    model=Ollama(
        id="glm-4.6:cloud",      # 192 tok/s - fast tools
        options={"num_ctx": 198000}
    ),
    tools=[api_tools],
    instructions="Execute validated API operation..."
)
```

**Why `glm-4.6:cloud` (again):**
- ✅ Excellent tool calling support
- ✅ Fast execution for responsive API calls
- ✅ Large context for API responses
- ✅ Final step - speed improves overall latency

---

## Model Selection Decision Tree

```
Start
  ↓
Does task require deep reasoning?
  ↓
  Yes → deepseek-v3.1:671b-cloud (76 tok/s, hybrid thinking)
  ↓
  No → Does task use tools?
    ↓
    Yes → glm-4.6:cloud (192 tok/s, excellent tools)
    ↓
    No → Is speed critical?
      ↓
      Yes → gpt-oss:120b-cloud (114 tok/s, fastest)
      ↓
      No → Is task coding-specific?
        ↓
        Yes → qwen3-coder:480b-cloud (54 tok/s, code-focused)
        ↓
        No → glm-4.6:cloud (192 tok/s, general purpose)
```

---

## Performance vs Accuracy Tradeoff

### Speed-Optimized Workflow
```python
# All agents use fastest model
parser = Agent(model=Ollama(id="glm-4.6:cloud"))      # 192 tok/s
validator = Agent(model=Ollama(id="glm-4.6:cloud"))   # 192 tok/s
executor = Agent(model=Ollama(id="glm-4.6:cloud"))    # 192 tok/s

# Total: ~8-12s for 3 steps (fast user experience)
```

**Use when:**
- User experience requires sub-10s response
- Tasks are straightforward (parsing, simple validation)
- High request volume (API serving)

### Accuracy-Optimized Workflow
```python
# Use best model for each task type
parser = Agent(model=Ollama(id="glm-4.6:cloud"))               # 192 tok/s - parsing
validator = Agent(model=Ollama(id="deepseek-v3.1:671b-cloud")) # 76 tok/s - reasoning
executor = Agent(model=Ollama(id="glm-4.6:cloud"))             # 192 tok/s - tools

# Total: ~12-18s for 3 steps (better accuracy)
```

**Use when:**
- Correctness more important than speed
- Complex validation logic
- Multi-step reasoning required
- Batch processing (latency less critical)

### Balanced Workflow (Recommended)
```python
# Fast for simple steps, powerful for critical steps
parser = Agent(model=Ollama(id="glm-4.6:cloud"))               # Fast parsing
validator = Agent(model=Ollama(id="deepseek-v3.1:671b-cloud")) # Careful validation
executor = Agent(model=Ollama(id="glm-4.6:cloud"))             # Fast execution

# Total: ~10-15s (good balance)
```

**Use when:**
- Default choice for most workflows
- Need both speed and accuracy
- Critical step requires reasoning (validation)
- Other steps are straightforward

---

## Context Window Considerations

### Match Model Context to Data Size

```python
# Small context needed (< 50K tokens)
agent = Agent(model=Ollama(
    id="gpt-oss:120b-cloud",        # 128K context
    options={"num_ctx": 128000}
))

# Medium context needed (50K-150K tokens)
agent = Agent(model=Ollama(
    id="deepseek-v3.1:671b-cloud",  # 160K context
    options={"num_ctx": 160000}
))

# Large context needed (150K+ tokens)
agent = Agent(model=Ollama(
    id="glm-4.6:cloud",              # 198K context
    options={"num_ctx": 198000}
))

# Extra large context (250K+ tokens)
agent = Agent(model=Ollama(
    id="qwen3-coder:480b-cloud",     # 256K context
    options={"num_ctx": 256000}
))
```

**Tip:** Don't use larger context than needed - it's slower and wastes resources.

---

## Consulting ollama-model-selector Skill

### Example Query Pattern

```markdown
Task: Create a 3-step workflow for API operations
- Step 1: Parse natural language query
- Step 2: Validate against API schema
- Step 3: Execute API call with tools

Requirements:
- Priority: Balanced (speed + accuracy)
- Context: Medium (API schemas ~50K tokens)
- Tools: Yes (MCP server)

Consultation:
@ollama-model-selector
Which models should I use for each step?
```

### Expected Recommendation

The skill will provide:
1. **Model suggestions** based on task type
2. **Performance metrics** (tok/s, context)
3. **Rationale** for each choice
4. **Alternative options** if different priorities

---

## Common Anti-Patterns

### ❌ Using Same Model for Everything
```python
# Bad: One size fits all
parser = Agent(model=Ollama(id="gpt-oss:120b-cloud"))
validator = Agent(model=Ollama(id="gpt-oss:120b-cloud"))
executor = Agent(model=Ollama(id="gpt-oss:120b-cloud"))

# Problem: gpt-oss not optimal for validation/reasoning
```

### ❌ Using Slow Model for Simple Tasks
```python
# Bad: Overkill for parsing
parser = Agent(model=Ollama(id="deepseek-v3.1:671b-cloud"))  # 76 tok/s

# Problem: 2.5x slower than needed for simple extraction
```

### ❌ Using Fast Model for Complex Reasoning
```python
# Bad: Insufficient for validation
validator = Agent(model=Ollama(id="gpt-oss:120b-cloud"))  # Fast but shallow

# Problem: May miss validation edge cases
```

### ✅ Optimal: Match Model to Task
```python
# Good: Right tool for right job
parser = Agent(model=Ollama(id="glm-4.6:cloud"))               # Fast parsing
validator = Agent(model=Ollama(id="deepseek-v3.1:671b-cloud")) # Deep reasoning
executor = Agent(model=Ollama(id="glm-4.6:cloud"))             # Fast tools
```

---

## Performance Testing Pattern

**Document your model choices:**

```python
# Create MODEL_SELECTION.md
"""
# Model Selection - [Workflow Name]

## Selection Criteria
- Task Type: API operations (parse/validate/execute)
- Priority: Balanced (speed + accuracy)
- Context: Medium (~50K tokens)
- Tool Use: Yes (MCP server)

## Selected Models

### Parser Agent
- **Model**: glm-4.6:cloud (192 tok/s, 198K context)
- **Rationale**: Fastest for simple extraction, good context
- **Task**: Parse natural language → structured data
- **Source**: ollama-model-selector recommendation (2025-01-13)

### Validator Agent
- **Model**: deepseek-v3.1:671b-cloud (76 tok/s, 160K context)
- **Rationale**: Hybrid thinking for complex validation logic
- **Task**: Validate against API requirements
- **Source**: ollama-model-selector recommendation (2025-01-13)

### Executor Agent
- **Model**: glm-4.6:cloud (192 tok/s, 198K context)
- **Rationale**: Excellent tool calling, fast execution
- **Task**: Execute validated API operations
- **Source**: ollama-model-selector recommendation (2025-01-13)

## Alternatives Considered
- gpt-oss:120b-cloud: Faster but less reasoning for validator
- qwen3-coder:480b-cloud: Good but slower for non-code tasks

## Performance Benchmarks
- Average workflow time: ~12s (3 steps)
- Parser: ~2s (192 tok/s)
- Validator: ~6s (76 tok/s) - acceptable for accuracy
- Executor: ~4s (192 tok/s + API latency)

## Verification Commands
```bash
# Check models available
ollama list | grep -E "(glm-4.6|deepseek-v3.1)"

# Test parser speed
time ollama run glm-4.6:cloud "parse this: create contact ABC"

# Test validator reasoning
time ollama run deepseek-v3.1:671b-cloud "validate: ..."
```
"""
```

---

## Key Takeaways

1. **Consult ollama-model-selector skill** before hardcoding models
2. **Match models to task types** (parsing → fast, reasoning → powerful)
3. **Balance speed and accuracy** based on workflow requirements
4. **Consider context windows** - don't use more than needed
5. **Document your choices** with rationale and performance metrics
6. **Avoid one-size-fits-all** - different steps need different models
7. **Test and iterate** - benchmark your choices

Data-driven model selection creates workflows that are both fast and accurate. Always consult the ollama-model-selector skill for optimal choices.

