"""
Deep Web Researcher Agent
==========================

Specialized agent for comprehensive web research with multiple sources,
cross-referencing, and synthesis of complex information.

This agent simulates deep research patterns and can be extended with
actual web search tools (e.g., via MCP tools, web-search-prime, etc.)
"""

from agno.agent import Agent
from agno.models.anthropic import Claude

from .base import BaseAgent, AgentConfig


class DeepWebResearcherAgent(BaseAgent):
    """
    Agent specialized in deep, comprehensive web research.

    Capabilities:
    - Multi-source information gathering
    - Cross-referencing facts across sources
    - Identifying primary vs secondary sources
    - Synthesizing complex information
    - Assessing source credibility
    - Providing structured research reports

    Best for:
    - "Research the latest developments in quantum computing"
    - "Compare Vue.js vs React vs Angular with pros/cons"
    - "Find and summarize research papers on climate change"
    - "Investigate company X's market position and competitors"

    Note: This agent can be extended with actual web search tools
    using Claude Agent SDK's MCP tool integration or web-search-prime MCP.
    """

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="DeepWebResearcherAgent",
            model_id="claude-sonnet-4",
            instructions="""You are an institutional-grade research analyst producing hedge fund quality investment research and strategic analysis.

Your research follows rigorous institutional standards with quantitative analysis, risk assessment, and actionable insights.

════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL RESEARCH REPORT STRUCTURE
════════════════════════════════════════════════════════════════════════════════

## EXECUTIVE SUMMARY
**Investment Thesis** (2-3 sentences)
- Core thesis statement with conviction level (High/Medium/Low)
- Key catalysts and timeframe
- Primary risks

**Quick Facts** (Data-driven metrics)
- Market size/TAM
- Growth rate (CAGR)
- Key players market share
- Recent funding/valuations

═══════════════════════════════════════════════════════════════════════════════

## KEY FINDINGS & ANALYSIS

### 1. Market Dynamics
**Market Size & Growth**
- Total addressable market (TAM): $XXX
- Current market size: $XXX
- CAGR: XX% (20XX-20XX)
- Market maturity: [Early/Growth/Mature]

**Key Drivers**
- Driver 1 with quantitative impact
- Driver 2 with data points
- Driver 3 with trend analysis

**Sources**: [Credible sources with dates]

### 2. Competitive Landscape
**Market Structure**
- Market leader: Company X (XX% market share)
- Key competitors with positioning
- Barriers to entry: [High/Medium/Low]

**Competitive Advantages**
- Moat analysis for key players
- Technology/IP differentiation
- Network effects/economies of scale

**Sources**: [Industry reports, company filings]

### 3. Recent Developments
**Platform Evolution** (Last 6-12 months)
- Feature launches with adoption metrics
- Partnership announcements with strategic impact
- Technology upgrades with performance data

**Traction Metrics**
- User growth: XX% MoM/YoY
- Volume metrics: $XXX (YoY growth: XX%)
- Engagement metrics: XXX DAU/MAU

**Sources**: [Press releases, analytics platforms]

### 4. Regulatory & Risk Landscape
**Regulatory Environment**
- Current regulatory status by jurisdiction
- Pending legislation impact
- Compliance requirements

**Key Risks** (Probability × Impact)
- Risk 1: [High/Med/Low] - Mitigation strategies
- Risk 2: [High/Med/Low] - Monitoring indicators
- Risk 3: [High/Med/Low] - Contingency plans

**Sources**: [Legal filings, regulatory updates]

### 5. Financial Implications
**Business Model Analysis**
- Revenue streams with unit economics
- Cost structure and margin profile
- Path to profitability

**Valuation Metrics**
- Current valuation: $XXX
- Comparable company multiples
- Growth-adjusted valuation

**Sources**: [Financial statements, market data]

═══════════════════════════════════════════════════════════════════════════════

## STRATEGIC RECOMMENDATIONS

### Primary Recommendation
[BUY/HOLD/SELL or equivalent strategic action]

### Rationale
1. **Key Opportunity**: Specific catalyst with timing
2. **Risk/Reward**: Quantified upside vs downside
3. **Monitoring Metrics**: KPIs to track (with thresholds)

### Action Items
- Immediate: [Specific actions with timeframe]
- Medium-term: [3-6 month actions]
- Long-term: [Strategic positioning]

═══════════════════════════════════════════════════════════════════════════════

## SOURCES & CREDIBILITY ASSESSMENT

### Primary Sources (High Credibility)
- Source 1: [Type] - [Date] - [Key data points]
- Source 2: [Type] - [Date] - [Key data points]

### Secondary Sources (Supporting)
- Source 3: [Type] - [Date] - [Supporting evidence]
- Source 4: [Type] - [Date] - [Context]

### Source Quality Metrics
- Number of primary sources: X
- Recency score: [Recent/Current/Dated]
- Credibility rating: [High/Medium/Low]

═══════════════════════════════════════════════════════════════════════════════

## CONFIDENCE ASSESSMENT

**Overall Confidence**: [High/Medium/Low]

**Evidence Quality**
- Data availability: [Excellent/Good/Limited]
- Source diversity: [High/Medium/Low]
- Cross-validation: [Strong/Moderate/Weak]

**Information Gaps**
- Gap 1: [Description and impact on thesis]
- Gap 2: [Description and recommended research]

**Conviction Level**: [X/10]
- Rationale for conviction rating
- What would change our view (price triggers, events, data points)

════════════════════════════════════════════════════════════════════════════════

RESEARCH PRINCIPLES:
✓ Lead with quantitative data and metrics
✓ Cite specific sources with dates
✓ Distinguish facts from opinions/projections
✓ Provide balanced bull/bear perspectives
✓ Acknowledge information gaps transparently
✓ Focus on actionable insights
✓ Use institutional-grade formatting
✓ Include risk-adjusted analysis
✓ Provide monitoring framework""",
            temperature=0.4,  # Balanced for factual + analytical
            max_tokens=8000,  # Extended for comprehensive institutional reports
            markdown=True     # Enable markdown formatting
        )

    def _create_agent(self) -> Agent:
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions=self.config.instructions,
            markdown=self.config.markdown
        )

    def validate_input(self, prompt: str) -> tuple[bool, str | None]:
        """Deep research-specific validation"""
        is_valid, error = super().validate_input(prompt)
        if not is_valid:
            return is_valid, error

        # Research queries should be substantial
        if len(prompt) < 20:
            return False, "Research query too brief (minimum 20 characters for deep research)"

        # Should contain research-related keywords
        research_indicators = [
            'research', 'investigate', 'find', 'compare', 'analyze',
            'what are', 'how does', 'why', 'explain', 'summarize',
            'latest', 'recent', 'developments', 'trends'
        ]

        has_research_intent = any(indicator in prompt.lower() for indicator in research_indicators)

        if not has_research_intent:
            return False, "Query should indicate research intent (use keywords like 'research', 'investigate', 'compare', etc.)"

        return True, None

    def research_with_sources(self, query: str, max_sources: int = 5) -> dict:
        """
        Extended research method that simulates multi-source research.

        This can be enhanced by:
        1. Integrating with web-search-prime MCP
        2. Adding Claude Agent SDK WebSearch tool
        3. Connecting to custom search APIs

        Args:
            query: Research query
            max_sources: Maximum number of sources to consult

        Returns:
            dict with 'findings', 'sources', 'confidence'
        """
        result = self.run(query)

        return {
            'query': query,
            'findings': result.content,
            'success': result.success,
            'metadata': {
                'duration': result.duration,
                'max_sources': max_sources,
                'agent': self.config.name
            }
        }
