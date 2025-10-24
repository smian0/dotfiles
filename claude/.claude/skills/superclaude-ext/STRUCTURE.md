# SuperClaudeExt Architecture

## Directory Structure

```
superclaude-ext/
├── SKILL.md                 # Main skill definition
├── README.md               # User documentation
├── STRUCTURE.md            # This file
├── agents/                 # Agent configurations
│   ├── domain-router.md    # Primary entry point
│   ├── business-panel.md   # 9-expert panel
│   ├── prd-manager.md      # PRD generation
│   ├── product-reviewer.md # Product review
│   ├── market-intel.md     # Market research
│   ├── macro-analyst.md    # Macro briefings
│   ├── market-analyzer.md  # Market analysis
│   ├── research-assistant.md # Research
│   ├── meta-builder.md     # System generation
│   └── framework-validator.md # Validation
├── references/             # Domain guides
│   ├── business-intelligence.md
│   ├── macro-intelligence.md
│   ├── system-framework.md
│   └── migration.md
└── examples/              # Usage examples
    ├── business-analysis.md
    ├── macro-briefing.md
    └── system-generation.md
```

## Architecture Overview

```
User Request
     ↓
[Auto-Activation Detection]
     ↓
domain-router (sonnet)
     ↓
[Domain Classification]
     ├── Business Domain
     │   ├── business-panel (opus)
     │   ├── prd-manager (sonnet)
     │   ├── product-reviewer (sonnet)
     │   └── market-intel (sonnet)
     ├── Macro Domain
     │   ├── macro-analyst (opus)
     │   ├── market-analyzer (sonnet)
     │   └── research-assistant (sonnet)
     ├── System Domain
     │   ├── meta-builder (opus)
     │   └── framework-validator (sonnet)
     └── Utility Domain
         └── (handled by router)
```

## Agent Communication

### Request Flow
1. User input triggers skill activation
2. Domain router analyzes intent
3. Router delegates to appropriate agent
4. Agent processes request
5. Response returned to user

### Context Sharing
- Agents can pass context via Task tool
- Shared memory through file system
- Session context preserved across calls

## Domain Boundaries

### Business Intelligence
**Scope**: Strategic analysis, product management, market research
**Triggers**: Business terminology, strategic questions
**Output**: Analysis reports, PRDs, recommendations

### Macro Intelligence
**Scope**: Economic analysis, market indicators, risk assessment
**Triggers**: Economic terms, market questions, Fed/central banks
**Output**: Briefings, trade ideas, risk alerts

### System Framework
**Scope**: Agent design, system architecture, orchestration
**Triggers**: Multi-agent, system generation, workflow design
**Output**: Agent configurations, orchestration code, documentation

### Utility Tools
**Scope**: Formatting, configuration, simple operations
**Triggers**: Format, clean, standardize
**Output**: Processed files, configurations

## Model Strategy

### Opus Usage (High Complexity)
- business-panel: Deep strategic analysis
- macro-analyst: Complex economic reasoning
- meta-builder: System architecture design

### Sonnet Usage (Balanced)
- domain-router: Intelligent routing
- prd-manager: Structured documentation
- product-reviewer: Code analysis
- market-intel: Research tasks
- market-analyzer: Data analysis
- research-assistant: Information gathering
- framework-validator: Rule checking

## Extension Points

### Adding New Agents
1. Create agent file in `agents/` directory
2. Update domain router with new routing rules
3. Add activation patterns to SKILL.md
4. Document in README.md

### Adding New Domains
1. Create domain section in domain-router
2. Add domain-specific agents
3. Update activation patterns
4. Create reference documentation

### Custom Workflows
1. Extend domain router for workflow detection
2. Create workflow orchestration logic
3. Define inter-agent communication
4. Add workflow documentation

## Performance Considerations

### Token Optimization
- Router uses minimal context for decisions
- Agents receive only relevant information
- Caching prevents redundant operations

### Parallel Processing
- Independent agents can run simultaneously
- Domain router supports batch routing
- Results aggregated efficiently

### Error Recovery
- Each agent has fallback behavior
- Router handles agent failures gracefully
- User prompted when clarification needed

## Integration with SuperClaude

### Command Compatibility
- Legacy `/biz:`, `/macro:`, `/sys:` commands supported
- Commands route through domain router
- Backward compatibility maintained

### Shared Resources
- Access to SuperClaude reference materials
- Shared utility functions
- Common formatting standards

### Migration Path
1. Existing agents wrapped by skill
2. Commands redirect to new structure
3. Gradual transition to unified interface
4. Full backward compatibility

## Quality Standards

### Agent Requirements
- Clear single responsibility
- Well-defined input/output
- Error handling
- Performance metrics
- Documentation

### Testing Strategy
- Unit tests per agent
- Integration tests for routing
- End-to-end workflow tests
- Performance benchmarks

### Documentation Standards
- Agent purpose clearly stated
- Usage examples provided
- Configuration documented
- Troubleshooting guides

## Monitoring and Metrics

### Usage Tracking
- Agent invocation counts
- Response times
- Error rates
- Token usage

### Performance Metrics
- Routing accuracy
- Agent success rates
- Response quality scores
- User satisfaction

### Improvement Process
1. Collect usage metrics
2. Identify patterns
3. Optimize routing rules
4. Enhance agent capabilities
5. Update documentation