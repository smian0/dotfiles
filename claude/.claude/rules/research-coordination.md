# Research Coordination Rules

Rules for coordinating multiple agents in the deep research pipeline.

## File Access Coordination

### Stream Isolation
- Each discovery agent writes ONLY to its assigned stream directory
- Stream directories are numbered: `stream-1/`, `stream-2/`, etc.
- No agent reads or modifies another stream's files
- Coordinator has read access to all streams

### File Naming Conventions
```
research-output/
├── streams/
│   ├── stream-{N}/
│   │   ├── sources.md         # Discovered sources
│   │   ├── progress.md         # Stream progress
│   │   └── search-history.md   # Search queries log
├── validation/
│   ├── all-sources.md          # Consolidated for validation
│   ├── validated.md            # Validation results
│   └── validation-progress.md  # Validation status
├── analysis/
│   ├── findings.md             # Analysis results
│   └── analysis-progress.md    # Analysis status
└── report/
    ├── final-report.md         # Final synthesis
    ├── executive-summary.md    # Standalone summary
    └── report-progress.md      # Synthesis status
```

### Write Permissions
```yaml
discovery-agents:
  - write: streams/stream-{assigned}/
  - read: none

fact-checker:
  - write: validation/
  - read: streams/*/sources.md

analysis-agent:
  - write: analysis/
  - read: validation/validated.md

report-synthesizer:
  - write: report/
  - read: validation/, analysis/

coordinator:
  - write: research-output/coordinator/
  - read: all
```

## Synchronization Protocol

### Phase Transitions
```markdown
Discovery → Validation
- Trigger: All streams complete OR timeout (15 min)
- Requirement: Minimum 2 successful streams
- Action: Consolidate sources, spawn validator

Validation → Analysis
- Trigger: Validation complete
- Requirement: Minimum 60% sources validated
- Action: Pass validated sources to analyzer

Analysis → Synthesis
- Trigger: Analysis complete
- Requirement: Key findings identified
- Action: Compile all artifacts for synthesizer
```

### Checkpoint Protocol
```markdown
Every 3 minutes:
1. Coordinator checks all progress files
2. Updates coordinator status
3. Detects stuck/failed agents
4. Makes transition decisions
```

## Communication Patterns

### Status Updates
```markdown
# Standard Progress Update Format
[Agent-Type] [Stream-ID] Status Update
- Phase: [Current phase]
- Progress: [X/Y items] or [X%]
- ETA: [Estimated completion]
- Issues: [Any blockers]
```

### Completion Signals
```markdown
# In progress.md files
Status: COMPLETE
Completed: 2024-01-01T10:30:00Z
Results: {summary of results}
HandoffReady: true
```

### Error Signals
```markdown
# In progress.md files
Status: FAILED
Error: {error description}
CanContinue: {true|false}
NeedsIntervention: {true|false}
```

## Parallel Execution Rules

### Resource Allocation
- Maximum 5 parallel discovery streams
- Streams start with 2-second stagger
- CPU/Memory monitored by coordinator
- Automatic throttling if system stressed

### Conflict Prevention
- No shared state between parallel agents
- Each stream has dedicated workspace
- Atomic file writes only
- No file locking required

### Failure Isolation
- Stream failure doesn't affect others
- Failed streams marked but not retried automatically
- Coordinator continues with successful streams
- Minimum success threshold enforced

## Error Handling Hierarchy

### Level 1: Agent-Level (Self-Handle)
- Network timeouts → Retry with backoff
- Rate limiting → Slow down requests
- Parse errors → Skip and continue
- 404 errors → Mark as unavailable

### Level 2: Phase-Level (Coordinator Handle)
- Stream failure → Continue with others
- Insufficient sources → Reduce requirements
- Validation failures → Accept partial results
- Analysis incomplete → Use basic analysis

### Level 3: Pipeline-Level (Human Escalation)
- Total discovery failure → Human intervention
- Systematic misinformation → Stop and alert
- Critical contradictions → Human review
- Infrastructure failure → Abort pipeline

## Quality Gates

### Discovery Phase
- Minimum 5 sources per stream
- At least 2 successful streams
- Diversity score > 0.5
- No single-source dominance

### Validation Phase
- 60% source validation rate
- Credibility average > 60/100
- Cross-reference success > 50%
- Contradiction rate < 30%

### Analysis Phase
- Minimum 3 patterns identified
- At least 5 key insights
- Evidence chains complete
- Confidence scores assigned

### Synthesis Phase
- All sections populated
- Citations complete
- Recommendations included
- Executive summary present

## Coordination State Machine

```markdown
States:
1. INITIALIZING
2. DISCOVERING (parallel)
3. CONSOLIDATING
4. VALIDATING
5. ANALYZING
6. SYNTHESIZING
7. COMPLETE
8. FAILED

Transitions:
- INITIALIZING → DISCOVERING: Setup complete
- DISCOVERING → CONSOLIDATING: Streams done/timeout
- CONSOLIDATING → VALIDATING: Sources merged
- VALIDATING → ANALYZING: Validation done
- ANALYZING → SYNTHESIZING: Analysis done
- SYNTHESIZING → COMPLETE: Report generated
- ANY → FAILED: Critical error
```

## Performance Boundaries

### Time Limits
- Discovery: 15 minutes maximum
- Validation: 20 minutes maximum
- Analysis: 30 minutes maximum
- Synthesis: 30 minutes maximum
- Total pipeline: 90 minutes maximum

### Resource Limits
- Memory per agent: 512MB
- CPU per agent: 1 core
- Network bandwidth: Shared fairly
- File size limits: 10MB per file

## Human Intervention Points

### Automatic Escalation
1. Contradictory evidence > 40%
2. All sources from single viewpoint
3. Critical system failures
4. Ethical concerns detected

### Optional Review Points
1. After discovery (source quality)
2. After validation (credibility check)
3. After analysis (insight review)
4. Before final report (approval)

## Monitoring and Logging

### Progress Tracking
```markdown
research-output/coordinator/status.md
- Overall pipeline status
- Phase completion percentages
- Active agent list
- Performance metrics
- Error summary
```

### Audit Trail
```markdown
research-output/coordinator/audit.log
- Timestamp | Agent | Action | Result
- All phase transitions
- All error occurrences
- All human interventions
- All quality gate decisions
```