# Research Workflow

**Purpose**: Comprehensive research with multiple perspectives and deep analysis

## Workflow Steps

### Step 1: Multi-Model Consensus (3 perspectives)

**Tool**: `mcp__zen__consensus`

**Model selection**:
- Model 1: `deepseek-v3.1:671b-cloud` (stance: for or aspect A)
- Model 2: `kimi-k2:1t-cloud` (stance: neutral or aspect B)
- Model 3: `glm-4.6:cloud` (stance: against or aspect C)

**Parameters**:
```json
{
  "prompt": "[Clear research question]",
  "models": [
    {"model": "deepseek-v3.1:671b-cloud", "stance": "for"},
    {"model": "kimi-k2:1t-cloud", "stance": "neutral"},
    {"model": "glm-4.6:cloud", "stance": "against"}
  ],
  "step": "Evaluate: [research question]",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "[Your analysis of the prompt]"
}
```

**Output**: 3 diverse perspectives on the research topic

### Step 2: Deep Analysis

**Tool**: `mcp__zen__thinkdeep`

**Model selection**: `deepseek-v3.1:671b-cloud` (best reasoning)

**Parameters**:
```json
{
  "prompt": "Analyze findings from consensus: [summary]",
  "model": "deepseek-v3.1:671b-cloud",
  "step": "[Investigation strategy]",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "[Key insights from consensus]",
  "hypothesis": "[Theory to test]",
  "confidence": "medium",
  "thinking_mode": "high"
}
```

**Output**: Systematic analysis with hypothesis testing

### Step 3: Synthesis

**Tool**: `mcp__zen__chat`

**Model selection**:
- Default: `kimi-k2:1t-cloud` (large 256K context)
- If context >256K: Escalate to `gemini-2.5-pro` (1M context)

**Parameters**:
```json
{
  "prompt": "Synthesize all research findings:\n\nConsensus perspectives:\n[summary]\n\nDeep analysis:\n[findings]\n\nProvide coherent recommendations.",
  "model": "kimi-k2:1t-cloud",
  "working_directory_absolute_path": "[current dir]"
}
```

**Output**: Final research summary with recommendations

## Example Execution

```
User: "zen research: benefits and drawbacks of remote work"

Claude: I'm using the zen-workflow skill for comprehensive research.

Step 1: Gathering diverse perspectives with consensus
- deepseek-v3.1 (pro-remote stance)
- kimi-k2 (balanced/neutral)
- glm-4.6 (pro-office stance)

[Execute consensus call with 3 Ollama models]

Perspectives gathered:
- Pro-remote: Flexibility, global talent, cost savings
- Neutral: Depends on role, company culture, tools
- Pro-office: Collaboration, culture, career growth

Step 2: Deep analysis with thinkdeep
Using deepseek-v3.1 for systematic investigation

[Execute thinkdeep with 3-4 investigation steps]

Analysis findings:
- Pattern: Success correlates with communication tools
- Hypothesis: Hybrid model optimal for most teams
- Evidence: Multiple studies support 2-3 days remote

Step 3: Synthesis with kimi-k2
Using large context window to combine all findings

[Execute chat synthesis]

Final recommendations:
1. Hybrid 2-3 days/week optimal for most organizations
2. Full remote works best for async global teams
3. Full office better for early-stage startups

Cost: $0 (all Ollama Cloud models)
Time: ~3-5 minutes
```

## Quality Checks

**After consensus**:
- Do we have 3 distinct perspectives?
- Are viewpoints substantive (not surface-level)?
- If poor quality → Retry with paid models

**After thinkdeep**:
- Did analysis identify patterns?
- Was hypothesis tested systematically?
- If insufficient depth → Escalate to gpt-5

**After synthesis**:
- Are recommendations clear and actionable?
- Is evidence properly cited?
- If unclear → Use gemini-2.5-pro for better synthesis

## Escalation Strategy

**Use paid models if**:
- Ollama responses generic or low-quality
- Research topic highly technical/specialized
- Context size approaches 256K tokens
- Time-critical research needing fastest models

**Recommended paid alternatives**:
- Consensus: gpt-5, gemini-2.5-pro, grok-4
- Thinkdeep: gpt-5 (extended thinking)
- Synthesis: gemini-2.5-pro (1M context)
