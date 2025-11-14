---
name: zen-workflow
description: Cost-optimized Zen MCP orchestration with Ollama Cloud preference for research, decisions, and debugging
---

# Zen Workflow Orchestration

**Purpose**: Execute multi-step Zen MCP workflows with intelligent model selection, preferring free Ollama Cloud models before escalating to paid alternatives.

## When to Use

Use this skill when you need:
- **Deep research** across multiple sources (consensus → thinkdeep → synthesis)
- **Critical decisions** with multiple perspectives (challenge → consensus → recommendation)
- **Complex debugging** requiring systematic investigation (thinkdeep → debug → validation)

**Triggers**:
- User says "zen research", "deep research", or "research workflow"
- User says "zen decide", "critical decision", or "evaluate options"
- User says "zen debug", "complex bug", or "systematic investigation"

## Cost Optimization Strategy

**Free Tier (Ollama Cloud)** - Use first:
- `deepseek-v3.1:671b-cloud` - Best reasoning (intelligence: 16, 76 tok/s, 160K context)
- `kimi-k2:1t-cloud` - Largest context (intelligence: 19, 33 tok/s, 256K context)
- `qwen3-coder:480b-cloud` - Best for code (intelligence: 18, 54 tok/s, 256K context)
- `glm-4.6:cloud` - Fastest responses (intelligence: 11, 192 tok/s, 198K context)

**Paid Tier** - Escalate when needed:
- `o3` - Extreme reasoning (200K context, extended thinking)
- `gpt-5` - Advanced reasoning (400K context)
- `gemini-2.5-pro` - Best overall (1M context, thinking mode)
- `grok-4` - Strong reasoning (256K context)

**Escalation Triggers**:
- Ollama model fails or returns poor quality
- Task explicitly requires extended thinking beyond Ollama capabilities
- Context size exceeds Ollama limits (>256K tokens)
- Time-critical work requiring fastest premium models

## Workflows

### Research Workflow
**Purpose**: Comprehensive research with multiple perspectives

**Steps**:
1. **Initial consensus** (3 Ollama models: deepseek, kimi, glm-4.6)
   - Gather diverse perspectives quickly
   - 3 stances: for/neutral/against or 3 different aspects

2. **Deep analysis** (thinkdeep with deepseek-v3.1)
   - Systematic investigation of findings
   - Hypothesis testing and evidence gathering

3. **Synthesis** (chat with kimi-k2 for large context)
   - Combine all findings
   - Present coherent recommendations

**Escalation**: Use gpt-5 or gemini-2.5-pro for synthesis if context >256K

### Decision Workflow
**Purpose**: Critical thinking and multi-angle evaluation

**Steps**:
1. **Challenge assumptions** (challenge with deepseek-v3.1)
   - Devil's advocate analysis
   - Identify blind spots and risks

2. **Multi-model consensus** (3 models: deepseek for/qwen3-coder neutral/kimi against)
   - Structured debate with different stances
   - Comprehensive pro/con analysis

3. **Final recommendation** (thinkdeep with deepseek-v3.1)
   - Synthesize all perspectives
   - Clear decision with rationale

**Escalation**: Use o3 or gpt-5 if decision requires extreme reasoning depth

### Debug Workflow
**Purpose**: Systematic code investigation

**Steps**:
1. **Initial investigation** (thinkdeep with qwen3-coder)
   - Code analysis and hypothesis formation
   - 3-5 investigation steps

2. **Deep debugging** (debug with qwen3-coder)
   - Root cause identification
   - Evidence gathering across files

3. **Validation** (codereview with deepseek-v3.1)
   - Verify proposed fixes
   - Ensure no regressions

**Escalation**: Use gpt-5 for codereview if codebase >100K LOC

## Usage Examples

### Research Workflow
```
User: "zen research: analyze the trade-offs of microservices vs monoliths"

Claude: I'm using the zen-workflow skill for comprehensive research.

Step 1: consensus with 3 Ollama models
- deepseek-v3.1 (for microservices)
- kimi-k2 (neutral/balanced)
- glm-4.6 (for monoliths)

[Execute consensus with 3 models]

Step 2: thinkdeep with deepseek-v3.1
- Analyze patterns across all 3 perspectives
- Test hypotheses about scalability, complexity, cost

[Execute thinkdeep analysis]

Step 3: chat with kimi-k2
- Synthesize findings with large context window
- Present final research summary

[Execute synthesis]

Cost: $0 (all Ollama Cloud models)
```

### Decision Workflow
```
User: "zen decide: should we migrate from REST to GraphQL?"

Claude: I'm using the zen-workflow skill for critical decision analysis.

Step 1: challenge with deepseek-v3.1
- Question assumptions about GraphQL benefits
- Identify migration risks and costs

[Execute challenge]

Step 2: consensus with 3 Ollama models
- deepseek-v3.1 (for GraphQL)
- qwen3-coder (neutral/technical)
- kimi-k2 (for REST/cautious)

[Execute consensus]

Step 3: thinkdeep with deepseek-v3.1
- Synthesize all arguments
- Provide clear recommendation with rationale

[Execute thinkdeep]

Cost: $0 (all Ollama Cloud models)
```

### Debug Workflow
```
User: "zen debug: authentication flow broken across 5 files"

Claude: I'm using the zen-workflow skill for systematic debugging.

Step 1: thinkdeep with qwen3-coder
- Code analysis across all 5 files
- Hypothesis formation about auth flow

[Execute thinkdeep investigation]

Step 2: debug with qwen3-coder
- Root cause identification
- Evidence gathering from logs/code

[Execute debug]

Step 3: codereview with deepseek-v3.1
- Verify proposed fix
- Check for security issues

[Execute codereview]

Cost: $0 (all Ollama Cloud models)
```

## Model Selection Logic

**For each Zen tool call:**

1. **Check task requirements**:
   - Context size needed?
   - Extended thinking required?
   - Code-specific or general reasoning?

2. **Start with Ollama Cloud**:
   - Use task-appropriate model from free tier
   - Execute and evaluate quality

3. **Escalate if needed**:
   - Poor quality response → Try premium model
   - Context too large → Use gemini-2.5-pro (1M context)
   - Requires extended thinking → Use o3 or gpt-5

4. **Report costs**:
   - Track which models used (free vs paid)
   - Report total cost at end: "Cost: $0 (all Ollama)" or "Cost: ~$0.15 (1 paid call)"

## Task-to-Model Mapping

**Research/General**:
- First: `deepseek-v3.1:671b-cloud` or `kimi-k2:1t-cloud`
- Fallback: `gemini-2.5-pro` or `gpt-5`

**Code/Technical**:
- First: `qwen3-coder:480b-cloud`
- Fallback: `gpt-5` or `gemini-2.5-pro`

**Fast iteration**:
- First: `glm-4.6:cloud` (fastest at 192 tok/s)
- Fallback: `gpt-5-mini`

**Large context (>256K)**:
- Skip Ollama → Use `gemini-2.5-pro` (1M context)

**Extended thinking**:
- First: `kimi-k2-thinking:cloud` (if available)
- Otherwise: `o3` or `gpt-5`

**External CLI (clink)**:
- **Default**: OpenCode with `github-copilot/claude-sonnet-4.5`
- **Alternative**: OpenCode with `github-copilot/claude-sonnet-4`
- **When to use**: Repository-aware tasks, file operations, CLI tool access
- **Example**: `mcp__zen__clink(cli_name="opencode", model="github-copilot/claude-sonnet-4.5", prompt="...")`

## Integration with DEFAULT_MODEL=auto

**This skill enhances (not overrides) DEFAULT_MODEL=auto**:

1. When DEFAULT_MODEL=auto is set:
   - Skill applies Ollama-first bias
   - Provides explicit model parameter to Zen tools
   - Auto mode still handles fallback if model unavailable

2. When specific model requested:
   - User preference takes precedence
   - Skill doesn't override explicit model choice

3. Transparency:
   - Always announce which model being used
   - Report if escalating from free to paid
   - Show cost summary at end

## Implementation Details

**For Claude Code**:
- Use mcp__zen__* tools directly
- Pass explicit `model` parameter to each call
- Handle continuation_id for multi-turn workflows
- Check response quality and escalate if needed

**For clink (External CLI integration)**:
- **Always specify model**: `model="github-copilot/claude-sonnet-4.5"` (default and recommended)
- **CLI selection**: Use `cli_name="opencode"` for GitHub Copilot integration
- **When to use clink**:
  - Tasks requiring repository file access and navigation
  - Running CLI tools (git, npm, pytest, etc.)
  - Code analysis requiring LSP-like symbol understanding
  - Multi-file refactoring or search operations
- **Example call**:
  ```python
  mcp__zen__clink(
      cli_name="opencode",
      model="github-copilot/claude-sonnet-4.5",
      prompt="Analyze the authentication flow across these files",
      absolute_file_paths=["/path/to/auth.py", "/path/to/middleware.py"]
  )
  ```
- **Model metadata**: Response includes `opencode_model` in metadata for verification

**Cost tracking**:
```python
# Track in workflow
ollama_calls = 0
paid_calls = 0

# After each tool call
if model.endswith(':cloud'):
    ollama_calls += 1
else:
    paid_calls += 1

# Report at end
cost_msg = f"Cost: $0 (all Ollama)" if paid_calls == 0 else f"Cost: ~${paid_calls * 0.05} ({paid_calls} paid calls)"
```

## Quality Thresholds

**When to escalate from Ollama to paid**:
- Response indicates model uncertainty ("I cannot confidently...")
- User feedback negative ("that's not quite right")
- Technical depth insufficient (surface-level analysis)
- Error rate high (multiple failed attempts)

**Always escalate for**:
- Medical/legal advice (use premium models for accuracy)
- Financial calculations (use o3 or gpt-5 for precision)
- Security audits (use gemini-2.5-pro or gpt-5)

## Notes

- **Ollama Cloud requires**: Ollama v0.12+, active internet connection
- **Model availability**: Check with `listmodels` tool if model not found
- **Context optimization**: Use Ollama for <256K context, premium for larger
- **Cost transparency**: Always report model usage and estimated costs
- **User control**: Respect explicit model requests, don't override

See [workflows/](./workflows/) for detailed workflow definitions.
