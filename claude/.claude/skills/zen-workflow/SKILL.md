---
name: zen-workflow
description: "Zen workflow orchestrator: invoke this whenever user mentions 'zen' or requests research, planning, debugging, or decision-making. Automatically routes zen plan, zen debug, zen research, zen decide to optimal workflows (formal research with citations, quick web research, knowledge analysis, planning, debugging, decisions). Uses Zen MCP tools with cost-optimized Ollama Cloud models. Primary handler for all zen-prefixed commands and multi-model workflows."
---

# Zen Workflow Router

> **🎯 Primary Handler**: This skill should be invoked **automatically** whenever the user mentions:
> - Any "zen" keyword (zen plan, zen debug, zen research, zen decide)
> - Research requests (formal, quick, web-enhanced)
> - Planning or implementation tasks
> - Debugging or error investigation
> - Decision-making or comparison analysis

**Purpose**: Smart router that detects user intent and automatically selects the appropriate Zen MCP workflow with cost-optimized model selection.

## When to Invoke This Skill

**✅ ALWAYS invoke when user prompt contains:**
- "zen" keyword (zen plan, zen debug, zen research, zen decide, zen workflow)
- Research requests: "research X", "analyze X", "compare X vs Y"
- Planning: "implement X", "build X", "design X", "plan X"
- Debugging: "bug in X", "error with X", "fix X", "not working"
- Decisions: "should we X", "choose between X and Y", "decide on X"
- Multi-model workflows: "get consensus on X", "think deep about X"

**❌ DO NOT invoke for:**
- Simple questions not requiring workflows
- Direct tool usage (user explicitly calls a specific MCP tool)
- General chat without workflow intent

**⚡ Quick Comparison: Search vs Research**
| User says | Action | Time | What happens |
|-----------|--------|------|--------------|
| "zen web X" | Direct websearch tool | ~30s | Just returns web search results (no analysis) |
| "zen web search X" | Direct websearch tool | ~30s | Same as above - just search results |
| "zen search X" | Direct websearch tool | ~30s | Same as above - just search results |
| "zen research X" | Full research workflow | 4-30m | Web search + consensus + deep analysis + synthesis |
| "latest X" (no zen) | Web research workflow | 4-7m | Auto-detects web need, runs workflow |

## How It Works (Progressive Disclosure)

This skill uses a **3-tier detection system** to determine which workflow to execute:

1. **Priority 1: Explicit Triggers** (highest priority)
   - User says "zen plan" → Planning workflow
   - User says "zen debug" → Debug workflow
   - User says "zen web" OR "zen web search" OR "zen search" → Direct websearch tool (no workflow)
   - User says "zen research" → Research workflow
   - User says "zen decide" → Decision workflow

2. **Priority 2: Context Detection** (fallback when no explicit trigger)
   - Formal research keywords ("research paper", "need citations", "publish", "formal research") → Research skill (rigorous)
   - Web research keywords ("latest", "current", "recent", "2024", "2025", "quick research") WITHOUT "zen web/search" → Web Research workflow (fast)
   - Planning keywords ("implement", "build", "design", "architect") → Planning workflow
   - Error keywords ("bug", "error", "broken", "failing", "not working") → Debug workflow
   - Analysis keywords ("research", "compare", "evaluate", "analyze") → Research workflow
   - Decision keywords ("decide", "should we", "choose", "which option") → Decision workflow

**Note**: If user says "zen web", "zen web search", or "zen search", this OVERRIDES Priority 2 detection and calls websearch tool directly (no workflow).

3. **Priority 3: General Chat** (fallback)
   - No clear intent → Use cost-optimized chat tool

## Intent Detection & Routing

### Step 1: Detect User Intent

Read the user's message and classify it:

```
IF message contains "zen plan" → PLAN workflow
ELSE IF message contains "zen debug" → DEBUG workflow
ELSE IF message contains "zen web" OR "zen web search" OR "zen search" → Call websearch tool directly (no workflow)
ELSE IF message contains "zen research" → Ask user for research depth (quick vs formal)
ELSE IF message contains "zen decide" → DECIDE workflow
ELSE IF message has formal research keywords → RESEARCH SKILL (rigorous, citations)
ELSE IF message has web research keywords (without "zen web/search" prefix) → WEB RESEARCH workflow (fast)
ELSE IF message has planning keywords → PLAN workflow
ELSE IF message has error keywords → DEBUG workflow
ELSE IF message has analysis keywords ("research", "compare", "evaluate") → RESEARCH workflow (knowledge-based)
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

#### WEBSEARCH (Direct Tool Call - NO Workflow)
**Triggers**: "zen web", "zen web search", "zen search"
**Tool**: `mcp__zen__websearch` (direct call, no workflow overhead)

**When to use**:
- User wants quick web search results
- No analysis or consensus needed
- Just need current information from the web
- Saves tokens and time (1 tool call vs full workflow)

**Execute**:
```
Call mcp__zen__websearch directly:
  mcp__zen__websearch(
    query="[user's search query]",
    max_results=8,
    focus="news" | "docs" | "github" | "stackoverflow" | null
  )

Return results directly - no further processing
```

**Examples**:
```
User: "zen web latest Next.js features"
→ mcp__zen__websearch(query="latest Next.js features", focus="docs")

User: "zen web search today's tech news"
→ mcp__zen__websearch(query="today's tech news", focus="news")

User: "zen search github copilot updates"
→ mcp__zen__websearch(query="github copilot updates", focus="github")
```

#### RESEARCH Workflow
**Triggers**: "zen research", "research paper", analysis keywords
**Workflows**: `research` skill (rigorous) OR `workflows/research.md` (quick) OR `workflows/web-research.md` (web-enhanced)

**Detection logic**:
```
IF formal research keywords ("research paper", "need citations", "publish"):
  → Use research skill (/research)
    - 100% citation requirement
    - Level 3 validation (URL + quote + author)
    - Quality scoring (8/10 threshold)
    - 4 parallel search angles
    - Full audit trail in .research/ directory
    - Time: 15-30 minutes

ELSE IF "zen research" (explicit trigger):
  → Ask user: "Quick research or formal research with citations?"
    - Quick → web-research.md or research.md
    - Formal → research skill

ELSE IF web keywords ("latest", "current", "recent", "2024", "2025", "quick research"):
  → Use web-research.md (fast exploratory)
    - Web search (clink + glm-4.6:cloud)
    - Consensus (3 models + web data)
    - Deep analysis (thinkdeep)
    - Synthesis (large context model)
    - Time: 4-7 minutes
    - Cost: $0 (Ollama Cloud)

ELSE IF analysis keywords ("compare", "evaluate", "analyze"):
  → Use research.md (knowledge-based)
    - Consensus (3 models)
    - Deep analysis (thinkdeep)
    - Synthesis (large context model)
    - Time: 3-5 minutes
    - Cost: $0 (Ollama Cloud)
```

**Research Selection Matrix**:

| Need | Workflow | Time | Citations | Cost |
|------|----------|------|-----------|------|
| Publishing/sharing | research skill | 15-30m | 100% validated | Variable |
| Quick current info | web-research.md | 4-7m | Informal | $0 |
| Concept analysis | research.md | 3-5m | None | $0 |
| Initial exploration | web-research.md | 4-7m | Informal | $0 |

**Quality Comparison**:
- **research skill**: PhD thesis quality (rigorous validation)
- **zen-workflow**: Stack Overflow answer quality (fast, practical)

**Hybrid approach** (when needed):
```
Step 1: Quick web-research (4-7 min)
  ↓ Get initial findings and key sources
Step 2: If valuable → Formal research skill (15-30 min)
  ↓ Validate sources, 100% citation coverage
Step 3: Publish with confidence
```

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

**Web Search (NEW - cost-optimized)**:
- **Tool**: `mcp__zen__websearch` - Direct web search via GLM CLI
- **Benefits**: Saves 60-80% tokens, uses GLM internally, $0 cost, auto-injects date/time/timezone, strips incorrect dates
- **When to use**: Any web search needs ("latest X", "today's Y", breaking news, current docs)
- **Example**: `mcp__zen__websearch(query="latest React features", max_results=8, focus="docs")`
- **Focus options**: "docs", "news", "github", "stackoverflow", or null
- **Note**: Automatically injects current date, time, and timezone (e.g., "November 15, 2025 at 02:30 PM PST") for accurate temporal searches

**External CLI (clink)**:
- **Default**: OpenCode with `github-copilot/claude-sonnet-4.5`
- **Alternative**: GLM CLI for web search (prefer websearch tool instead)
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

### Example 3: Web Search (Direct - No Workflow)
```
User: "zen web get today's china news"

Claude: I'm using the zen-workflow router.
→ Detected: "zen web" (explicit trigger - Priority 1)
→ Action: Call websearch tool DIRECTLY (no workflow)

[Single tool call - no multi-model consensus or deep analysis]
mcp__zen__websearch(
  query="get today's china news",
  max_results=8,
  focus="news"
)

Tool automatically injects:
🗓️ CRITICAL: CURRENT DATE & TIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
November 15, 2025 at 02:30 PM PST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results returned immediately:
- 8 search results with URLs
- Reuters China news (today)
- South China Morning Post (latest)
- Bloomberg Asia (Nov 15, 2025)

Cost: $0 (GLM CLI via websearch tool)
Time: ~30 seconds (single tool call)
```

**Key difference**: "zen web" = Just search, no analysis workflow!

**All these trigger direct websearch**:
- "zen web [query]" ✓
- "zen web search [query]" ✓  
- "zen search [query]" ✓

### Example 3a: Quick Research (Knowledge-Based)
```
User: "Compare microservices vs monoliths trade-offs"

Claude: I'm using the zen-workflow router.
→ Detected: "compare" (analysis keyword)
→ No web keywords or formal research indicators
→ Routing to: RESEARCH workflow (knowledge-based)
→ Using embedded research workflow

[Executes: consensus → thinkdeep → synthesis]
Cost: $0 (all Ollama Cloud models)
Time: ~3-5 minutes
```

### Example 3b: Quick Web Research
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

### Example 3c: Formal Research (With Citations)
```
User: "I need to write a research paper on quantum error correction with proper citations"

Claude: I'm using the zen-workflow router.
→ Detected: "research paper" + "citations" (formal research keywords)
→ Routing to: RESEARCH SKILL (rigorous validation)
→ Using /research skill

Stage 1: Parallel Search (4 angles)
- Agent 1 (hardware): 3 results ✓
- Agent 2 (software): 4 results ✓
- Agent 3 (performance): 3 results ✓
- Agent 4 (adoption): 3 results ✓
Total: 13 search results

Stage 2: Citation Extraction
- Found 11 citations with verbatim quotes ✓

Stage 3: Source Validation (Level 3)
- 11 citations checked
- 9 validated (avg credibility: 8.8/10)
- 2 rejected (low credibility)

Stage 4: Claim Grounding
- 12 claims extracted
- 100% grounding coverage ✓

Stage 5: Report Writing
- Inline citations: 12 citations
- Self-validation: Passed ✓

Stage 6: Quality Scoring
Quality Score: 9/10 ✓ PASS
- Grounding: 5/5 (100% cited) ✓
- Source Quality: 2/2 (avg 8.8) ✓
- Diversity: 1/1 (9 unique sources) ✓
- Completeness: 1/1 ✓
- Clarity: 1/1 ✓

Research saved to: .research/2025-11-15-quantum-error-correction/

Time: ~20 minutes
Cost: Variable (depends on models used)
Output: Formal report with verified citations ready for publishing
```

### Example 3d: User Clarification
```
User: "zen research: AI transformer architectures"

Claude: I'm using the zen-workflow router.
→ Detected: "zen research" (explicit trigger)
→ Needs clarification on research depth

Quick question: What type of research do you need?

1. **Quick research** (4-7 min, informal sources, $0)
   - Fast overview with web search
   - Good for personal understanding

2. **Formal research** (15-30 min, validated citations, variable cost)
   - 100% citation coverage
   - Ready for publishing/sharing
   - Full audit trail

User: "Just need a quick overview"

→ Routing to: WEB RESEARCH workflow (fast)
[Executes web-enhanced research workflow...]
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
