---
name: zen-workflow
description: Progressive disclosure router for Zen MCP workflows - automatically detects user intent and routes to specialized workflows (zen-plan, zen-debug, research, decision) with cost-optimized Ollama Cloud models
---

# Zen Workflow Router

**Purpose**: Smart router that detects user intent and automatically selects the appropriate Zen MCP workflow with cost-optimized model selection.

## How It Works (Progressive Disclosure)

This skill uses a **3-tier detection system** to determine which workflow to execute:

1. **Priority 1: Explicit Triggers** (highest priority)
   - User says "zen plan" → Planning workflow
   - User says "zen debug" → Debug workflow
   - User says "zen research" → Research workflow
   - User says "zen decide" → Decision workflow

2. **Priority 2: Context Detection** (fallback when no explicit trigger)
   - Web research keywords ("latest", "current", "recent", "2024", "2025", "search for") → Web Research workflow
   - Planning keywords ("implement", "build", "design", "architect") → Planning workflow
   - Error keywords ("bug", "error", "broken", "failing", "not working") → Debug workflow
   - Analysis keywords ("research", "compare", "evaluate", "analyze") → Research workflow
   - Decision keywords ("decide", "should we", "choose", "which option") → Decision workflow

3. **Priority 3: General Chat** (fallback)
   - No clear intent → Use cost-optimized chat tool

## Intent Detection & Routing

### Step 1: Detect User Intent

Read the user's message and classify it:

```
IF message contains "zen plan" → PLAN workflow
ELSE IF message contains "zen debug" → DEBUG workflow
ELSE IF message contains "zen research" → RESEARCH workflow (check for web keywords)
ELSE IF message contains "zen decide" → DECIDE workflow
ELSE IF message has web research keywords → WEB RESEARCH workflow
ELSE IF message has planning keywords → PLAN workflow
ELSE IF message has error keywords → DEBUG workflow
ELSE IF message has analysis keywords → RESEARCH workflow
ELSE IF message has decision keywords → DECIDE workflow
ELSE → GENERAL chat with cost-optimized model
```

### Step 2: Execute Workflow

Once intent is detected, execute the appropriate workflow:

#### PLAN Workflow
**Triggers**: "zen plan", planning keywords
**Specialized Skill**: `/zen-plan` (if available in project)
**Fallback**: Embedded planning workflow

**When to use zen-plan skill**:
- Project has `.claude/skills/zen-plan/SKILL.md`
- Need interactive planning with multi-phase consensus validation
- Want automatic save to Serena memory
- Require post-implementation validation (Phase 4)

**Execute**:
```
If zen-plan skill exists:
  Skill(skill="zen-plan")
Else:
  See workflows/plan.md for embedded fallback
```

#### DEBUG Workflow
**Triggers**: "zen debug", error keywords
**Specialized Skill**: `/zen-debug-consensus` (if available in project)
**Fallback**: Embedded debug workflow

**When to use zen-debug-consensus skill**:
- Project has `.claude/skills/zen-debug-consensus/SKILL.md`
- Debugging external library issues (Context7 lookup available)
- Need multi-model consensus debugging
- Complex multi-file bugs

**Execute**:
```
If zen-debug-consensus skill exists:
  Skill(skill="zen-debug-consensus")
Else:
  See workflows/debug.md for embedded fallback
```

#### RESEARCH Workflow
**Triggers**: "zen research", analysis keywords
**Workflow**: See `workflows/research.md` or `workflows/web-research.md`

**Detection logic**:
```
IF "zen research" OR analysis keywords:
  IF web keywords detected ("latest", "current", "recent", "2024", "2025", "search"):
    → Use web-research.md (includes C-Link web search)
  ELSE:
    → Use research.md (knowledge-based only)
```

**Standard Research** (workflows/research.md):
- Consensus (3 models)
- Deep analysis (thinkdeep)
- Synthesis (large context model)

**Web-Enhanced Research** (workflows/web-research.md):
- Web search (clink + glm-4.6:cloud)
- Consensus (3 models + web data)
- Deep analysis (thinkdeep)
- Synthesis (large context model)

#### DECIDE Workflow
**Triggers**: "zen decide", decision keywords
**Workflow**: See `workflows/decision.md`

Critical decision analysis with:
- Challenge assumptions
- Multi-model consensus
- Final recommendation

## Cost Optimization Strategy

**Free Tier (Ollama Cloud)** - Always try first:
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
- Task requires extended thinking beyond Ollama capabilities
- Context size exceeds Ollama limits (>256K tokens)
- Time-critical work requiring fastest premium models

## Model Selection by Task

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

## Usage Examples

### Example 1: Planning
```
User: "zen plan: implement user authentication system"

Claude: I'm using the zen-workflow router.
→ Detected: "zen plan" (explicit trigger)
→ Routing to: PLAN workflow
→ Checking for zen-plan skill...
→ Found! Using /zen-plan skill

[Executes zen-plan workflow with interactive planning + consensus validation]
```

### Example 2: Debugging
```
User: "I have a bug where authentication fails for some users"

Claude: I'm using the zen-workflow router.
→ Detected: "bug", "fails" (error keywords)
→ Routing to: DEBUG workflow
→ Checking for zen-debug-consensus skill...
→ Found! Using /zen-debug-consensus skill

[Executes zen-debug-consensus with Context7 + multi-model debugging]
```

### Example 3: Research (Knowledge-Based)
```
User: "zen research: microservices vs monoliths trade-offs"

Claude: I'm using the zen-workflow router.
→ Detected: "zen research" (explicit trigger)
→ No web keywords detected
→ Routing to: RESEARCH workflow (knowledge-based)
→ Using embedded research workflow

[Executes: consensus → thinkdeep → synthesis]
Cost: $0 (all Ollama Cloud models)
```

### Example 3b: Research (Web-Enhanced)
```
User: "What are the latest AI coding tools in 2025?"

Claude: I'm using the zen-workflow router.
→ Detected: "latest" + "2025" (web research keywords)
→ Routing to: WEB RESEARCH workflow
→ Using embedded web-research workflow

Step 0: Web Search via C-Link
Using glm-4.6:cloud (fastest at 192 tok/s)
[Search for latest AI coding tools...]

Web findings:
- Cursor raised Series B funding
- GitHub Copilot Chat features expanded
- Windsurf Editor with Cascade flow
- Sources: TechCrunch, GitHub Blog, Product Hunt

Step 1: Multi-Model Consensus (with web context)
- deepseek-v3.1, kimi-k2, qwen3-coder
[Analyze perspectives informed by web data...]

Step 2: Deep Analysis with ThinkDeep
Using deepseek-v3.1 for systematic investigation
[Test hypothesis: agentic coding trend...]

Step 3: Final Synthesis
Using kimi-k2 (large context)
[Comprehensive report with sources...]

Cost: $0 (all Ollama Cloud models)
Time: ~4-7 minutes
Sources: 8 authoritative sources cited
```

### Example 4: Decision
```
User: "Should we migrate from REST to GraphQL?"

Claude: I'm using the zen-workflow router.
→ Detected: "should we", "migrate" (decision keywords)
→ Routing to: DECIDE workflow
→ Using embedded decision workflow

[Executes: challenge → consensus → recommendation]
Cost: $0 (all Ollama Cloud models)
```

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

## Workflow Definitions

Detailed workflow definitions are in the `workflows/` directory:
- `workflows/plan.md` - Planning workflow with zen-plan reference
- `workflows/debug.md` - Debug workflow with zen-debug-consensus reference
- `workflows/research.md` - Research workflow (knowledge-based, embedded)
- `workflows/web-research.md` - Web-enhanced research with C-Link search (embedded)
- `workflows/decision.md` - Decision workflow (embedded)

## Notes

- **Ollama Cloud requires**: Ollama v0.12+, active internet connection
- **Model availability**: Check with `listmodels` tool if model not found
- **Context optimization**: Use Ollama for <256K context, premium for larger
- **Cost transparency**: Always report model usage and estimated costs
- **User control**: Respect explicit model requests, don't override
- **Progressive disclosure**: Router automatically determines best workflow
- **Graceful degradation**: Falls back to embedded workflows if specialized skills unavailable
