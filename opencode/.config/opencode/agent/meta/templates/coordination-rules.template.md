# {{DOMAIN}} Agent Coordination Rules

Rules for multiple agents working in parallel within {{EXECUTION_CONTEXT}} for {{DOMAIN}} operations.

## Parallel Execution Principles

1. **{{PARALLELISM_TYPE}}** - {{PARALLELISM_DESCRIPTION}}
2. **Explicit coordination** - When {{SHARED_RESOURCES}} needed, coordinate explicitly
3. **Fail fast** - Surface conflicts immediately, don't try to be clever
4. **Human resolution** - {{CONFLICT_RESOLUTION}} are resolved by humans, not agents
5. **{{DOMAIN_PRINCIPLE}}** - {{DOMAIN_PRINCIPLE_DESCRIPTION}}

## Work Stream Assignment

Each agent is assigned a work stream from the {{ANALYSIS_SOURCE}}:

```yaml
# From {{ANALYSIS_FILE}}
{{#each WORK_STREAMS}}
Stream {{this.id}}: {{this.name}}
  Files: {{this.file_patterns}}
  Agent: {{this.agent_type}}
  Dependencies: {{this.dependencies}}
  Conflicts: {{this.conflicts}}
{{/each}}
```

Agents should only modify files in their assigned patterns.

## File Access Coordination

### {{DOMAIN}} File Categories
{{#each FILE_CATEGORIES}}
#### {{this.category}}
- **Pattern**: `{{this.pattern}}`
- **Access Type**: {{this.access_type}}
- **Coordination Required**: {{this.coordination_required}}
- **Conflict Risk**: {{this.conflict_risk}}
{{/each}}

### Check Before Modify
Before modifying any file:
```bash
# Check if file is being modified
git status {{FILE_PATTERN}}

# If modified by another agent, coordinate
if [[ $(git status --porcelain {{FILE_PATTERN}}) ]]; then
  echo "⏳ Waiting for {{FILE_PATTERN}} to be available..."
  {{WAIT_STRATEGY}}
fi
```

### Atomic Operations
Make commits atomic and focused:
```bash
# Good - Single purpose commit for {{DOMAIN}}
git add {{EXAMPLE_FILES}}
git commit -m "{{COMMIT_MESSAGE_FORMAT}}"

# Bad - Mixed concerns
git add {{MIXED_CONCERNS_EXAMPLE}}
git commit -m "{{BAD_COMMIT_EXAMPLE}}"
```

## Communication Between Agents

### Through {{EXECUTION_CONTEXT}}
Agents see each other's work through {{COMMUNICATION_METHOD}}:
```bash
# Agent checks what others have done
{{STATUS_CHECK_COMMAND}}

# Agent syncs latest changes
{{SYNC_COMMAND}}
```

### Through Progress Files
Each stream maintains progress in: `{{PROGRESS_FILE_PATTERN}}`
```markdown
# {{PROGRESS_FILE_EXAMPLE}}
---
---

## Completed
{{COMPLETED_EXAMPLE}}

## Working On
{{WORKING_ON_EXAMPLE}}

## Blocked
{{BLOCKED_EXAMPLE}}

## {{DOMAIN}} Specific Status
{{DOMAIN_STATUS_EXAMPLE}}
```

### Through Analysis Files
The {{ANALYSIS_FILE}} is the contract:
```yaml
# Agents read this to understand boundaries
{{#each STREAM_BOUNDARIES}}
Stream {{this.id}}:
  Files: {{this.files}}     # Agent {{this.id}} only touches these
  {{DOMAIN_CONSTRAINT}}: {{this.constraint}}
{{/each}}
```

## {{DOMAIN}} Specific Coordination

### {{DOMAIN}} Resources
{{#each DOMAIN_RESOURCES}}
#### {{this.resource}}
- **Type**: {{this.type}}
- **Access Pattern**: {{this.access_pattern}}
- **Coordination Method**: {{this.coordination}}
- **Conflict Resolution**: {{this.resolution}}
{{/each}}

### {{DOMAIN}} Dependencies
{{#each DOMAIN_DEPENDENCIES}}
#### {{this.dependency}}
- **Type**: {{this.type}}
- **Trigger**: {{this.trigger}}
- **Coordination**: {{this.coordination}}
- **Timeout**: {{this.timeout}}
{{/each}}

## Handling Conflicts

### Conflict Detection
```bash
# If {{CONFLICT_SCENARIO}} fails due to conflict
{{CONFLICT_DETECTION_COMMAND}}
# Error: conflicts exist

# Agent should report and wait
echo "❌ Conflict detected in {{CONFLICT_EXAMPLE}}"
echo "{{CONFLICT_RESOLUTION_MESSAGE}}"
```

### {{DOMAIN}} Conflict Types
{{#each CONFLICT_TYPES}}
#### {{this.type}}
- **Scenario**: {{this.scenario}}
- **Detection**: {{this.detection}}
- **Resolution**: {{this.resolution}}
- **Prevention**: {{this.prevention}}
{{/each}}

### Conflict Resolution
Always defer to humans:
1. Agent detects conflict
2. Agent reports issue with {{CONTEXT_REQUIREMENTS}}
3. Agent pauses work on {{PAUSE_SCOPE}}
4. Human resolves using {{RESOLUTION_TOOLS}}
5. Agent continues from {{RESUME_POINT}}

Never attempt automatic merge resolution for {{CRITICAL_RESOURCES}}.

## Synchronization Points

### Natural Sync Points
{{#each SYNC_POINTS}}
- {{this.point}} - {{this.description}}
{{/each}}

### Explicit Sync
```bash
# Pull latest changes
{{EXPLICIT_SYNC_COMMAND}}

# If conflicts, stop and report
if [[ $? -ne 0 ]]; then
  echo "❌ Sync failed - {{SYNC_FAILURE_MESSAGE}}"
  exit 1
fi
```

### {{DOMAIN}} Checkpoints
{{#each DOMAIN_CHECKPOINTS}}
#### {{this.checkpoint}}
- **Frequency**: {{this.frequency}}
- **Validation**: {{this.validation}}
- **Actions**: {{this.actions}}
{{/each}}

## Agent Communication Protocol

### Status Updates
Agents should update their status regularly:
```bash
# Update progress file every {{UPDATE_FREQUENCY}}
echo "✅ Completed: {{STATUS_UPDATE_FORMAT}}" >> {{PROGRESS_FILE}}
git add {{PROGRESS_FILE}}
git commit -m "{{PROGRESS_COMMIT_FORMAT}}"
```

### Coordination Requests
When agents need to coordinate:
```markdown
# In {{COORDINATION_FILE}}
## Coordination Needed
- {{COORDINATION_REQUEST_FORMAT}}
- {{TIMING_INFORMATION}}
- {{IMPACT_ASSESSMENT}}
```

### {{DOMAIN}} Notifications
{{#each NOTIFICATION_TYPES}}
#### {{this.type}}
- **Trigger**: {{this.trigger}}
- **Format**: {{this.format}}
- **Recipients**: {{this.recipients}}
- **Urgency**: {{this.urgency}}
{{/each}}

## Parallel Execution Strategy

### No Conflicts Possible
When working on {{INDEPENDENT_RESOURCES}}:
```bash
# These can happen simultaneously
{{PARALLEL_EXAMPLE_1}}
{{PARALLEL_EXAMPLE_2}}
{{PARALLEL_EXAMPLE_3}}
```

### Sequential When Needed
When touching {{SHARED_RESOURCES}}:
```bash
# Agent A executes first
{{SEQUENTIAL_EXAMPLE_1}}

# Agent B waits, then proceeds
# (After A's completion)
{{SEQUENTIAL_EXAMPLE_2}}
```

### {{DOMAIN}} Execution Patterns
{{#each EXECUTION_PATTERNS}}
#### Pattern: {{this.name}}
- **When**: {{this.when}}
- **Approach**: {{this.approach}}
- **Coordination**: {{this.coordination}}
- **Example**: {{this.example}}
{{/each}}

## Best Practices

### General Practices
1. **Commit early and often** - Smaller commits = fewer conflicts
2. **Stay in your lane** - Only modify assigned files
3. **Communicate changes** - Update progress files
4. **Sync frequently** - Stay synchronized with other agents
5. **Fail loudly** - Report issues immediately
6. **Never force** - No `--force` flags ever

### {{DOMAIN}} Specific Practices
{{#each DOMAIN_PRACTICES}}
#### {{this.category}}
{{#each this.practices}}
- **{{this.practice}}**: {{this.description}}
{{/each}}
{{/each}}

## Common Patterns

### Starting Work
```bash
1. {{STARTUP_STEP_1}}
2. {{STARTUP_STEP_2}}
3. {{STARTUP_STEP_3}}
4. {{STARTUP_STEP_4}}
5. {{STARTUP_STEP_5}}
```

### During Work
```bash
1. {{WORK_STEP_1}}
2. {{WORK_STEP_2}}
3. {{WORK_STEP_3}}
4. {{WORK_STEP_4}}
5. {{WORK_STEP_5}}
```

### Completing Work
```bash
1. {{COMPLETION_STEP_1}}
2. {{COMPLETION_STEP_2}}
3. {{COMPLETION_STEP_3}}
4. {{COMPLETION_STEP_4}}
```

## Error Recovery

### Recovery Procedures
{{#each RECOVERY_PROCEDURES}}
#### {{this.scenario}}
```bash
{{#each this.steps}}
# {{@index}}. {{this}}
{{/each}}
```
{{/each}}

### {{DOMAIN}} Specific Recovery
{{#each DOMAIN_RECOVERY}}
#### {{this.error_type}}
- **Detection**: {{this.detection}}
- **Assessment**: {{this.assessment}}
- **Recovery**: {{this.recovery}}
- **Prevention**: {{this.prevention}}
{{/each}}

## Monitoring and Debugging

### Progress Monitoring
Track coordination through:
{{#each MONITORING_METHODS}}
- **{{this.method}}**: {{this.description}}
{{/each}}

### Debug Information
When reporting coordination issues, include:
{{#each DEBUG_INFO}}
- **{{this.info}}**: {{this.description}}
{{/each}}

### Performance Metrics
{{#each PERFORMANCE_METRICS}}
#### {{this.metric}}
- **Measurement**: {{this.measurement}}
- **Target**: {{this.target}}
- **Alert Threshold**: {{this.alert_threshold}}
{{/each}}

## Troubleshooting Guide

### Common Coordination Issues
{{#each TROUBLESHOOTING_ISSUES}}
#### {{this.issue}}
- **Symptoms**: {{this.symptoms}}
- **Likely Causes**: {{this.causes}}
- **Resolution Steps**: {{this.resolution}}
- **Prevention**: {{this.prevention}}
{{/each}}

---
---

*Generated by meta-multi-agent framework*
*Template version: {{TEMPLATE_VERSION}}*
*Domain: {{DOMAIN}} | Coordination type: {{COORDINATION_TYPE}}*
