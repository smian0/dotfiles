"""
Adaptive Deep Research Agent
=============================

A sophisticated research agent with adaptive strategies, multi-hop reasoning,
and self-reflective mechanisms.

Based on Claude Code's deep-research-agent pattern but implemented for Agno.

Features:
- Adaptive planning (simple/ambiguous/complex queries)
- Multi-hop reasoning (entity expansion, temporal progression, etc.)
- Self-reflective progress assessment
- Evidence-based synthesis
- Comprehensive reporting
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from agno.agent import Agent
from agno.models.anthropic import Claude

from .base import BaseAgent, AgentConfig, AgentResult

logger = logging.getLogger(__name__)


class AdaptiveDeepResearchAgent(BaseAgent):
    """
    Deep research agent with adaptive strategies and intelligent exploration.

    Capabilities:
    - Adaptive planning based on query complexity
    - Multi-hop reasoning (up to 5 levels)
    - Self-reflective quality monitoring
    - Evidence management and citation
    - 4-phase workflow (Discovery → Investigation → Synthesis → Reporting)

    Example:
        agent = AdaptiveDeepResearchAgent()
        result = agent.run("Research quantum computing applications in drug discovery")

        # With complexity hint
        result = agent.run(query, complexity="complex", max_hops=3)
    """

    def __init__(self, config: Optional[AgentConfig] = None, tools: Optional[List] = None):
        """Initialize adaptive deep research agent.

        Args:
            config: Agent configuration
            tools: List of tools for web search (WebSearch, Ollama tools, MCP tools, etc.)
        """
        if config is None:
            config = self._default_config()

        super().__init__(config)
        self._hop_count = 0
        self._max_hops = 5
        self._confidence_threshold = 0.6
        self._tools = tools or []

    def _default_config(self) -> AgentConfig:
        """Create default configuration with comprehensive research instructions."""
        return AgentConfig(
            name="AdaptiveDeepResearchAgent",
            model_id="claude-sonnet-4",
            instructions=self._build_research_instructions(),
            temperature=0.3,  # Lower for more consistent research
            max_tokens=12000,  # Extended for comprehensive reports
            markdown=True
        )

    def _build_research_instructions(self) -> str:
        """Build comprehensive research instructions."""
        return """You are an elite research agent combining the rigor of a research scientist with the investigative skills of an investigative journalist.

════════════════════════════════════════════════════════════════════════════════
CORE RESEARCH METHODOLOGY
════════════════════════════════════════════════════════════════════════════════

## Adaptive Planning Strategy

Automatically detect query complexity and adapt your approach:

**Planning-Only** (Simple/Clear Queries)
- Direct execution without clarification
- Single-pass investigation
- Straightforward synthesis
- Example: "What is the capital of France?"

**Intent-Planning** (Ambiguous Queries)
- Generate clarifying questions FIRST
- Refine scope through interaction
- Iterative query development
- Example: "Research AI" → Clarify: Which aspect? Applications? Ethics? Recent developments?

**Unified Planning** (Complex/Collaborative)
- Present investigation plan FIRST
- Then EXECUTE the research immediately in the same response
- Provide comprehensive findings after execution
- Example: Multi-faceted research questions requiring structured approach

## Multi-Hop Reasoning Patterns

Track reasoning chains up to 5 hops deep:

**Entity Expansion**
- Person → Affiliations → Related work → Impact → Legacy
- Company → Products → Competitors → Market → Future

**Temporal Progression**
- Current state → Recent changes → Historical context → Trends → Predictions
- Event → Immediate causes → Root causes → Long-term implications

**Conceptual Deepening**
- Overview → Core concepts → Technical details → Applications → Limitations
- Theory → Research → Practice → Results → Future directions

**Causal Chains**
- Observation → Immediate cause → Contributing factors → Root cause → Solutions
- Problem → Analysis → Options → Trade-offs → Recommendations

For each hop (LABEL EXPLICITLY IN YOUR REPORT):
- **[Hop 1]**: State what you're exploring and why it's relevant
- **[Hop 2]**: Explain how it builds on previous findings
- **[Hop 3]**: Continue the chain, showing clear progression
- Assess information quality at each step
- Show genealogy: **[Hop 1] → [Hop 2] → [Hop 3]** in report sections
- Use bold hop labels so the reasoning chain is visually clear

════════════════════════════════════════════════════════════════════════════════
SELF-REFLECTIVE MECHANISMS
════════════════════════════════════════════════════════════════════════════════

## Progress Assessment (After Each Major Step)

Ask yourself:
✓ Have I addressed the core question?
✓ What gaps remain in my understanding?
✓ Is my confidence level improving or declining?
✓ Should I adjust my search strategy?
✓ Do I need to drill deeper or broaden scope?

## Quality Monitoring

**Source Credibility**
- Prefer: Academic, government, established organizations
- Verify: News outlets, blogs, social media
- Flag: Unverifiable claims, outdated info, biased sources

**Information Consistency**
- Cross-reference key facts across multiple sources
- Note contradictions explicitly
- Assess consensus vs outlier views

**Bias Detection**
- Identify potential conflicts of interest
- Note ideological or commercial bias
- Present balanced perspectives

**Completeness Evaluation**
- Have I covered all major aspects?
- Are there obvious knowledge gaps?
- Do I have recent information?

## Replanning Triggers

Replan your approach when:
- Confidence drops below 60%
- Contradictory information exceeds 30%
- Multiple dead ends encountered
- Time/resource constraints emerge
- User provides new direction

════════════════════════════════════════════════════════════════════════════════
EVIDENCE MANAGEMENT
════════════════════════════════════════════════════════════════════════════════

## Result Evaluation

For each finding:
1. **Relevance**: How directly does this address the question?
2. **Reliability**: Is the source authoritative?
3. **Recency**: Is this current information?
4. **Completeness**: Are there gaps in this evidence?

## Citation Standards

**Inline Citations** (MANDATORY - NO EXCEPTIONS)
- Cite sources IMMEDIATELY after EVERY factual claim
- Format: "Claim [Source, Date]"
- Example: "Quantum computing shows promise for drug discovery [Nature, 2024]"
- NEVER list sources only at the end - ALWAYS cite inline first
- Every paragraph with facts MUST have at least one inline citation

**Source Assessment**
- HIGH confidence: Academic papers, government data, technical documentation
- MEDIUM confidence: Reputable news, industry reports, expert blogs
- LOW confidence: Social media, unverified sources, outdated info

**Uncertainty Marking**
- "According to X..." (attributed)
- "Evidence suggests..." (moderate confidence)
- "It appears..." (low confidence)
- "Unverified claim:" (flag dubious info)

════════════════════════════════════════════════════════════════════════════════
4-PHASE RESEARCH WORKFLOW
════════════════════════════════════════════════════════════════════════════════

### PHASE 1: DISCOVERY

**Objectives:**
- Map the information landscape
- Identify authoritative sources
- Detect major themes and patterns
- Establish knowledge boundaries

**Actions:**
1. Broad exploratory searches
2. Survey key sources
3. Note emerging themes
4. Identify knowledge gaps

**Output:** Research map with key areas and sources

---

### PHASE 2: INVESTIGATION

**Objectives:**
- Deep dive into specifics
- Cross-reference information
- Resolve contradictions
- Extract detailed insights

**Actions:**
1. Targeted deep searches
2. Multi-source verification
3. Follow citation chains
4. Investigate discrepancies

**Output:** Detailed findings with evidence

---

### PHASE 3: SYNTHESIS

**Objectives:**
- Build coherent narrative
- Create evidence chains
- Identify remaining gaps
- Generate insights

**Actions:**
1. Connect related findings
2. Construct logical arguments
3. Note evidence strength
4. Acknowledge limitations

**Output:** Integrated analysis

---

### PHASE 4: REPORTING

**Objectives:**
- Structure for audience
- Provide proper citations
- Include confidence levels
- Deliver clear conclusions

**Actions:**
1. Organize by importance
2. Add all citations
3. State confidence explicitly
4. Provide recommendations

**Output:** Comprehensive report

════════════════════════════════════════════════════════════════════════════════
REPORT STRUCTURE
════════════════════════════════════════════════════════════════════════════════

## Executive Summary
- Core finding in 2-3 sentences
- Key takeaways (3-5 bullets)
- **Overall Confidence Level: [High/Medium/Low]** (MANDATORY - always state explicitly)

## Research Methodology
- Query interpretation
- Adaptive strategy used
- Number of hops explored
- Sources consulted

## Key Findings

### Finding 1: [Topic]
**Evidence:** [Sources and data]
**Confidence:** [Level with rationale]
**Limitations:** [Known gaps]

### Finding 2: [Topic]
[Same structure]

## Analysis & Synthesis
- Cross-cutting insights
- Patterns identified
- Contradictions resolved (or noted)
- Implications

## Remaining Questions (MANDATORY - NO EXCEPTIONS)
- What we still don't know (be specific - identify at least 2-3 knowledge gaps)
- Why gaps exist (lack of data, ongoing research, conflicting sources, etc.)
- Suggested follow-up research directions
- NEVER write "None" or "No remaining questions" - every research has gaps

## Conclusions
- Direct answer to original query
- Confidence assessment
- Recommendations

## Sources
- Complete source list with dates
- Source credibility ratings
- Key sources highlighted

## Research Metadata
- Total search iterations: X
- Hop depth reached: X
- Confidence level: X/10
- Research duration: Xs

════════════════════════════════════════════════════════════════════════════════
QUALITY STANDARDS
════════════════════════════════════════════════════════════════════════════════

**Information Quality**
✓ Verify key claims when possible
✓ Prefer recent sources for current topics
✓ Assess reliability explicitly
✓ Detect and mitigate bias

**Synthesis Requirements**
✓ Clear fact vs interpretation
✓ Transparent contradiction handling
✓ Explicit confidence statements
✓ Traceable reasoning chains

**Performance Optimization**
✓ Batch similar searches
✓ Reuse successful patterns
✓ Prioritize high-value sources
✓ Balance depth with efficiency

════════════════════════════════════════════════════════════════════════════════

**Remember:** Think systematically, question critically, cite thoroughly, and synthesize coherently. Your goal is not just to find information, but to understand it deeply and communicate it clearly."""

    def _create_agent(self) -> Agent:
        """Create the underlying Agno agent with Claude model and research tools."""
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions=self.config.instructions,
            markdown=self.config.markdown,
            tools=self._tools if self._tools else []
        )

    def run(
        self,
        prompt: str,
        complexity: Optional[str] = None,
        max_hops: Optional[int] = None,
        **kwargs
    ) -> AgentResult:
        """
        Execute adaptive deep research.

        Args:
            prompt: Research query
            complexity: Hint about query complexity ("simple", "ambiguous", "complex")
            max_hops: Maximum reasoning hops (default: 5)
            **kwargs: Additional parameters

        Returns:
            AgentResult with comprehensive research report
        """
        # Reset hop tracking
        self._hop_count = 0
        self._max_hops = max_hops or 5

        # Detect complexity if not provided
        if complexity is None:
            complexity = self._detect_complexity(prompt)

        # Enhance prompt with complexity guidance
        enhanced_prompt = self._enhance_prompt(prompt, complexity)

        # Execute research
        result = super().run(enhanced_prompt, **kwargs)

        # Add research metadata
        if result.success and result.metadata:
            result.metadata['complexity'] = complexity
            result.metadata['max_hops'] = self._max_hops
            result.metadata['research_type'] = 'adaptive_deep_research'

        return result

    def _detect_complexity(self, prompt: str) -> str:
        """
        Detect query complexity based on prompt characteristics.

        Returns:
            "simple", "ambiguous", or "complex"
        """
        prompt_lower = prompt.lower()

        # Simple indicators
        simple_indicators = [
            'what is', 'who is', 'when did', 'where is',
            'define', 'explain briefly'
        ]

        # Complex indicators
        complex_indicators = [
            'analyze', 'compare', 'comprehensive', 'research',
            'investigate', 'detailed analysis', 'in-depth',
            'all aspects', 'thoroughly'
        ]

        # Ambiguous indicators
        ambiguous_indicators = [
            'about', 'regarding', 'information on',
            'tell me about', 'research', 'look into'
        ]

        # Count words
        word_count = len(prompt.split())

        # Check indicators
        if any(ind in prompt_lower for ind in simple_indicators) and word_count < 15:
            return "simple"

        if any(ind in prompt_lower for ind in complex_indicators) or word_count > 50:
            return "complex"

        if any(ind in prompt_lower for ind in ambiguous_indicators):
            return "ambiguous"

        # Default based on length
        if word_count < 10:
            return "simple"
        elif word_count > 30:
            return "complex"
        else:
            return "ambiguous"

    def _enhance_prompt(self, prompt: str, complexity: str) -> str:
        """
        Enhance prompt with complexity-specific guidance.

        Args:
            prompt: Original research query
            complexity: Detected complexity level

        Returns:
            Enhanced prompt with strategy guidance
        """
        current_date = datetime.now().strftime("%B %d, %Y")

        base = f"""Current Date: {current_date}

Research Query: {prompt}

Query Complexity: {complexity}
"""

        if complexity == "simple":
            guidance = """
Strategy: PLANNING-ONLY
- Execute directly without extensive planning
- Provide concise, accurate answer
- Include 2-3 key sources
- Single-pass synthesis
"""
        elif complexity == "ambiguous":
            guidance = """
Strategy: INTENT-PLANNING
- First, identify what aspects need clarification
- If truly ambiguous, ask clarifying questions
- If reasonably clear, proceed with best interpretation
- Note any assumptions made
"""
        else:  # complex
            guidance = """
Strategy: UNIFIED PLANNING
- Present your research plan first (brief):
  1. Key areas to investigate
  2. Sources to prioritize
  3. Expected depth and scope
- Then IMMEDIATELY EXECUTE the research using your web search tools
- Use multi-hop reasoning as needed (up to 5 hops)
- Provide thorough analysis with proper citations
- DO NOT wait for confirmation - execute the full research in this response
"""

        return base + guidance

    def run_with_reflection(
        self,
        prompt: str,
        min_confidence: float = 0.7,
        max_iterations: int = 3
    ) -> AgentResult:
        """
        Execute research with self-reflection and iteration.

        Args:
            prompt: Research query
            min_confidence: Minimum confidence to accept results (0-1)
            max_iterations: Maximum research iterations

        Returns:
            AgentResult with highest confidence research
        """
        best_result = None
        best_confidence = 0.0

        for iteration in range(max_iterations):
            logger.info(
                f"{self.config.name}: Research iteration {iteration + 1}/{max_iterations}"
            )

            # Run research
            result = self.run(prompt)

            if not result.success:
                continue

            # Estimate confidence (simple heuristic based on content length and structure)
            confidence = self._estimate_confidence(result.content)

            logger.info(f"{self.config.name}: Estimated confidence: {confidence:.2f}")

            # Track best result
            if confidence > best_confidence:
                best_confidence = confidence
                best_result = result

            # Check if we've met threshold
            if confidence >= min_confidence:
                logger.info(
                    f"{self.config.name}: Confidence threshold met "
                    f"({confidence:.2f} >= {min_confidence:.2f})"
                )
                break

            # Enhance prompt for next iteration
            prompt = f"{prompt}\n\nPrevious attempt had gaps. Please provide more comprehensive analysis with additional sources."

        if best_result:
            best_result.metadata['final_confidence'] = best_confidence
            best_result.metadata['iterations'] = iteration + 1

        return best_result or AgentResult(
            success=False,
            content="",
            error="Failed to achieve minimum confidence after all iterations"
        )

    def _estimate_confidence(self, content: str) -> float:
        """
        Estimate confidence level based on content characteristics.

        Simple heuristic based on:
        - Content length
        - Source citations
        - Structural completeness
        - Key section presence

        Returns:
            Confidence score (0-1)
        """
        score = 0.0

        # Length factor (up to 0.2)
        length_score = min(len(content) / 10000, 0.2)
        score += length_score

        # Citation count (up to 0.3)
        citation_indicators = content.count('[') + content.count('Source:')
        citation_score = min(citation_indicators / 20, 0.3)
        score += citation_score

        # Structure sections (up to 0.3)
        required_sections = [
            '# ', '## ', 'Summary', 'Findings', 'Conclusion', 'Sources'
        ]
        section_count = sum(1 for section in required_sections if section in content)
        section_score = (section_count / len(required_sections)) * 0.3
        score += section_score

        # Quantitative data presence (up to 0.2)
        has_numbers = any(char.isdigit() for char in content)
        has_tables = '|' in content and '---' in content
        quant_score = (0.1 if has_numbers else 0) + (0.1 if has_tables else 0)
        score += quant_score

        return min(score, 1.0)


def create_adaptive_researcher(
    model_id: str = "claude-sonnet-4",
    temperature: float = 0.3,
    max_tokens: int = 12000,
    tools: Optional[List] = None
) -> AdaptiveDeepResearchAgent:
    """
    Convenience function to create an adaptive deep research agent.

    Args:
        model_id: Model to use
        temperature: Temperature setting
        max_tokens: Maximum tokens
        tools: List of web search tools (WebSearch, Ollama, MCP, etc.)

    Returns:
        Configured AdaptiveDeepResearchAgent with research tools
    """
    config = AgentConfig(
        name="AdaptiveDeepResearchAgent",
        model_id=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
        markdown=True
    )

    config.instructions = AdaptiveDeepResearchAgent(
        config
    )._build_research_instructions()

    return AdaptiveDeepResearchAgent(config, tools=tools)
