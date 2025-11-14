---
name: agno-workflow-builder
description: "Build Agno AI agents and workflows. Use for simple CLI agents (single-agent chat/Q&A) OR complex workflows (multi-step, parallel processing, orchestration). Covers minimal CLI agents (~10 lines) to production workflows with debugging and optimization."
---

# Agno Agent & Workflow Builder

## Overview

Build Agno AI solutions from simple CLI agents to production-ready workflows:
- **Simple CLI Agents**: Interactive chat, single-purpose assistants (~10 lines)
- **Complex Workflows**: Multi-step orchestration, parallel processing, debugging, optimization

Choose the approach that fits your task complexity.

## CRITICAL: Consult Agno Documentation

**BEFORE implementing, ALWAYS consult:**

1. **Context7 MCP** - Get up-to-date Agno documentation:
   ```
   mcp__context7__resolve-library-id "agno"
   mcp__context7__get-library-docs "/agno/agno"
   ```

2. **Agno Source** - Reference actual codebase:
   ```
   Location: /Users/smian/github-smian0/agno-ck/libs/agno/
   Check cookbook/ for examples, agno.workflow for APIs
   ```

**Why:** Agno evolves rapidly. Source has patterns not in this skill. Always verify against current APIs.

## Decision Guide

| Need | Use | Template/Example |
|------|-----|------------------|
| Single agent, no orchestration | Simple CLI Agent | `assets/simple_agent_cli.py` |
| Multi-agent collaboration | Team | `examples/team_workflow_reference.py` |
| Multi-step sequential/parallel | Workflow | `assets/workflow_template.py` |
| MCP + JSON output | Two-model pattern | `examples/agno_mcp_structured.py` |
| Real-world reference | Market analysis | `examples/market_analysis_workflow.py` |

### Use Simple CLI Agent When:
- ✅ Single agent, no orchestration
- ✅ Interactive chat or Q&A
- ✅ No parallel processing
- ✅ **Structure**: ~30-70 lines
- ✅ **Templates**: `assets/simple_agent_cli.py`, `assets/agent_advanced_cli.py`

### Use Complex Workflow When:
- ✅ Multi-step sequential (step1 → step2 → step3)
- ✅ Parallel execution (research 3 topics simultaneously)
- ✅ Conditional branching, loops, routing
- ✅ Custom data transformations
- ✅ **Structure**: 70-250 lines
- ✅ **Templates**: `assets/workflow_template.py`, `assets/simple_workflow.py`
- ✅ **Patterns**: [Workflow Patterns Reference](./references/workflow_patterns.md)

### Use Multi-Agent Team When:
- ✅ Multiple specialists need to **collaborate**
- ✅ Need team leader to coordinate delegation
- ✅ Agents should see each other's work
- ✅ Requires discussion and consensus
- ✅ **Structure**: 40-120 lines
- ✅ **Examples**: `examples/team_workflow_reference.py`, `examples/workflow_with_team_research.py`

## Quick Start

### 1. Simple CLI Agent
```bash
# Copy template and customize
cp assets/simple_agent_cli.py my_agent.py
# Edit: Change model, tools, instructions
# Run: python my_agent.py query "your question"
```

### 2. Complex Workflow
```bash
# Copy workflow template
cp assets/workflow_template.py my_workflow.py
# See: references/workflow_patterns.md for detailed patterns
# Run: python my_workflow.py
```

### 3. Multi-Agent Team
```bash
# Reference verified team pattern
# See: examples/team_workflow_reference.py
```

## Important Configuration

### Disable Telemetry (Required)
```python
import os
os.environ["AGNO_TELEMETRY"] = "false"
```

### Enable Debug Mode (Development)
```python
agent = Agent(debug_mode=True)
workflow = Workflow(debug_mode=True)
```

### Structured Outputs (Recommended for Workflows)
```python
from pydantic import BaseModel, Field

class MyOutput(BaseModel):
    result: str
    count: int

agent = Agent(
    output_schema=MyOutput,  # Enforces Pydantic validation
    instructions="Return MyOutput with result and count fields"
)
```
→ See [Structured Outputs Guide](./references/structured_outputs_guide.md) for complete pattern

### Output Control (Production vs Development)
```python
# Production: Clean output
result = await workflow.arun(input)

# Development: Rich formatted output
await workflow.aprint_response(
    input=input,
    show_step_details=True,  # Show structured outputs
    show_time=True,          # Show execution time
)
```
→ See [Output Control Patterns](./references/output_control_patterns.md) for implementation

## Key Patterns

### MCP Tools Integration

**Basic MCP with tools:**
→ See `examples/agno_mcp.py`

**MCP + Structured Output (Two-Model Pattern):**
→ See `examples/agno_mcp_structured.py`

When you need both MCP tool invocation AND structured JSON output:
- **Main model** (`model=`) - Handles tool invocation (e.g., glm-4.6:cloud)
- **Parser model** (`parser_model=`) - Parses to JSON (e.g., gpt-oss:120b-cloud)

```python
agent = Agent(
    model=Ollama(id="glm-4.6:cloud"),           # Tool calling
    parser_model=Ollama(id="gpt-oss:120b-cloud"), # JSON parsing
    tools=[mcp_tools],
    output_schema=YourPydanticModel,
)
```

**Schema design:** Keep flat (List[str], not List[Model]). See `examples/agno_mcp_structured.py` for complete pattern.

### Teams in Workflows

**When to use:**
- Need specialist collaboration within a workflow step
- Want members to see each other's work
- Require coordinated delegation

→ See `examples/workflow_with_team_research.py` for verified pattern

### Parallel Processing

→ See [Workflow Patterns Reference](./references/workflow_patterns.md) for:
- Parallel steps
- Agent factory pattern
- Result aggregation

### Debugging & Optimization

→ See [Debug Guide](./references/debug_guide.md) for:
- Debug mode usage
- Performance analysis
- Common issues and fixes

## Templates & Assets

| File | Purpose |
|------|---------|
| `assets/simple_agent_cli.py` | Basic CLI agent template |
| `assets/agent_advanced_cli.py` | Advanced CLI with multiple commands |
| `assets/workflow_template.py` | Complete workflow template |
| `assets/simple_workflow.py` | Minimal workflow example |
| `assets/test_workflow_template.py` | Workflow testing template |

## Examples

| File | Demonstrates |
|------|--------------|
| `examples/agno_mcp.py` | Basic MCP integration with Context7 |
| `examples/agno_mcp_structured.py` | MCP + structured output (two models) |
| `examples/team_workflow_reference.py` | Verified team pattern |
| `examples/workflow_with_team_research.py` | Team within workflow |
| `examples/market_analysis_workflow.py` | Real-world: yfinance + Teams |

## Reference Documentation

| File | Content |
|------|---------|
| [Workflow Patterns](./references/workflow_patterns.md) | Parallel processing, factories, caching, optimization |
| [Debug Guide](./references/debug_guide.md) | Troubleshooting, performance analysis, common issues |
| [Structured Outputs Guide](./references/structured_outputs_guide.md) | **NEW** Pydantic models, type-safe workflows, validation best practices |
| [Output Control Patterns](./references/output_control_patterns.md) | **NEW** Production vs development modes, aprint_response(), CLI flags |
| [Model Selection Patterns](./references/model_selection_patterns.md) | **NEW** Data-driven model selection, task-based optimization |

## Common Workflows

### Create Simple Agent
1. Copy `assets/simple_agent_cli.py`
2. Update model, tools, instructions
3. Run: `python agent.py query "test"`

### Create Complex Workflow
1. Consult Context7 MCP for latest patterns
2. Copy `assets/workflow_template.py`
3. Read [Workflow Patterns](./references/workflow_patterns.md)
4. **Design structured outputs** with Pydantic models ([Structured Outputs Guide](./references/structured_outputs_guide.md))
5. **Select optimal models** per agent using `@ollama-model-selector` ([Model Selection Patterns](./references/model_selection_patterns.md))
6. Implement steps (Sequential, Parallel, Condition, Loop, Router)
7. **Add output control** with CLI flags ([Output Control Patterns](./references/output_control_patterns.md))
8. Enable debug mode during development
9. See [Debug Guide](./references/debug_guide.md) for optimization

### Add MCP Tools
1. For basic: See `examples/agno_mcp.py`
2. For structured output: See `examples/agno_mcp_structured.py`
3. Pattern: Main model for tools, parser model for JSON

### Add Teams
1. Standalone: See `examples/team_workflow_reference.py`
2. In workflow: See `examples/workflow_with_team_research.py`
3. Choose delegation mode: sequential (default) or all-at-once

## Recommendations

**Development:**
- Always enable `debug_mode=True` during development
- Use Click command groups for professional CLI
- Start simple, add complexity as needed
- Test with `assets/test_workflow_template.py`

**Production:**
- Disable telemetry: `os.environ["AGNO_TELEMETRY"] = "false"`
- Set `debug_mode=False`
- Use agent/tool result caching for performance
- Monitor performance with debug exports

**Model Selection:**
- **ALWAYS consult**: `@ollama-model-selector` skill for data-driven recommendations
- **Parsing/extraction**: glm-4.6:cloud (192 tok/s, fastest)
- **Validation/reasoning**: deepseek-v3.1:671b-cloud (76 tok/s, hybrid thinking)
- **Tool calling**: glm-4.6:cloud (192 tok/s, excellent tool support)
- **Code generation**: qwen3-coder:480b-cloud (54 tok/s, code-focused)
→ See [Model Selection Patterns](./references/model_selection_patterns.md) for task-based optimization

---

**For detailed implementation patterns, load:**
- [Workflow Patterns Reference](./references/workflow_patterns.md)
- [Debug Guide](./references/debug_guide.md)
