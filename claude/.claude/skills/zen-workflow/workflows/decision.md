# Decision Workflow

**Purpose**: Critical thinking and multi-angle evaluation for important decisions

## Workflow Steps

### Step 1: Challenge Assumptions

**Tool**: `mcp__zen__challenge`

**Model selection**: `deepseek-v3.1:671b-cloud` (strong reasoning)

**Parameters**:
```json
{
  "prompt": "[Decision statement or proposal]"
}
```

**Purpose**: Devil's advocate analysis to identify:
- Unstated assumptions
- Blind spots and risks
- Alternative perspectives
- Potential failure modes

**Output**: Critical analysis highlighting weaknesses

### Step 2: Multi-Model Consensus

**Tool**: `mcp__zen__consensus`

**Model selection**:
- Model 1: `deepseek-v3.1:671b-cloud` (stance: for)
- Model 2: `qwen3-coder:480b-cloud` (stance: neutral/technical)
- Model 3: `kimi-k2:1t-cloud` (stance: against/cautious)

**Parameters**:
```json
{
  "prompt": "[Decision proposal]",
  "models": [
    {"model": "deepseek-v3.1:671b-cloud", "stance": "for"},
    {"model": "qwen3-coder:480b-cloud", "stance": "neutral"},
    {"model": "kimi-k2:1t-cloud", "stance": "against"}
  ],
  "step": "Evaluate: [proposal]",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "[Challenge insights + your analysis]"
}
```

**Output**: Structured debate with pros/cons from each perspective

### Step 3: Final Recommendation

**Tool**: `mcp__zen__thinkdeep`

**Model selection**:
- Default: `deepseek-v3.1:671b-cloud`
- If extreme reasoning needed: Escalate to `o3` or `gpt-5`

**Parameters**:
```json
{
  "prompt": "Synthesize decision analysis:\n\nChallenge findings:\n[summary]\n\nConsensus debate:\n[perspectives]\n\nProvide clear recommendation.",
  "model": "deepseek-v3.1:671b-cloud",
  "step": "[Synthesis strategy]",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": false,
  "findings": "[Key decision factors]",
  "hypothesis": "[Recommended decision]",
  "confidence": "high",
  "thinking_mode": "high"
}
```

**Output**: Clear decision with rationale and implementation guidance

## Example Execution

```
User: "zen decide: should we migrate from monorepo to microservices?"

Claude: I'm using the zen-workflow skill for critical decision analysis.

Step 1: Challenge assumptions with deepseek-v3.1
Questioning the need for microservices migration

[Execute challenge]

Challenge findings:
- Assumption: "Microservices = better scalability" (not always true)
- Risk: Increased operational complexity (monitoring, deployment)
- Alternative: Modular monolith might achieve same goals
- Cost: 3-6 months migration, team retraining

Step 2: Multi-model consensus (3 perspectives)
- deepseek-v3.1: Pro-microservices stance
- qwen3-coder: Neutral/technical analysis
- kimi-k2: Pro-monorepo/cautious stance

[Execute consensus with 3 Ollama models]

Consensus findings:
Pro-microservices (deepseek):
- Independent scaling and deployment
- Team autonomy and ownership
- Technology diversity

Neutral/Technical (qwen3-coder):
- Depends on team size (10+ engineers needed)
- Depends on traffic patterns (uneven load)
- Infrastructure maturity required (K8s, service mesh)

Pro-monorepo (kimi):
- Simpler operations and debugging
- Easier refactoring and code sharing
- Lower infrastructure costs
- Current monorepo not at limits yet

Step 3: Final recommendation with deepseek-v3.1
Synthesizing all perspectives for clear decision

[Execute thinkdeep]

Decision: WAIT - Not ready for microservices

Rationale:
1. Team size (6 engineers) insufficient for microservices overhead
2. Monorepo not at scalability limits yet
3. Can achieve goals with modular monolith approach
4. Defer 12-18 months, revisit at 15+ engineers

Implementation:
1. Refactor monorepo into clear bounded contexts
2. Prepare for future split (clear interfaces)
3. Invest in observability and testing now
4. Revisit decision when team doubles

Cost: $0 (all Ollama Cloud models)
Time: ~5-7 minutes
Confidence: High
```

## Quality Checks

**After challenge**:
- Did we identify unstated assumptions?
- Are risks substantive and specific?
- If generic → Retry with gpt-5

**After consensus**:
- Are the 3 perspectives truly different?
- Is technical analysis rigorous?
- If shallow → Escalate pro-con models to paid tier

**After recommendation**:
- Is decision clear (yes/no/wait)?
- Is rationale evidence-based?
- Is implementation guidance actionable?
- If unclear → Use o3 for final synthesis

## Escalation Strategy

**Use paid models if**:
- Decision has >$100K impact (use premium for accuracy)
- Technical complexity very high (use gpt-5 or o3)
- Multiple stakeholders with conflicting goals (use gemini-2.5-pro)
- Legal/compliance implications (use o3 for extended thinking)

**Recommended paid alternatives**:
- Challenge: gpt-5 or o3
- Consensus: gpt-5, gemini-2.5-pro, grok-4, o3
- Recommendation: o3 (best for complex decisions)

## Decision Framework

**Decision types and recommended models**:

**Strategic decisions** (product direction, architecture):
- Challenge: deepseek-v3.1 → gpt-5 if complex
- Consensus: 3 Ollama models → paid if >$1M impact
- Recommendation: deepseek-v3.1 → o3 if critical

**Technical decisions** (framework choice, design patterns):
- Challenge: qwen3-coder
- Consensus: qwen3-coder, deepseek, kimi
- Recommendation: qwen3-coder → gpt-5 if novel

**Process decisions** (workflow changes, tool adoption):
- Challenge: glm-4.6 (fast iteration)
- Consensus: 3 Ollama models (sufficient)
- Recommendation: deepseek-v3.1 (rarely needs escalation)
