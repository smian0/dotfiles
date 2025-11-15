# Web-Enhanced Research Workflow

**Purpose**: Comprehensive research combining web search with multi-model analysis for topics requiring current information

## When to Use This Workflow

**Triggers**:
- Keywords: "latest", "current", "recent", "2024", "2025", "2026"
- Time-sensitive: "news", "trends", "developments", "updates"
- Search intent: "search for", "look up", "find information", "what's new"
- Comparative: "compare latest", "evaluate current options"

**Use cases**:
- Technology trends and new frameworks
- Current market conditions or stock prices
- Recent news or events
- Latest best practices or standards
- Comparing current product offerings

## Workflow Steps

### Step 0: Web Search with C-Link + GLM

**Tool**: `mcp__zen__clink`

**Model selection**: GLM-4.6 (fastest at 192 tok/s, good for quick web searches)

**Parameters**:
```json
{
  "cli_name": "opencode",
  "model": "glm-4.6:cloud",
  "prompt": "Search the web for: [research topic]. Focus on:\n1. Current state and recent developments\n2. Key sources and authoritative references\n3. Relevant statistics or data points\n4. Recent expert opinions or consensus\n\nSummarize findings with source URLs.",
  "role": "default"
}
```

**Expected output**:
- Web search results with citations
- Key facts and recent developments
- Source URLs for verification
- Initial synthesis of findings

**Quality check**:
- Are sources recent (within last 1-2 years)?
- Do we have authoritative references?
- Is information substantive (not generic)?
- If poor quality → Retry with `deepseek-v3.1:671b-cloud` for deeper analysis

### Step 1: Multi-Model Consensus (with web context)

**Tool**: `mcp__zen__consensus`

**Model selection**:
- Model 1: `deepseek-v3.1:671b-cloud` (stance: for or aspect A)
- Model 2: `kimi-k2:1t-cloud` (stance: neutral or aspect B)
- Model 3: `qwen3-coder:480b-cloud` (stance: against or aspect C)

**Parameters**:
```json
{
  "prompt": "[Research question]\n\nWEB SEARCH FINDINGS:\n[Summary from Step 0]\n\nProvide your perspective on this topic.",
  "models": [
    {"model": "deepseek-v3.1:671b-cloud", "stance": "for"},
    {"model": "kimi-k2:1t-cloud", "stance": "neutral"},
    {"model": "qwen3-coder:480b-cloud", "stance": "against"}
  ],
  "step": "Evaluate perspectives considering web research findings: [research question]",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "[Your synthesis of web findings and initial analysis]"
}
```

**Output**: 3 diverse perspectives informed by current web data

### Step 2: Deep Analysis

**Tool**: `mcp__zen__thinkdeep`

**Model selection**: `deepseek-v3.1:671b-cloud` (best reasoning)

**Parameters**:
```json
{
  "prompt": "Analyze research findings:\n\nWEB DATA:\n[Step 0 summary]\n\nCONSENSUS PERSPECTIVES:\n[Step 1 summary]\n\nConduct systematic investigation.",
  "model": "deepseek-v3.1:671b-cloud",
  "step": "[Investigation strategy focusing on patterns from web data and consensus]",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "[Key insights combining web research and consensus perspectives]",
  "hypothesis": "[Theory to test based on web findings]",
  "confidence": "medium",
  "thinking_mode": "high"
}
```

**Output**: Systematic analysis with hypothesis testing grounded in current data

### Step 3: Final Synthesis

**Tool**: `mcp__zen__chat`

**Model selection**:
- Default: `kimi-k2:1t-cloud` (large 256K context for synthesis)
- If context >256K: Escalate to `gemini-2.5-pro` (1M context)

**Parameters**:
```json
{
  "prompt": "Synthesize complete research:\n\nWEB FINDINGS:\n[Step 0]\n\nMULTI-MODEL PERSPECTIVES:\n[Step 1]\n\nDEEP ANALYSIS:\n[Step 2]\n\nProvide:\n1. Comprehensive summary\n2. Key insights with sources\n3. Actionable recommendations\n4. Source citations",
  "model": "kimi-k2:1t-cloud",
  "working_directory_absolute_path": "[current dir]"
}
```

**Output**: Complete research report with web-sourced evidence and recommendations

## Example Execution

```
User: "What are the latest developments in AI code generation tools?"

Claude: I'm using the zen-workflow skill for web-enhanced research.

Step 0: Web Search with C-Link (glm-4.6:cloud)
Searching for current information on AI code generation tools...

[Execute clink with glm-4.6:cloud via opencode]

Web findings:
- Cursor raised $100M Series B (Oct 2024)
- GitHub Copilot Chat expanded features (Nov 2024)
- Claude Sonnet 4.5 with agentic coding (Dec 2024)
- Windsurf Editor with Cascade flow (Dec 2024)
- Replit Agent and Bolt.new gaining traction

Sources: TechCrunch, GitHub Blog, Anthropic Blog, Product Hunt

Step 1: Multi-Model Consensus (informed by web data)
- deepseek-v3.1: Agentic coding is the future
- kimi-k2: Market is fragmenting, multiple viable options
- qwen3-coder: Traditional IDEs integrating AI features

[Execute consensus with 3 Ollama models]

Perspectives gathered with current market context

Step 2: Deep Analysis with ThinkDeep
Using deepseek-v3.1 for systematic investigation...

[Execute thinkdeep with 3 investigation steps]

Analysis findings:
- Pattern: Shift from copilot → autonomous agents
- Hypothesis: Agentic coding will dominate 2025-2026
- Evidence: Investment patterns, feature development trends

Step 3: Synthesis with kimi-k2
Combining all findings into comprehensive report...

[Execute chat synthesis]

Final report:
1. Market landscape (with sources)
2. Key trends identified
3. Recommendations for developers
4. Future predictions (2025-2026)

Cost: $0 (all Ollama Cloud models)
Time: ~4-7 minutes
Sources: 8 authoritative sources cited
```

## Decision Logic

```python
# Detect if web research needed
web_research_keywords = [
    "latest", "current", "recent", "new", "2024", "2025", "2026",
    "news", "trends", "developments", "updates", "what's new",
    "compare latest", "best [current year]", "state of"
]

needs_web_search = any(keyword in user_prompt.lower() for keyword in web_research_keywords)

if needs_web_search:
    # Execute Step 0: Web Search
    web_results = mcp__zen__clink(
        cli_name="opencode",
        model="glm-4.6:cloud",
        prompt=f"Search web for: {research_topic}"
    )
    
    # Quality check
    if web_results_quality_low:
        # Retry with better model
        web_results = mcp__zen__clink(
            cli_name="opencode", 
            model="deepseek-v3.1:671b-cloud",
            prompt=f"Deep web research: {research_topic}"
        )
    
    # Proceed with web-informed consensus
    consensus_prompt = f"{research_question}\n\nWEB FINDINGS:\n{web_results}"
else:
    # Standard research workflow (no web search)
    consensus_prompt = research_question

# Continue with Steps 1-3 as normal
```

## Quality Checks

**After web search (Step 0)**:
- Are sources recent and authoritative?
- Do we have specific facts/data (not generic)?
- Are source URLs provided for verification?
- If poor quality → Retry with `deepseek-v3.1:671b-cloud`

**After consensus (Step 1)**:
- Do perspectives reference web findings?
- Are viewpoints substantive (not surface-level)?
- If disconnected from web data → Retry with explicit web context

**After thinkdeep (Step 2)**:
- Does analysis integrate web research?
- Is hypothesis grounded in current data?
- If insufficient integration → Prompt for web context focus

**After synthesis (Step 3)**:
- Are recommendations based on current information?
- Are sources properly cited?
- Is timeline/recency clear?
- If unclear → Use `gemini-2.5-pro` for better synthesis

## Escalation Strategy

**Use paid models if**:
- Web search returns low-quality results (generic/outdated)
- Research topic highly specialized/technical
- Context size exceeds 256K tokens
- Time-critical research needing fastest premium models

**Recommended paid alternatives**:
- Web Search: `claude-sonnet-4.5` via opencode (better comprehension)
- Consensus: `gpt-5`, `gemini-2.5-pro`, `grok-4`
- ThinkDeep: `gpt-5` with extended thinking
- Synthesis: `gemini-2.5-pro` (1M context, thinking mode)

## Error Handling

**If web search fails**:
```python
try:
    web_results = mcp__zen__clink(model="glm-4.6:cloud", ...)
except Exception as e:
    # Log error
    logger.warning(f"Web search failed: {e}")
    
    # Fallback to standard research workflow
    print("⚠️ Web search unavailable. Proceeding with knowledge-based research.")
    # Execute standard research.md workflow
```

**If clink unavailable**:
- Fall back to standard research workflow
- Note limitation in final output
- Suggest manual web search topics

## Cost Optimization

**All Ollama Cloud (free tier)**:
- Web Search: `glm-4.6:cloud` (fastest, 192 tok/s)
- Consensus: 3x Ollama Cloud models
- ThinkDeep: `deepseek-v3.1:671b-cloud`
- Synthesis: `kimi-k2:1t-cloud`
- **Total cost: $0**

**Escalated (paid tier)**:
- If 1 step escalated: ~$0.05-0.10
- If all steps escalated: ~$0.20-0.50
- Premium models worth it for critical research

## Notes

- **GLM-4.6 speed**: 192 tok/s makes it ideal for quick web searches
- **Source verification**: Always include URLs for user fact-checking
- **Recency bias**: Web search results biased toward recent content
- **Fallback ready**: Workflow degrades gracefully if web search fails
- **Cost transparency**: Report model usage and costs at completion

