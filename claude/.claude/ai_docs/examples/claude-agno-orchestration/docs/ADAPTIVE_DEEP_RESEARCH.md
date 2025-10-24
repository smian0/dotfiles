# Adaptive Deep Research Agent

An advanced research agent with adaptive strategies, multi-hop reasoning, and self-reflective mechanisms.

## Overview

The `AdaptiveDeepResearchAgent` is a sophisticated research agent that automatically adapts its strategy based on query complexity. It implements features from Claude Code's deep-research-agent pattern, including:

- **Adaptive Planning**: Automatically selects strategy based on query complexity
- **Multi-Hop Reasoning**: Explores information chains up to 5 levels deep
- **Self-Reflection**: Monitors progress and adjusts approach
- **Evidence Management**: Rigorous source citation and credibility assessment
- **4-Phase Workflow**: Discovery → Investigation → Synthesis → Reporting

## vs DeepWebResearcherAgent

| Feature | DeepWebResearcherAgent | AdaptiveDeepResearchAgent |
|---------|------------------------|---------------------------|
| **Strategy** | Fixed institutional format | Adaptive (simple/ambiguous/complex) |
| **Complexity Detection** | None | Automatic |
| **Planning Approach** | Direct execution | 3 adaptive strategies |
| **Multi-Hop Reasoning** | No | Yes (up to 5 hops) |
| **Self-Reflection** | No | Yes (with iteration) |
| **Replanning** | No | Yes (on low confidence) |
| **Output Format** | Institutional report | Varies by complexity |
| **Best For** | Hedge fund reports | Varied research tasks |

## Important: Web Search Tools Required

**⚠️ The AdaptiveDeepResearchAgent requires web search tools to perform actual research.**

Without tools, the agent will generate research plans but cannot execute them. You must provide one or more web search tools:

- **Agno OllamaWebTools**: Fast local search via Ollama
- **Agno MCPTools**: Use MCP web search servers (webSearchPrime, etc.)
- **DuckDuckGo**: Reliable free search API
- **Custom tools**: Any tool that provides web search capability

### Tool Setup Examples

```python
# Option 1: Ollama Web Search (fast, local)
from agno.tools.ollama_web import OllamaWebTools

web_tools = OllamaWebTools(
    cache_results=True,
    cache_ttl=3600
)
agent = AdaptiveDeepResearchAgent(tools=[web_tools])

# Option 2: MCP Web Search Prime
from agno.tools.mcp import MCPTools

mcp_tools = MCPTools(
    url="https://api.z.ai/api/mcp/web_search_prime/mcp",
    ...
)
agent = AdaptiveDeepResearchAgent(tools=[mcp_tools])

# Option 3: Multiple tools (cascading fallback)
from cascading_search import CascadingSearchTools

cascading = CascadingSearchTools(...)  # Ollama → MCP → DuckDuckGo
agent = AdaptiveDeepResearchAgent(tools=[cascading])
```

## Quick Start

### Basic Usage

```python
from orchestration import AdaptiveDeepResearchAgent

# IMPORTANT: For actual research, provide web search tools
from agno.tools.ollama_web import OllamaWebTools

web_tools = OllamaWebTools(cache_results=True)

# Create agent with tools
agent = AdaptiveDeepResearchAgent(tools=[web_tools])

# Simple query (auto-detects complexity)
result = agent.run("What is quantum computing?")

# With complexity hint
result = agent.run(
    "Research AI developments",
    complexity="ambiguous"
)

# Complex query with max hops
result = agent.run(
    "Analyze quantum computing impact on cryptography",
    complexity="complex",
    max_hops=3
)
```

### With Self-Reflection

```python
# Research with iteration until confidence threshold met
result = agent.run_with_reflection(
    query="Analyze the impact of large language models",
    min_confidence=0.7,
    max_iterations=3
)

print(f"Final confidence: {result.metadata['final_confidence']:.2f}")
print(f"Iterations: {result.metadata['iterations']}")
```

### With Orchestrator

```python
from orchestration import DirectOrchestrator, create_adaptive_researcher

orchestrator = DirectOrchestrator()
agent = create_adaptive_researcher(
    temperature=0.2,
    max_tokens=15000
)
orchestrator.add_agent('researcher', agent)

result = orchestrator.run("Your research query")
```

## Adaptive Planning Strategies

### Planning-Only (Simple Queries)

**Triggered by:**
- Short queries (< 10 words)
- Simple question patterns ("What is...", "Who is...", "Define...")
- Clear, unambiguous intent

**Strategy:**
- Direct execution without clarification
- Single-pass investigation
- Concise, accurate answer
- 2-3 key sources

**Example:**
```python
agent.run("What is Python?")  # Auto-detected as simple
```

### Intent-Planning (Ambiguous Queries)

**Triggered by:**
- Medium-length queries (10-30 words)
- Vague intent ("about", "regarding", "information on")
- Multiple possible interpretations

**Strategy:**
- Identify clarification needs
- Ask questions OR proceed with best interpretation
- Note assumptions made
- Moderate depth analysis

**Example:**
```python
agent.run("Research AI developments")  # Auto-detected as ambiguous
```

### Unified Planning (Complex Queries)

**Triggered by:**
- Long queries (> 30 words)
- Analysis keywords ("analyze", "comprehensive", "investigate")
- Multiple sub-questions
- Explicit complexity indicators

**Strategy:**
- Present research plan first
- Execute comprehensive investigation
- Multi-hop reasoning
- Thorough synthesis

**Example:**
```python
agent.run("""Research quantum computing and drug discovery.
Focus on: breakthroughs, challenges, timeline, players.""")
# Auto-detected as complex
```

## Multi-Hop Reasoning Patterns

The agent supports 4 reasoning patterns up to 5 hops deep:

### 1. Entity Expansion
Person → Affiliations → Related work → Impact → Legacy

```python
result = agent.run(
    "Research Satya Nadella's impact on Microsoft",
    max_hops=4
)
```

### 2. Temporal Progression
Current state → Recent changes → Historical context → Trends → Predictions

```python
result = agent.run(
    "Trace the evolution of neural networks from inception to today",
    max_hops=5
)
```

### 3. Conceptual Deepening
Overview → Core concepts → Technical details → Applications → Limitations

```python
result = agent.run(
    "Explain quantum entanglement from basics to applications",
    max_hops=5
)
```

### 4. Causal Chains
Observation → Immediate cause → Root cause → Solutions → Implementations

```python
result = agent.run(
    "Investigate why AI models hallucinate and potential solutions",
    max_hops=4
)
```

## Self-Reflective Mechanisms

### Progress Assessment

After each major step, the agent evaluates:
- Core question addressed?
- Remaining knowledge gaps?
- Confidence improving or declining?
- Strategy adjustment needed?

### Quality Monitoring

**Source Credibility:**
- HIGH: Academic papers, government data, technical docs
- MEDIUM: Reputable news, industry reports, expert blogs
- LOW: Social media, unverified sources, outdated info

**Information Consistency:**
- Cross-references key facts
- Notes contradictions explicitly
- Assesses consensus vs outlier views

**Bias Detection:**
- Identifies conflicts of interest
- Notes ideological/commercial bias
- Presents balanced perspectives

### Replanning Triggers

The agent replans when:
- Confidence drops below 60%
- Contradictory information exceeds 30%
- Multiple dead ends encountered
- Time/resource constraints emerge

## 4-Phase Research Workflow

### Phase 1: Discovery
**Objectives:** Map information landscape, identify sources, detect themes

**Actions:**
- Broad exploratory searches
- Survey key sources
- Note emerging themes
- Identify gaps

### Phase 2: Investigation
**Objectives:** Deep dive into specifics, cross-reference, resolve contradictions

**Actions:**
- Targeted deep searches
- Multi-source verification
- Follow citation chains
- Investigate discrepancies

### Phase 3: Synthesis
**Objectives:** Build coherent narrative, create evidence chains, identify gaps

**Actions:**
- Connect related findings
- Construct logical arguments
- Note evidence strength
- Acknowledge limitations

### Phase 4: Reporting
**Objectives:** Structure for audience, provide citations, include confidence

**Actions:**
- Organize by importance
- Add all citations
- State confidence explicitly
- Provide recommendations

## Report Structure

The agent produces structured reports:

```markdown
## Executive Summary
- Core finding (2-3 sentences)
- Key takeaways (3-5 bullets)
- Confidence level

## Research Methodology
- Query interpretation
- Strategy used
- Hops explored
- Sources consulted

## Key Findings
### Finding 1: [Topic]
**Evidence:** [Sources]
**Confidence:** [Level]
**Limitations:** [Gaps]

## Analysis & Synthesis
- Cross-cutting insights
- Patterns identified
- Contradictions resolved

## Remaining Questions
- What we don't know
- Why gaps exist
- Follow-up suggestions

## Conclusions
- Direct answer
- Confidence assessment
- Recommendations

## Sources
- Complete list with dates
- Credibility ratings
- Key sources highlighted

## Research Metadata
- Search iterations: X
- Hop depth: X
- Confidence: X/10
- Duration: Xs
```

## Configuration Options

### Model Configuration

```python
from orchestration import AgentConfig, AdaptiveDeepResearchAgent

config = AgentConfig(
    name="CustomResearcher",
    model_id="claude-sonnet-4",
    temperature=0.2,      # Lower = more consistent
    max_tokens=15000,     # Higher = more comprehensive
    markdown=True
)

agent = AdaptiveDeepResearchAgent(config)
```

### Convenience Function

```python
from orchestration import create_adaptive_researcher

agent = create_adaptive_researcher(
    model_id="claude-sonnet-4",
    temperature=0.3,
    max_tokens=12000
)
```

## Advanced Features

### Complexity Detection

```python
# Manual complexity detection
complexity = agent._detect_complexity("Your query")
print(f"Detected: {complexity}")  # simple/ambiguous/complex
```

### Confidence Estimation

```python
# Estimate confidence from content
confidence = agent._estimate_confidence(result.content)
print(f"Estimated confidence: {confidence:.2f}")
```

### Prompt Enhancement

```python
# See how prompts are enhanced
enhanced = agent._enhance_prompt(
    "Research AI",
    complexity="ambiguous"
)
print(enhanced)
```

## Performance Optimization

### Recommended Settings by Use Case

**Quick Fact-Finding:**
```python
agent = create_adaptive_researcher(
    temperature=0.1,
    max_tokens=4000
)
```

**Comprehensive Analysis:**
```python
agent = create_adaptive_researcher(
    temperature=0.3,
    max_tokens=15000
)
```

**Exploratory Research:**
```python
agent = create_adaptive_researcher(
    temperature=0.5,
    max_tokens=20000
)
```

## Examples

See `examples/05_adaptive_deep_research.py` for:
- Simple query handling
- Ambiguous query handling
- Complex query processing
- Self-reflective research
- Orchestration integration
- Output management
- Comparison with standard agent

## Limitations

- **Requires web search tools**: Agent needs OllamaWebTools, MCPTools, or similar for actual research
- **Tool-dependent quality**: Research quality depends on provided search tools
- Confidence estimation is heuristic-based
- Multi-hop tracking is implicit, not explicit
- No paywall bypass or private data access
- Complex queries may require multiple LLM calls (cost consideration)

## Future Enhancements

- ✅ **Web search tool integration** - IMPLEMENTED (supports Ollama, MCP, DuckDuckGo)
- Explicit hop tracking and visualization
- Confidence model training with ML models
- Automated source verification and fact-checking
- Parallel investigation paths with multiple agents
- Advanced result caching across sessions
- Integration with specialized domain databases

## Related Documentation

- [DeepWebResearcherAgent](./DEEP_WEB_RESEARCHER.md)
- [Orchestration Patterns](./ORCHESTRATION_PATTERNS.md)
- [Output Management](./OUTPUT_MANAGEMENT.md)
- [Artifact Visualization](./ARTIFACT_VISUALIZATION.md)

---

Last Updated: 2025-10-13
