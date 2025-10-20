# Web-Researcher Agent Prompt Template

Use this template when spawning web-researcher agents in Phase 1 (Discovery).

Replace placeholders: `{research_question}`, `{stream_number}`, `{angle_name}`, `{angle_description}`, `{key_areas}`, `{current_date}`, `{current_year}`

**CRITICAL**: Always use `{current_year}` for year references in search queries and focus areas. Never hardcode years like "2024" or "2025".

---

## Prompt Template

```
Research {angle_description} for the question: {research_question}

## Your Research Focus
{Detailed description of what this stream should investigate. Be specific about:
- Primary focus areas
- Types of evidence to prioritize
- Stakeholder perspectives to include
- Temporal scope (recent events vs historical context)}

## Key Areas to Cover
{key_areas}
Example:
- Price trends and market data (last 6 months)
- Institutional investment patterns
- Retail investor sentiment indicators
- Market structure changes

## Deliverables Required

1. **10-20 quality sources** with:
   - Source name and URL
   - Credibility assessment (A/B/C tier)
   - Key findings summary
   - Specific data points with dates

2. **Source diversity**:
   - Primary sources (government, official data, on-chain if applicable)
   - Secondary sources (established media, research firms)
   - Geographic diversity where applicable
   - Mix of perspectives (not just consensus views)

3. **Structured output** at ./research-output/sources/stream-{stream_number}-sources-{current_date}.md:

```markdown
# Stream {stream_number}: {angle_name}
**Date**: {current_date}
**Research Period**: [Date range of sources examined]

## Executive Summary
[3-5 bullet points of key findings]

## Key Sources

### [Source 1 Name]
- **Type**: Primary/Secondary/Tertiary
- **URL**: [link]
- **Credibility**: A/B/C tier
- **Key Findings**:
  - [Finding with specific data]
  - [Finding with dates]
- **Relevant Quotes**: [If applicable]

[Repeat for 10-20 sources]

## Additional Context
[Background information, trends, patterns observed]
```

## Research Rigor Standards

Execute research using:

1. **Multiple search queries** with different angles
   - Direct question format
   - Different terminology
   - Related concepts
   - Temporal variations

2. **Adversarial search** (test contrary perspectives)
   - "Why [assumption] might be wrong"
   - "Criticisms of [mainstream view]"
   - "Alternative explanations for [phenomenon]"

3. **Source diversity** (not just top results)
   - Different publishers
   - Different geographic regions
   - Different stakeholder perspectives
   - Mix of quantitative and qualitative sources

4. **Primary source prioritization**
   - Government reports over news articles
   - Research papers over summaries
   - Official data over aggregators
   - Company filings over analyst commentary

5. **Date verification** for current events
   - Publication date
   - Data collection period
   - Last updated timestamp
   - Relevance to current situation

## Source Credibility Guidelines

**A-Tier: High Credibility**
- Government agencies, regulatory bodies
- Academic peer-reviewed research
- Official data sources
- Primary documents, filings

**B-Tier: Medium Credibility**
- Established news media
- Reputable research firms
- Industry associations
- Expert opinions (verified)

**C-Tier: Needs Verification**
- Single-source reporting
- Opinion pieces without evidence
- Social media claims
- Unverified data

## Quality Standards

Your research MUST achieve:
- ✅ 10-20 documented sources
- ✅ 80%+ A/B tier credibility
- ✅ Geographic/institutional diversity
- ✅ Specific data points with dates
- ✅ Both supporting and contrary evidence
- ✅ Primary sources when available

Deliver rigorous, comprehensive research suitable for professional analysis.
```

---

## Usage Example

For research question: "Why is cryptocurrency market suffering in {current_year}?"

**IMPORTANT**: Get current date first with `date "+%Y-%m-%d %H:%M:%S %Z"` to determine {current_year} and {current_date}

Stream 1: Market Analysis
```python
Task(
    subagent_type="web-researcher",
    description="Stream 1: Market analysis & price trends",
    prompt=f"""
Research market analysis and price trends for the question: Why is cryptocurrency market suffering in {current_year}?

**CURRENT DATE: {current_date}**
**CURRENT YEAR: {current_year}**

## Your Research Focus
Investigate quantitative market data, price movements, trading volumes, and market structure changes. Focus on:
- Bitcoin and major altcoin price trends (last 6 months through {current_date})
- Trading volume analysis across major exchanges
- Market capitalization changes
- Institutional vs retail investor flows
- Derivatives market indicators (futures, options)

## Key Areas to Cover
- Price trends across major cryptocurrencies (BTC, ETH, SOL, etc.)
- Trading volume patterns and liquidity changes
- Market maker and exchange dynamics
- Correlation with traditional markets (stocks, bonds)
- On-chain metrics (active addresses, transaction volumes)

## Search Strategy
Use search queries with {current_year} and recent timeframes:
- "Bitcoin price {current_year}"
- "crypto market trends October {current_year}"
- "BTC ETH price analysis {current_year}"

[... rest of template ...]
"""
)
```

Stream 2: Regulatory Impact
```python
Task(
    subagent_type="web-researcher",
    description="Stream 2: Regulatory & policy impact",
    prompt=f"""
Research regulatory and policy impact for the question: Why is cryptocurrency market suffering in {current_year}?

**CURRENT DATE: {current_date}**
**CURRENT YEAR: {current_year}**

## Your Research Focus
Investigate government regulations, policy changes, enforcement actions, and legal developments affecting crypto markets in {current_year}. Focus on:
- US regulatory actions (SEC, CFTC, Treasury)
- International regulatory developments
- Exchange shutdowns or restrictions
- Legal precedents and court cases
- Policy announcements and their market impact

## Search Strategy
- "crypto regulation {current_year}"
- "SEC crypto enforcement October {current_year}"
- "crypto policy changes {current_year}"

[... rest of template ...]
"""
)
```

---

## Customization Guidelines

**Adjust for domain**:
- Financial research: Emphasize data sources, official reports
- Technical research: Prioritize documentation, code repositories
- Policy research: Focus on government sources, think tanks
- Scientific research: Require peer-reviewed papers

**Adjust for depth**:
- Shallow: 5-10 sources, basic verification
- Medium: 10-15 sources, standard rigor
- Deep: 15-20 sources, comprehensive adversarial search

**Adjust for urgency**:
- Time-sensitive: Focus on recent sources (last 7-30 days)
- Historical: Include historical context and trends
- Comparative: Require temporal comparison across periods
