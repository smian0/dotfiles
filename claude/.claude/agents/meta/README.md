# Meta-Multi-Agent Framework

A comprehensive framework for rapidly generating sophisticated multi-agent systems for any domain using Claude Code. Based on successful patterns from production multi-agent systems like CCPM and the `/research` orchestrator.

## Overview

This framework enables you to create complete multi-agent systems that include:
- **Hierarchical orchestration** - Commands that coordinate agents and sub-agents
- **Parallel execution** - Safe concurrent work with conflict prevention
- **Context management** - Domain knowledge and state tracking
- **Communication protocols** - Agent coordination through files and events
- **Automated validation** - Quality gates and safety checks

## How It Works

### Orchestration Command: `/multi-agent`

**The primary way to use this framework** is through the `/multi-agent` orchestration command located at `commands/multi-agent.md`. This command automatically coordinates all meta-framework agents to generate complete systems.

**Usage**:
```bash
/multi-agent [domain description]
```

**Example**:
```bash
/multi-agent Create a multi-agent system for restaurant kitchen management that handles order processing, station coordination, inventory tracking, and quality control
```

The command orchestrates these agents in a 9-phase workflow:
1. Parse domain requirements
2. **Parallel**: domain-analyzer + context-architect analyze patterns
3. orchestrator-builder designs command structure
4. meta-multi-agent generates orchestrator command
5. meta-multi-agent generates specialist agents (sequential for safety)
6. parallel-coordinator generates coordination rules
7. context-architect generates context documentation
8. Validation phase (YAML syntax, structure, content)
9. Documentation generation

### Framework Components (Agents in `agents/meta/`)

These agents are **spawned automatically** by the `/multi-agent` command:

- **`meta-multi-agent`** - Main agent that generates complete multi-agent systems
- **`domain-analyzer`** - Analyzes domain requirements and identifies patterns
- **`context-architect`** - Builds context management and documentation systems
- **`orchestrator-builder`** - Creates command orchestration structures
- **`parallel-coordinator`** - Designs safe parallel execution strategies
- **`meta-sub-agent`** - Generates individual agent files

**Note**: You typically don't invoke these agents directly. Use `/multi-agent` instead.

## Quick Start

### Recommended: Use the Orchestrator Command
```bash
# Full automation - recommended approach
/multi-agent Create a multi-agent system for managing a restaurant kitchen

# With detailed requirements
/multi-agent Create a multi-agent system for:
- Domain: Software deployment pipeline
- Requirements: Handle CI/CD, testing, deployment, rollback
- Parallelization: Tests and builds can run in parallel
- Context: Kubernetes environment with multiple environments
```

### Advanced: Manual Agent Invocation
For specialized use cases, you can invoke individual agents:
```bash
# Generate a single agent (not a complete system)
@meta-sub-agent Create an inventory-tracker agent for restaurant management

# Manual system generation (not recommended - use /multi-agent instead)
@meta-multi-agent Create a multi-agent system for [domain]
```

**Warning**: Manual invocation requires you to coordinate agents yourself. Use `/multi-agent` for automated orchestration.

## Generated System Structure

When you run `/multi-agent [domain]`, it creates a complete `.claude` directory structure:

```
.claude/
├── commands/{domain-slug}/
│   ├── main-workflow.md          # Primary orchestrator command
│   └── {operation}-{action}.md   # Specific operation commands (optional)
│
├── agents/{domain-slug}/         # Separate directory per domain
│   ├── {specialist}-agent.md     # Domain specialist agents
│   └── {coordinator}-agent.md    # Coordination agents
│
├── rules/{domain-slug}/
│   ├── coordination-protocol.md  # How agents communicate
│   ├── file-access-rules.md      # Conflict prevention rules
│   └── error-escalation.md       # When to fail vs retry
│
├── context/{domain-slug}/
│   ├── {domain}-overview.md      # Domain knowledge base
│   ├── workflow-patterns.md      # Common workflow patterns
│   └── progress-tracking.md      # State management templates
│
└── {domain-slug}-README.md       # Complete usage documentation
```

**Note**: Generated agents go in `agents/{domain-slug}/` to keep them separate from framework agents in `agents/meta/` and `agents/research/`.

## Example: Restaurant Kitchen Management System

Let's walk through creating a multi-agent system for restaurant kitchen management:

### 1. Generate the System
```bash
/multi-agent Create a multi-agent system for restaurant kitchen management that handles:
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

**What happens**: The `/multi-agent` command automatically:
- Analyzes restaurant kitchen domain patterns
- Designs orchestration architecture
- Generates all files (commands, agents, rules, context)
- Validates YAML syntax and structure
- Creates comprehensive documentation

**Runtime**: ~2-5 minutes for complete system generation

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
After generation completes, you get a complete working system:

**Generated files**:
```
.claude/
├── commands/restaurant-kitchen/
│   └── main-workflow.md
├── agents/restaurant-kitchen/
│   ├── kitchen-coordinator.md
│   ├── station-manager.md
│   ├── inventory-tracker.md
│   ├── quality-controller.md
│   └── service-liaison.md
├── rules/restaurant-kitchen/
│   └── coordination-protocol.md, file-access-rules.md, error-escalation.md
├── context/restaurant-kitchen/
│   └── domain-overview.md, workflow-patterns.md, progress-tracking.md
└── restaurant-kitchen-README.md
```

**Run the system**:
```bash
/restaurant-kitchen:main-workflow lunch-rush
```

**What happens**:
1. Main workflow command validates prerequisites
2. Analyzes incoming orders
3. Spawns parallel station-manager agents (prep, grill, salad, dessert)
4. Each agent works on its assigned station (file-level parallelism)
5. quality-controller validates checkpoints
6. service-liaison coordinates handoff
7. Results consolidated and reported

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
station: grill
agent: station-manager-grill
status: in_progress
orders: 3
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

## Comparison with Research System

The meta-multi-agent framework mirrors the `/research` orchestrator pattern:

| Aspect | `/research` | `/multi-agent` |
|--------|-------------|----------------|
| **Purpose** | Conduct research | Generate systems |
| **Input** | Research question | Domain description |
| **Agents** | research/ agents (8) | meta/ agents (6) |
| **Parallel Phase** | web-researcher streams | domain-analyzer + context-architect |
| **Quality Loop** | Critique → iterate (3x) | Validation → regenerate if needed |
| **Output** | Research report | Complete .claude system |
| **Runtime** | 8-15 minutes | 2-5 minutes |

Both follow the same orchestration principles:
- ✅ Full automation (no manual intervention)
- ✅ Phased execution with TodoWrite tracking
- ✅ Parallel execution when safe
- ✅ Quality validation checkpoints
- ✅ Concise final output

## See Also

- **[`commands/multi-agent.md`](../../commands/multi-agent.md)** - The orchestration command (start here)
- **[`commands/README.md`](../../commands/README.md)** - Pattern comparison and usage
- **[`ARCHITECTURE.md`](../../ARCHITECTURE.md)** - Complete system architecture documentation
- **[`agents/research/`](../research/)** - Parallel research system for comparison

---

**Meta-Multi-Agent Framework v1.0**

*Transform any domain into a sophisticated multi-agent system in 2-5 minutes with the `/multi-agent` orchestration command.*

**Quick Links**:
- Run: `/multi-agent [your domain description]`
- Docs: [`commands/multi-agent.md`](../../commands/multi-agent.md)
- Architecture: [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- Comparison: [`commands/README.md`](../../commands/README.md)