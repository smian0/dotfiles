---
name: superclaude-ext
description: Comprehensive multi-domain intelligence framework providing business analysis, macro intelligence, system generation, and utility tools
---

# SuperClaudeExt Skill

> Comprehensive multi-domain intelligence framework providing business analysis, macro intelligence, system generation, and utility tools

## Metadata
- **Version**: 1.0.0
- **Author**: SuperClaude Framework
- **License**: MIT
- **Model**: sonnet (router), opus/sonnet (domain agents)

## Overview

SuperClaudeExt is a unified skill that consolidates multiple advanced capabilities across four primary domains:

1. **Business Intelligence** (`/biz:`) - Expert panel analysis, PRD generation, product review
2. **Macro Intelligence** (`/macro:`) - Economic briefings, market analysis, risk assessment
3. **System Framework** (`/sys:`) - Meta-agent generation, framework validation
4. **Utility Tools** (`/util:`) - Code formatting, configuration management

## Auto-Activation Patterns

The skill automatically activates when detecting:

### Natural Language Triggers
- **Business Domain**: "business analysis", "expert panel", "business panel", "PRD", "product review", "market research", "competitive analysis", "business strategy"
- **Macro Domain**: "macro briefing", "market analysis", "economic intelligence", "risk assessment", "portfolio analysis", "market indicators", "Fed policy"
- **System Domain**: "generate agent", "create sub-agent", "multi-agent system", "meta builder", "framework validation", "agent architecture"
- **Utility Domain**: "format code", "standardize", "AGENTS.md", "agent configuration"

### Slash Command Triggers
- `/biz:*` - All business intelligence commands
- `/macro:*` - All macro intelligence commands
- `/sys:*` - All system framework commands
- `/util:*` - All utility commands
- `/superclaude-ext` - Direct skill invocation

## Architecture

```
superclaude-ext/
├── domain-router (primary entry point)
├── business/
│   ├── business-panel
│   ├── prd-manager
│   ├── product-reviewer
│   └── market-intel
├── macro/
│   ├── macro-analyst
│   ├── market-analyzer
│   └── research-assistant
├── system/
│   ├── meta-builder
│   └── framework-validator
└── utility/
    └── (integrated into router)
```

## Domain Router Logic

The domain router (`@superclaude-ext/domain-router`) serves as the intelligent entry point:

1. **Context Analysis**: Examines user intent, keywords, and patterns
2. **Domain Classification**: Maps request to appropriate domain
3. **Agent Selection**: Routes to specific sub-agent or handles directly
4. **Fallback Handling**: Provides clarification for ambiguous requests

### Routing Rules

```yaml
Priority Order:
1. Explicit slash commands (/biz:, /macro:, etc.)
2. Strong keyword matches (>90% confidence)
3. Context patterns (code, business terms, economic indicators)
4. User clarification prompt (ambiguous cases)
```

## Sub-Agent Registry

### Business Intelligence Domain

**@superclaude-ext/business-panel**
- Purpose: 9-expert business analysis panel
- Model: opus
- Capabilities: Strategic analysis, market positioning, growth strategies

**@superclaude-ext/prd-manager**
- Purpose: PRD generation and implementation
- Model: sonnet
- Capabilities: Requirements specification, feature definition, acceptance criteria

**@superclaude-ext/product-reviewer**
- Purpose: Product development review and architecture analysis
- Model: sonnet
- Capabilities: Code review, architecture assessment, improvement recommendations

**@superclaude-ext/market-intel**
- Purpose: Market intelligence and competitive research
- Model: sonnet
- Capabilities: Competitor analysis, market trends, opportunity identification

### Macro Intelligence Domain

**@superclaude-ext/macro-analyst**
- Purpose: Elite macro economic intelligence
- Model: opus
- Capabilities: Economic indicators, central bank policy, risk assessment

**@superclaude-ext/market-analyzer**
- Purpose: Cross-asset market analysis
- Model: sonnet
- Capabilities: Equity, bonds, FX, commodities analysis

**@superclaude-ext/research-assistant**
- Purpose: Multi-source research and validation
- Model: sonnet
- Capabilities: Data collection, source validation, report generation

### System Framework Domain

**@superclaude-ext/meta-builder**
- Purpose: Multi-agent system generation
- Model: opus
- Capabilities: Agent design, workflow orchestration, system architecture

**@superclaude-ext/framework-validator**
- Purpose: Validation and compliance checking
- Model: sonnet
- Capabilities: Code validation, pattern compliance, best practices enforcement

## Usage Examples

### Natural Language
```
User: I need a business analysis of our new product launch
→ Activates @superclaude-ext/business-panel

User: Generate a macro briefing for today's Fed meeting
→ Activates @superclaude-ext/macro-analyst

User: Create a multi-agent system for customer support
→ Activates @superclaude-ext/meta-builder
```

### Slash Commands
```
/biz:panel "Analyze market opportunity for AI assistants"
/macro:brief
/sys:generate "Create trading bot architecture"
/util:format main.py
```

### Direct Agent Access
```
@superclaude-ext/business-panel analyze competitor strategy
@superclaude-ext/macro-analyst Fed impact assessment
@superclaude-ext/meta-builder design authentication system
```

## Configuration

### Model Preferences
```yaml
defaults:
  router: sonnet
  business: opus    # High-quality analysis
  macro: opus       # Complex economic analysis
  system: opus      # System generation
  utility: sonnet   # Balanced performance
```

### Tool Access
All agents have access to:
- Read, Write, Edit (document operations)
- Bash (system commands)
- Task (sub-agent delegation)
- WebSearch, WebFetch (research)
- Grep, Glob (code analysis)

## Integration

### Migration from Standalone Commands

Existing commands are preserved for backward compatibility:
- `/biz:` commands → Routed through business domain
- `/macro:` commands → Routed through macro domain
- `/sys:` commands → Routed through system domain

### Extending the Skill

Add new agents by:
1. Creating agent file in appropriate domain folder
2. Updating domain router routing rules
3. Adding activation patterns to this file

## Performance Optimization

- **Intelligent Routing**: Minimizes token usage through smart delegation
- **Model Selection**: Uses appropriate model sizes for each task
- **Parallel Processing**: Supports concurrent agent execution where applicable
- **Context Caching**: Reuses context across related requests

## Troubleshooting

### Common Issues

**Skill Not Activating**
- Check activation patterns match your request
- Use explicit slash commands for direct access
- Verify skill is installed in correct location

**Wrong Agent Selected**
- Be more specific in your request
- Use direct agent access syntax
- Check domain router logs for routing decisions

**Performance Issues**
- Review model selection for each agent
- Check for recursive delegation loops
- Monitor token usage across agents

## References

- [Business Intelligence Guide](references/business-intelligence.md)
- [Macro Intelligence Guide](references/macro-intelligence.md)
- [System Framework Guide](references/system-framework.md)
- [Migration Guide](references/migration.md)