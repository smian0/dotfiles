---
name: opencode-delegate
description: Delegate tasks to OpenCode for processing in isolated context. Use when you need fresh context, parallel processing, or OpenCode-specific capabilities.
---

# OpenCode Delegation Skill

## Purpose

Delegate tasks to OpenCode while maintaining context separation between Claude Code and OpenCode sessions.

## When to Use

- **Fresh Context Needed**: Task requires clean slate without accumulated conversation history
- **Parallel Processing**: Multiple independent tasks that benefit from isolation
- **OpenCode-Specific Features**: Leverage OpenCode's unique agents, commands, or configurations
- **Testing/Comparison**: Compare outputs from different AI systems

## Usage Pattern

### Step 1: Identify the Task

Determine what needs to be delegated:
- Research tasks requiring web search
- Code generation with specific model preferences
- Multi-agent orchestration tasks
- Analysis requiring different tooling

### Step 2: Choose OpenCode Command

```bash
# List available commands
oc command list

# Common commands:
# - research: Web research tasks
# - multi-agent: Complex multi-agent orchestration
# - analyze: Code analysis tasks
# - Custom commands defined in .opencode/command/
```

### Step 3: Invoke OpenCode

```bash
# Basic invocation
oc run --command <command> "<prompt>"

# With specific agent
oc run --agent <agent-name> "<prompt>"

# To specific directory
cd /path/to/project && oc run --command <command> "<prompt>"
```

### Step 4: Process Results

- Parse the output from Bash tool
- Extract key findings
- Format for Claude Code context
- Handle any errors or incomplete results

## Examples

### Example 1: Research Delegation

**Scenario**: Need comprehensive web research without polluting Claude Code context

```bash
oc run --command research "Compare React Server Components vs. traditional SSR performance characteristics. Include benchmark data and real-world case studies."
```

**Result handling**:
1. Capture full research output
2. Summarize key findings (3-5 bullet points)
3. Preserve source links
4. Return to Claude Code for integration

### Example 2: Multi-Agent Code Generation

**Scenario**: Generate complex system with OpenCode's multi-agent orchestration

```bash
oc run --command multi-agent "Create a microservices architecture for e-commerce with: user service, product catalog, order processing, and payment gateway. Include Docker configs and API documentation."
```

**Result handling**:
1. OpenCode creates files in target directory
2. Review generated structure
3. Report back file list and architecture overview
4. Claude Code can then refine specific files

### Example 3: Parallel Analysis

**Scenario**: Analyze multiple codebases independently

```bash
# Analyze first project
cd ~/projects/project-a && oc run --command analyze "Identify security vulnerabilities" > /tmp/analysis-a.txt

# Analyze second project
cd ~/projects/project-b && oc run --command analyze "Identify security vulnerabilities" > /tmp/analysis-b.txt

# Compare results
cat /tmp/analysis-a.txt /tmp/analysis-b.txt
```

## Best Practices

### ✅ Do

- Use for tasks requiring fresh context
- Delegate independent, parallelizable work
- Leverage OpenCode's specialized commands
- Capture output to files for large results
- Handle errors gracefully with fallbacks

### ❌ Don't

- Delegate tasks requiring accumulated context from Claude Code session
- Use for simple queries better handled directly
- Expect real-time streaming (OpenCode runs batch-style)
- Delegate tasks requiring Claude Code's specific MCP servers

## Output Handling Patterns

### Pattern 1: Direct Output
```bash
result=$(oc run --command research "query")
echo "$result"
```

### Pattern 2: File-Based (for large outputs)
```bash
oc run --command analyze "complex query" > /tmp/oc-result.txt
# Then read file with Read tool
```

### Pattern 3: Structured Parsing
```bash
result=$(oc run --command research "query")
# Extract specific sections
echo "$result" | grep -A 10 "Key Findings"
```

## Troubleshooting

### Issue: Output Truncated
**Solution**: Use file-based output redirection

### Issue: OpenCode Not Found
**Solution**: Verify `oc` is in PATH: `which oc`

### Issue: Command Not Recognized
**Solution**: Check available commands: `oc command list`

### Issue: Context Too Large
**Solution**: Break into smaller sub-tasks, delegate independently

## Integration with Claude Code Workflows

### Workflow 1: Research → Implement
1. Claude Code identifies research need
2. Delegate to OpenCode: `@opencode-delegate research X`
3. OpenCode performs web research in isolation
4. Claude Code receives summary
5. Claude Code implements based on findings

### Workflow 2: Parallel Code Generation
1. Claude Code designs architecture
2. Delegate module generation to OpenCode instances
3. Multiple `oc run` commands for each module
4. Claude Code integrates and refines
5. Final review and testing in Claude Code

### Workflow 3: Comparative Analysis
1. Claude Code defines analysis criteria
2. Delegate analysis to OpenCode for comparison
3. OpenCode uses different models/configurations
4. Claude Code compares outputs
5. Select best approach

## Technical Details

**Process Isolation**: Each `oc run` spawns separate OpenCode process

**Context Sharing**: No automatic context sharing - explicitly pass data via:
- Command-line arguments
- File paths
- Environment variables

**Tool Access**: OpenCode has its own MCP servers and tool configurations

**Model Selection**: OpenCode uses its configured models (may differ from Claude Code)
