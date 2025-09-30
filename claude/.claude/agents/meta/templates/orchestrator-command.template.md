---
allowed-tools: Read, Write, Bash, Task, SlashCommand, TodoWrite
argument-hint: <{{DOMAIN}}_name> [options]
---

# {{OPERATION_TITLE}}

{{OPERATION_DESCRIPTION}}

## Usage
```
/{{DOMAIN}}:{{COMMAND_NAME}} <required_args> [optional_args]
```

## Required Rules

**IMPORTANT:** Before executing this command, read and follow:
- `.claude/rules/{{DOMAIN}}-coordination.md` - Domain coordination rules
- `.claude/rules/file-access-rules.md` - File conflict prevention
{{#if ADDITIONAL_RULES}}
{{#each ADDITIONAL_RULES}}
- `{{this}}` - {{@key}}
{{/each}}
{{/if}}

## Preflight Checklist

Before proceeding, complete these validation steps:

1. **Verify prerequisites:**
{{#each PREREQUISITES}}
   - {{this}}
{{/each}}

2. **Check system state:**
{{#each STATE_CHECKS}}
   - {{this}}
{{/each}}

3. **Validate inputs:**
{{#each INPUT_VALIDATIONS}}
   - {{this}}
{{/each}}

## Instructions

You are orchestrating: **{{WORKFLOW_NAME}}**

### 1. Preparation Phase
{{#each PREPARATION_STEPS}}
- {{this}}
{{/each}}

### 2. Analysis Phase
{{#if NEEDS_ANALYSIS}}
Determine execution strategy:
- **Sequential execution**: If dependencies are complex
- **Parallel execution**: If work streams are independent
- **Hybrid execution**: If mixed dependencies exist

{{#if USE_DOMAIN_ANALYZER}}
For complex domains, use domain analysis:
```yaml
Task:
  description: "Analyze {{DOMAIN}} requirements"
  subagent_type: "domain-analyzer"
  prompt: |
    Analyze the {{DOMAIN}} domain for multi-agent execution:

    Requirements: {{REQUIREMENTS}}

    Provide:
    - Core workflows and processes
    - Parallelization opportunities
    - Coordination requirements
    - Recommended agent architecture
```
{{/if}}
{{/if}}

### 3. Execution Phase
{{#if PARALLEL_EXECUTION}}
#### Parallel Execution Strategy
Spawn parallel worker for multi-stream execution:

```yaml
Task:
  description: "Execute {{WORKFLOW_NAME}} in parallel"
  subagent_type: "{{DOMAIN}}-parallel-worker"
  prompt: |
    Execute parallel work streams for: {{WORKFLOW_NAME}}

    Work Analysis: {{ANALYSIS_FILE}}
    Execution Context: {{EXECUTION_CONTEXT}}

    Instructions:
    1. Read work stream definitions
    2. Spawn appropriate sub-agents for each stream
    3. Coordinate execution based on dependencies
    4. Monitor progress and handle failures
    5. Consolidate results from all streams

    Return consolidated status and results.
```
{{else}}
#### Sequential Execution
Execute workflow steps in order:

{{#each EXECUTION_STEPS}}
##### Step {{@index}}: {{this.name}}
{{this.description}}

{{#if this.uses_agent}}
```yaml
Task:
  description: "{{this.task_description}}"
  subagent_type: "{{this.agent_type}}"
  prompt: |
    {{this.agent_prompt}}
```
{{else}}
```bash
{{this.bash_commands}}
```
{{/if}}
{{/each}}
{{/if}}

### 4. Validation Phase
Verify execution results:
{{#each VALIDATION_STEPS}}
- {{this}}
{{/each}}

### 5. Consolidation Phase
{{#each CONSOLIDATION_STEPS}}
- {{this}}
{{/each}}

## Error Handling

### Common Failure Scenarios
{{#each ERROR_SCENARIOS}}
#### Error: {{this.name}}
- **Symptoms**: {{this.symptoms}}
- **Cause**: {{this.cause}}
- **Resolution**: {{this.resolution}}
{{/each}}

### Recovery Procedures
{{#each RECOVERY_PROCEDURES}}
#### {{this.name}}
{{this.steps}}
{{/each}}

### Escalation
If critical errors occur:
1. **Stop execution** - Halt all running agents
2. **Preserve state** - Save current progress
3. **Report status** - Provide clear error description
4. **Request intervention** - Ask for human assistance

## Output Format

### Success Output
```
🚀 {{OPERATION_TITLE}} Complete: $ARGUMENTS

{{#each SUCCESS_SECTIONS}}
{{this.title}} ✓
{{#each this.items}}
  - {{this}}
{{/each}}

{{/each}}
{{#if NEXT_STEPS}}
Next Steps:
{{#each NEXT_STEPS}}
  {{this}}
{{/each}}
{{/if}}
```

### Progress Updates
During execution, provide regular status updates:
```
⏳ {{OPERATION_TITLE}} Progress: {{STAGE_NAME}}
- Current: {{CURRENT_ACTIVITY}}
- Completed: {{COMPLETED_COUNT}}/{{TOTAL_COUNT}}
- ETA: {{ESTIMATED_COMPLETION}}
```

### Error Output
```
❌ {{OPERATION_TITLE}} Failed: {{ERROR_TYPE}}

Issue: {{ERROR_DESCRIPTION}}
Stage: {{FAILURE_STAGE}}
Impact: {{IMPACT_ASSESSMENT}}

Recovery Options:
1. {{RECOVERY_OPTION_1}}
2. {{RECOVERY_OPTION_2}}

Human intervention needed: {{INTERVENTION_REQUIRED}}
```

## Integration Points

### Command Composition
This command can be used with:
{{#each RELATED_COMMANDS}}
- `/{{DOMAIN}}:{{this.command}}` - {{this.description}}
{{/each}}

### Agent Coordination
This command coordinates these agent types:
{{#each AGENT_TYPES}}
- **{{this.name}}** - {{this.purpose}}
{{/each}}

### External Dependencies
{{#each EXTERNAL_DEPENDENCIES}}
- **{{this.name}}** - {{this.description}} - {{this.type}}
{{/each}}

## Advanced Options

{{#if PARALLEL_OPTIONS}}
### Parallel Execution Options
- `--max-parallel={{MAX_PARALLEL}}` - Maximum concurrent agents
- `--coordination-mode={{COORDINATION_MODE}}` - How agents coordinate
- `--conflict-resolution={{CONFLICT_RESOLUTION}}` - Conflict handling strategy
{{/if}}

{{#if VALIDATION_OPTIONS}}
### Validation Options
- `--skip-validation` - Skip preflight validation (use with caution)
- `--validation-level={{VALIDATION_LEVEL}}` - Thoroughness of validation
- `--dry-run` - Simulate execution without making changes
{{/if}}

{{#if MONITORING_OPTIONS}}
### Monitoring Options
- `--verbose` - Detailed progress reporting
- `--log-level={{LOG_LEVEL}}` - Logging detail level
- `--status-file={{STATUS_FILE}}` - File for status updates
{{/if}}

## Notes

{{#each NOTES}}
- {{this}}
{{/each}}

---

*Generated by meta-multi-agent framework*
*Template version: {{TEMPLATE_VERSION}}*
*Domain: {{DOMAIN}} | Operation: {{OPERATION_NAME}}*