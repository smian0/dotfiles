# Zen Workflow Directory

Quick reference for available workflows and when to use each.

## Workflow Selection Decision Tree

```
User Request
    ↓
[Check for explicit trigger]
    ├─ "zen plan" → plan.md
    ├─ "zen debug" → debug.md
    ├─ "zen research" → (check for web keywords)
    │   ├─ Has web keywords → web-research.md
    │   └─ No web keywords → research.md
    └─ "zen decide" → decision.md
    ↓
[Check for context keywords]
    ├─ Web keywords ("latest", "current", "2025") → web-research.md
    ├─ Planning keywords ("implement", "build") → plan.md
    ├─ Error keywords ("bug", "broken") → debug.md
    ├─ Analysis keywords ("compare", "evaluate") → research.md
    └─ Decision keywords ("should we", "choose") → decision.md
    ↓
[Fallback to general chat]
```

## Workflow Files

### plan.md
**Purpose**: Implementation planning with consensus validation

**When to use**:
- User wants to plan a feature or system
- Keywords: "implement", "build", "design", "architect", "plan"
- Explicit: "zen plan"

**Tools used**:
- zen-plan skill (if available in project)
- Fallback: planner tool with consensus validation

**Cost**: $0 with Ollama Cloud models

---

### debug.md
**Purpose**: Multi-model debugging with Context7 library lookup

**When to use**:
- User reports bugs or errors
- Keywords: "bug", "error", "broken", "failing", "not working"
- Explicit: "zen debug"

**Tools used**:
- zen-debug-consensus skill (if available in project)
- Fallback: debug tool with consensus validation

**Cost**: $0 with Ollama Cloud models

---

### research.md
**Purpose**: Knowledge-based research with multiple perspectives

**When to use**:
- Research doesn't require current/recent information
- Questions about general concepts, tradeoffs, best practices
- Keywords: "research", "compare", "evaluate", "analyze"
- Explicit: "zen research" (without web keywords)

**Workflow**:
1. Multi-model consensus (3 perspectives)
2. Deep analysis with thinkdeep
3. Synthesis with large context model

**Tools used**:
- `mcp__zen__consensus`
- `mcp__zen__thinkdeep`
- `mcp__zen__chat`

**Models**:
- Consensus: deepseek-v3.1, kimi-k2, glm-4.6 (all :cloud)
- ThinkDeep: deepseek-v3.1:671b-cloud
- Synthesis: kimi-k2:1t-cloud

**Cost**: $0 (all Ollama Cloud)
**Time**: ~3-5 minutes

**Example queries**:
- "Compare microservices vs monoliths"
- "Analyze trade-offs of SQL vs NoSQL"
- "Research authentication patterns"

---

### web-research.md
**Purpose**: Web-enhanced research combining current information with deep analysis

**When to use**:
- Research requires current/recent information
- Keywords: "latest", "current", "recent", "2024", "2025", "2026", "new"
- Time-sensitive: "news", "trends", "developments", "updates"
- Search intent: "search for", "look up", "find information"

**Workflow**:
1. **Web search** with C-Link (glm-4.6:cloud)
2. Multi-model consensus (3 perspectives + web data)
3. Deep analysis with thinkdeep
4. Synthesis with large context model

**Tools used**:
- `mcp__zen__clink` (web search via opencode)
- `mcp__zen__consensus`
- `mcp__zen__thinkdeep`
- `mcp__zen__chat`

**Models**:
- Web Search: glm-4.6:cloud (fastest at 192 tok/s)
- Consensus: deepseek-v3.1, kimi-k2, qwen3-coder (all :cloud)
- ThinkDeep: deepseek-v3.1:671b-cloud
- Synthesis: kimi-k2:1t-cloud

**Cost**: $0 (all Ollama Cloud)
**Time**: ~4-7 minutes

**Example queries**:
- "What are the latest AI coding tools in 2025?"
- "Current state of quantum computing"
- "Recent developments in WebAssembly"
- "Compare latest JavaScript frameworks"

**Quality checks**:
- Are sources recent (within 1-2 years)?
- Are source URLs provided?
- If poor quality → Retry with deepseek-v3.1:671b-cloud

---

### decision.md
**Purpose**: Critical decision analysis with challenge assumptions

**When to use**:
- User needs to make a technical decision
- Keywords: "decide", "should we", "choose", "which option"
- Explicit: "zen decide"

**Workflow**:
1. Challenge assumptions
2. Multi-model consensus
3. Final recommendation

**Tools used**:
- `mcp__zen__challenge`
- `mcp__zen__consensus`
- `mcp__zen__chat`

**Cost**: $0 with Ollama Cloud models

---

## Web Keywords Detection

Use `web-research.md` when query contains:

**Temporal keywords**:
- "latest", "current", "recent", "new"
- "2024", "2025", "2026" (or future years)
- "news", "trends", "developments", "updates"
- "what's new", "state of [year]"

**Search intent keywords**:
- "search for", "look up", "find information"
- "compare latest", "best [current year]"

**Recency indicators**:
- "recently", "just released", "announced"
- "upcoming", "future", "roadmap"

## Cost Optimization

All workflows default to **Ollama Cloud (free tier)**:
- deepseek-v3.1:671b-cloud
- kimi-k2:1t-cloud
- qwen3-coder:480b-cloud
- glm-4.6:cloud

**Escalation to paid models** only when:
- Ollama returns poor quality results
- Context size exceeds 256K tokens
- Time-critical research needing premium models
- User explicitly requests specific paid model

## Error Handling

**If C-Link fails** (web-research.md):
- Fall back to standard research.md workflow
- Log warning about web search unavailability
- Note limitation in final output

**If consensus fails**:
- Retry with different model selection
- Fall back to single-model analysis
- Report degraded workflow to user

**If thinkdeep fails**:
- Use direct chat analysis
- Note that systematic investigation unavailable

## Model Selection Reference

**Best for web search**:
- glm-4.6:cloud (192 tok/s, fastest)
- Fallback: deepseek-v3.1:671b-cloud (better comprehension)

**Best for reasoning**:
- deepseek-v3.1:671b-cloud (intelligence: 16, 76 tok/s)
- Premium: gpt-5, o3

**Best for large context**:
- kimi-k2:1t-cloud (256K context, 33 tok/s)
- Premium: gemini-2.5-pro (1M context)

**Best for code**:
- qwen3-coder:480b-cloud (intelligence: 18, 54 tok/s)
- Premium: gpt-5, claude-sonnet-4.5

## Testing Your Workflow

**Quick test queries**:

```bash
# Test web-research
"What are the latest developments in LLM serving?"

# Test standard research
"Compare REST vs GraphQL architectures"

# Test plan
"zen plan: implement user authentication"

# Test debug
"I have a bug where the login fails intermittently"

# Test decision
"Should we use TypeScript or JavaScript for our new project?"
```

**Expected behavior**:
1. Skill detects intent correctly
2. Routes to appropriate workflow
3. Executes all steps in sequence
4. Reports model usage and costs
5. Provides quality results

## Notes

- All workflows are cost-optimized for Ollama Cloud
- Graceful degradation if tools unavailable
- Quality checks at each step
- User visibility into workflow progress
- Source citations for web research
- Explicit cost reporting

