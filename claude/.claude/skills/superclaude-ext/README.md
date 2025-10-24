# SuperClaudeExt Skill

> Comprehensive multi-domain intelligence framework for Claude Code

## Quick Start

```bash
# Business analysis with expert panel
/biz:panel analyze our SaaS pricing strategy

# Macro economic briefing
/macro:brief

# Generate multi-agent system
/sys:generate customer support system

# Direct agent access
@superclaude-ext/business-panel analyze competitor landscape
```

## Features

- **Business Intelligence**: 9-expert strategic analysis panel, PRD generation, market research
- **Macro Intelligence**: Economic briefings, cross-asset analysis, risk assessment
- **System Framework**: Multi-agent system generation, orchestration patterns
- **Intelligent Routing**: Automatic domain detection and agent delegation

## Installation

The skill is automatically available in Claude Code when placed in:
- User-level: `~/.claude/skills/superclaude-ext/`
- Project-level: `.claude/skills/superclaude-ext/`

## Available Agents

### Business Domain
- `@superclaude-ext/business-panel` - Elite 9-expert analysis
- `@superclaude-ext/prd-manager` - PRD generation
- `@superclaude-ext/product-reviewer` - Product review
- `@superclaude-ext/market-intel` - Market intelligence

### Macro Domain
- `@superclaude-ext/macro-analyst` - Economic intelligence
- `@superclaude-ext/market-analyzer` - Market analysis
- `@superclaude-ext/research-assistant` - Research validation

### System Domain
- `@superclaude-ext/meta-builder` - System generation
- `@superclaude-ext/framework-validator` - Validation

## Usage Examples

### Natural Language Activation
```
"I need a business analysis of our new AI product"
→ Automatically routes to business-panel

"What's the Fed's impact on markets?"
→ Automatically routes to macro-analyst

"Create a multi-agent customer support system"
→ Automatically routes to meta-builder
```

### Slash Commands
```bash
# Business commands
/biz:panel "Analyze market opportunity"
/biz:prd "Design authentication system"

# Macro commands
/macro:brief
/macro:analyze SPY

# System commands
/sys:generate "Trading bot architecture"
/sys:validate existing-system.md
```

### Direct Agent Access
```
@superclaude-ext/business-panel competitive analysis for fintech
@superclaude-ext/macro-analyst Fed meeting impact assessment
@superclaude-ext/meta-builder design authentication workflow
```

## Domain Detection

The skill automatically detects domain based on keywords:

**Business**: strategy, PRD, product, market, competitive, revenue, growth
**Macro**: Fed, ECB, inflation, GDP, trading, portfolio, risk
**System**: agent, multi-agent, orchestration, workflow, automation

## Configuration

Agents use optimized models:
- **Business Panel**: Opus (comprehensive analysis)
- **Macro Analyst**: Opus (complex reasoning)
- **Meta Builder**: Opus (system design)
- **Others**: Sonnet (balanced performance)

## Migration from Legacy Commands

Existing commands continue to work:
- `/biz:*` commands → Business domain
- `/macro:*` commands → Macro domain
- `/sys:*` commands → System domain

## Advanced Features

### Parallel Agent Execution
Multiple agents can work simultaneously on different aspects of a problem.

### Context Preservation
Agents share context within a session for coherent analysis.

### Intelligent Fallback
Ambiguous requests prompt for clarification rather than guessing.

## Troubleshooting

**Skill not activating?**
- Check keywords match activation patterns
- Use explicit slash commands
- Try direct agent access with `@superclaude-ext/`

**Wrong agent selected?**
- Be more specific in request
- Use direct agent syntax
- Check [SKILL.md](SKILL.md) for routing rules

---
*For detailed documentation, see [SKILL.md](SKILL.md)*