# Meta-Multi-Agent Framework

A comprehensive framework for rapidly generating sophisticated multi-agent systems for any domain using Claude Code. Based on successful patterns from production multi-agent systems like CCPM.

## Overview

This framework enables you to create complete multi-agent systems that include:
- **Hierarchical orchestration** - Commands that coordinate agents and sub-agents
- **Parallel execution** - Safe concurrent work with conflict prevention
- **Context management** - Domain knowledge and state tracking
- **Communication protocols** - Agent coordination through files and events
- **Template-driven generation** - Reusable patterns for rapid development

## Framework Components

### Core Agents
- **`meta-multi-agent`** - Main agent that generates complete multi-agent systems
- **`domain-analyzer`** - Analyzes domain requirements and identifies patterns
- **`orchestrator-builder`** - Creates command orchestration structures
- **`parallel-coordinator`** - Designs safe parallel execution strategies
- **`context-architect`** - Builds context management and documentation systems

### Template Library
- **`orchestrator-command.template.md`** - Template for main orchestration commands
- **`specialist-agent.template.md`** - Template for domain-specific agents
- **`parallel-worker.template.md`** - Template for parallel execution coordinators
- **`coordination-rules.template.md`** - Template for agent coordination rules

## Quick Start

### Basic Usage
```
@meta-multi-agent Create a multi-agent system for managing a restaurant kitchen
```

### Advanced Usage
```
@meta-multi-agent Create a multi-agent system for:
- Domain: Software deployment pipeline
- Requirements: Handle CI/CD, testing, deployment, rollback
- Parallelization: Tests and builds can run in parallel
- Context: Kubernetes environment with multiple environments
```

## Generated System Structure

When you use the meta-multi-agent, it creates a complete `.claude` directory structure:

```
.claude/
├── commands/{domain}/
│   ├── main-workflow.md          # Primary orchestrator command
│   ├── {operation}-{action}.md   # Specific operation commands
│   └── parallel-execute.md       # Parallel execution command
├── agents/
│   ├── {domain}-coordinator.md   # Main coordination agent
│   ├── {specialist}-agent.md     # Domain specialist agents
│   └── parallel-worker.md        # Parallel execution worker
├── rules/
│   ├── {domain}-coordination.md  # Coordination protocols
│   ├── file-access-rules.md      # Conflict prevention rules
│   └── communication-protocol.md # Agent communication rules
├── context/
│   ├── {domain}-overview.md      # Domain knowledge base
│   ├── workflow-patterns.md      # Common workflow patterns
│   └── progress-tracking.md      # State management structure
└── templates/
    └── {domain}-templates/       # Domain-specific templates
```

## Example: Restaurant Kitchen Management System

Let's walk through creating a multi-agent system for restaurant kitchen management:

### 1. Generate the System
```
@meta-multi-agent Create a multi-agent system for restaurant kitchen management that handles:
- Order processing and prioritization
- Kitchen station coordination (prep, grill, salad, dessert)
- Inventory tracking and alerts
- Quality control and timing
- Service coordination with front-of-house

Requirements:
- Kitchen stations can work in parallel on different parts of orders
- Inventory needs real-time tracking
- Quality checks at multiple stages
- Integration with POS system and service staff
```

### 2. Generated Commands
The system would generate commands like:
- `/kitchen:process-orders` - Main workflow for handling orders
- `/kitchen:station-coordination` - Coordinate parallel kitchen stations
- `/kitchen:inventory-check` - Monitor inventory levels
- `/kitchen:quality-control` - Quality assurance workflow

### 3. Generated Agents
Specialized agents would include:
- **kitchen-coordinator** - Orchestrates overall kitchen operations
- **station-manager** - Manages individual kitchen stations (grill, prep, etc.)
- **inventory-tracker** - Monitors supplies and ingredients
- **quality-controller** - Ensures food quality standards
- **service-liaison** - Coordinates with front-of-house

### 4. Usage Example
After generation, you could run:
```
/kitchen:process-orders lunch-rush
```

This would:
1. Analyze incoming orders
2. Break down orders by kitchen station requirements
3. Spawn parallel station-manager agents for each station
4. Coordinate timing between stations
5. Handle quality control checkpoints
6. Coordinate with service staff for pickup

## Key Patterns

### 1. File-Level Parallelism
Agents work on different files to prevent conflicts:
```yaml
Stream A (Prep): prep/*.md, ingredients/*.md
Stream B (Grill): grill/*.md, proteins/*.md
Stream C (Salad): salads/*.md, vegetables/*.md
```

### 2. Progress Communication
Agents communicate through progress files:
```markdown
# station-grill-progress.md
---
---

## Completed Orders
- Order #1234: Burger (medium) - 12:15
- Order #1235: Steak (rare) - 12:18

## Current Orders
- Order #1236: Chicken (well) - ETA 12:25
- Order #1237: Fish (medium) - ETA 12:28

## Issues
- Running low on propane - requested refill
```

### 3. Coordination Rules
Clear rules prevent conflicts:
```markdown
# Kitchen Station Rules
- Each station owns specific ingredient categories
- Shared equipment (ovens) requires explicit coordination
- Quality control checkpoints are sequential, not parallel
- Service handoff happens only after all stations complete
```

## Advanced Features

### Hooks Integration
Generated systems can include hooks for:
- **PreToolUse** - Validate orders before processing
- **PostToolUse** - Update inventory after each order
- **SessionStart** - Initialize kitchen state for new shift

### Context Management
Rich context systems include:
- **Domain knowledge** - Restaurant operations, food safety rules
- **Process documentation** - Standard operating procedures
- **State tracking** - Current orders, inventory levels, staff assignments
- **Integration guides** - POS system, inventory system connections

### Parallel Execution Safety
Built-in safety mechanisms:
- **Conflict detection** - Identify resource conflicts immediately
- **Atomic operations** - Ensure consistent state updates
- **Human escalation** - Clear escalation paths for complex issues
- **Recovery procedures** - How to handle partial failures

## Best Practices

### Domain Analysis
- **Start with workflows** - Understand how work flows through the domain
- **Identify bottlenecks** - Find constraint points that limit throughput
- **Map dependencies** - Understand what depends on what
- **Consider failure modes** - Plan for what goes wrong

### Agent Design
- **Single responsibility** - Each agent has one clear purpose
- **Clear boundaries** - Agents have non-overlapping responsibilities
- **Explicit communication** - How agents coordinate is well-defined
- **Error handling** - Graceful degradation when things fail

### System Architecture
- **Hierarchical coordination** - Commands orchestrate agents orchestrate tasks
- **Context-driven** - Rich context enables intelligent decision making
- **Template-based** - Reusable patterns enable rapid development
- **Documentation-first** - Clear docs make systems maintainable

## Customization

### Extending Generated Systems
After generation, you can:
1. **Add domain-specific agents** - Create specialized agents for unique needs
2. **Customize coordination rules** - Modify how agents communicate
3. **Enhance context** - Add more domain knowledge and documentation
4. **Create additional commands** - Build new orchestration workflows

### Template Customization
You can modify the templates to:
- **Add domain patterns** - Include common patterns for your industry
- **Change coordination styles** - Adjust how agents communicate
- **Modify output formats** - Customize reporting and status formats
- **Include integrations** - Add standard external system connections

## Troubleshooting

### Common Issues
1. **Agents conflicting over files** - Check file access patterns in rules
2. **Complex dependencies** - Consider breaking into smaller work streams
3. **Poor coordination** - Review communication protocols
4. **Context overload** - Focus on essential domain knowledge

### Debug Information
When reporting issues, include:
- **Domain and use case** - What you're trying to build
- **Generated structure** - What files were created
- **Error messages** - Specific failures encountered
- **Expected vs actual** - What you expected vs what happened

## Contributing

To improve the meta-multi-agent framework:
1. **Analyze new domains** - Document patterns from other successful systems
2. **Enhance templates** - Improve template flexibility and reusability
3. **Add coordination patterns** - Document new coordination strategies
4. **Improve documentation** - Make the framework easier to understand and use

## Examples Repository

See the `examples/` directory for complete generated systems:
- **Restaurant Management** - Kitchen, service, and inventory coordination
- **Software Deployment** - CI/CD pipeline with testing and deployment
- **Event Planning** - Vendor coordination, timeline management, logistics
- **Content Creation** - Writing, editing, review, and publishing workflows

---
