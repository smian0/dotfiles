# Business Intelligence Domain Guide

## Overview

The Business Intelligence domain provides comprehensive strategic analysis through expert perspectives, product management tools, and market research capabilities.

## Available Agents

### business-panel
Elite 9-expert panel providing strategic business analysis from multiple perspectives:
- Peter Thiel (Contrarian Strategy)
- Jeff Bezos (Customer Obsession)
- Reid Hoffman (Network Effects)
- Ben Horowitz (Operational Excellence)
- Marc Andreessen (Technology Disruption)
- Mary Meeker (Market Intelligence)
- Michael Porter (Competitive Strategy)
- Clayton Christensen (Innovation Theory)
- Jim Collins (Organizational Excellence)

**Best for**: Strategic decisions, market entry, competitive positioning, growth strategy

### prd-manager
Product requirement document specialist for comprehensive product planning:
- User story generation
- Acceptance criteria definition
- Technical specifications
- Implementation roadmaps

**Best for**: New features, product launches, technical planning, stakeholder alignment

### product-reviewer
Technical product and architecture reviewer:
- Code quality assessment
- Architecture evaluation
- Security review
- Performance analysis

**Best for**: Code reviews, technical audits, refactoring decisions, quality assurance

### market-intel
Market intelligence and competitive research:
- Market sizing (TAM/SAM/SOM)
- Competitive analysis
- Trend identification
- Opportunity assessment

**Best for**: Market entry, competitive strategy, investment decisions, product positioning

## Common Use Cases

### Strategic Planning
```
@superclaude-ext/business-panel analyze our B2B SaaS expansion into Europe
```

### Product Development
```
@superclaude-ext/prd-manager create PRD for multi-tenant architecture
```

### Market Research
```
@superclaude-ext/market-intel analyze fintech market opportunities in payments
```

### Technical Review
```
@superclaude-ext/product-reviewer review our microservices architecture
```

## Frameworks and Methods

### Business Analysis Frameworks
- **Porter's Five Forces**: Industry competitive analysis
- **SWOT Analysis**: Strengths, weaknesses, opportunities, threats
- **BCG Matrix**: Product portfolio analysis
- **Value Chain Analysis**: Activity optimization
- **Blue Ocean Strategy**: Market creation

### Product Management Methods
- **Jobs-to-be-Done**: Customer need analysis
- **Lean Canvas**: Business model design
- **Design Thinking**: Innovation process
- **Agile/Scrum**: Development methodology
- **OKRs**: Goal setting and tracking

### Market Research Techniques
- **TAM/SAM/SOM**: Market sizing
- **Competitive Positioning**: 2x2 matrices
- **Customer Segmentation**: Target analysis
- **Trend Analysis**: Future projection
- **PESTEL Analysis**: Macro environment

## Best Practices

### For Strategic Analysis
1. Define clear objectives and constraints
2. Provide context about industry and company
3. Specify time horizons for recommendations
4. Include relevant financial metrics
5. Mention key stakeholders

### For Product Planning
1. Start with user problems, not solutions
2. Include acceptance criteria for all stories
3. Prioritize features using MoSCoW or similar
4. Define clear success metrics
5. Consider technical debt and scalability

### For Market Research
1. Specify geographic focus
2. Define target customer segments
3. Include competitor names if known
4. Mention relevant regulations
5. Provide budget constraints if applicable

## Integration Examples

### Multi-Agent Workflows

**Comprehensive Business Analysis**:
1. market-intel: Gather market data
2. business-panel: Strategic analysis
3. prd-manager: Implementation plan
4. product-reviewer: Feasibility assessment

**Product Launch Planning**:
1. market-intel: Market opportunity
2. prd-manager: Product specification
3. business-panel: Go-to-market strategy
4. product-reviewer: Technical validation

## Output Formats

### Executive Briefing
- Executive summary (2-3 sentences)
- Key findings (bullet points)
- Recommendations (prioritized)
- Risks and mitigations
- Next steps with owners

### Detailed Analysis
- Context and objectives
- Methodology
- Detailed findings
- Supporting data
- Appendices

### Action Plan
- Immediate actions (0-30 days)
- Short-term initiatives (30-90 days)
- Long-term strategy (90+ days)
- Success metrics
- Resource requirements

## Tips for Effective Use

1. **Be Specific**: Provide industry, company size, and context
2. **Set Boundaries**: Define what's in and out of scope
3. **Provide Data**: Share relevant metrics and benchmarks
4. **Clarify Goals**: State desired outcomes clearly
5. **Iterate**: Use findings to refine questions

## Common Pitfalls to Avoid

1. **Vague Requests**: "Analyze our business" vs "Analyze our SaaS pricing strategy"
2. **Missing Context**: Forgetting to mention industry or competition
3. **Unclear Timeline**: Not specifying urgency or timeframe
4. **No Success Criteria**: Failing to define what success looks like
5. **Information Overload**: Requesting everything instead of prioritizing

## Advanced Techniques

### Scenario Planning
Use business-panel with multiple scenarios:
```
@superclaude-ext/business-panel analyze three scenarios:
1. Aggressive expansion
2. Conservative growth
3. Pivot to new market
```

### Competitive War Gaming
Combine market-intel and business-panel:
```
@superclaude-ext/market-intel competitor analysis
→ @superclaude-ext/business-panel competitive response strategy
```

### Product-Market Fit Analysis
Sequential analysis:
```
@superclaude-ext/market-intel identify customer needs
→ @superclaude-ext/prd-manager design solution
→ @superclaude-ext/business-panel evaluate fit
```