# /research:deep-research - Deep Research Orchestrator

Main orchestrator command for comprehensive multi-phase research with parallel execution.

## Usage

```bash
/research:deep-research <research-question> [--streams=<number>] [--depth=<level>] [--output=<directory>]
```

## Parameters

- `research-question`: The main research question or topic to investigate
- `--streams`: Number of parallel research streams (default: 3, max: 5)
- `--depth`: Research depth level (shallow/medium/deep, default: deep)
- `--output`: Output directory for research artifacts (default: ./research-output)

## Workflow Phases

### Phase 1: Discovery (Parallel)
- Spawns N parallel source discovery agents
- Each agent researches different angles/aspects
- Progress tracked in separate stream files

### Phase 2: Validation
- Fact-checker agent validates all discovered sources
- Cross-references claims across sources
- Flags low-confidence or conflicting information

### Phase 3: Analysis
- Deep analysis of validated sources
- Pattern identification across research streams
- Insights and connections synthesis

### Phase 4: Synthesis
- Combines all findings into comprehensive report
- Structures insights by importance and relevance
- Generates executive summary and detailed findings

## Orchestration Logic

```markdown
1. Parse research question and determine research angles
2. Initialize research workspace and progress tracking
3. Spawn parallel discovery agents with:
   - Specific research angle/aspect
   - Stream identifier
   - Output file path
4. Monitor discovery progress
5. Once all streams complete, initiate validation
6. Pass validated sources to analysis
7. Generate final synthesized report
8. Clean up temporary files
```

## Error Handling

- If a discovery stream fails, continue with remaining streams
- Minimum 2 successful streams required to proceed
- Human escalation for critical conflicts
- Automatic retry for transient failures

## Progress Tracking

Creates structured progress files:
```
research-output/
├── progress/
│   ├── stream-1-progress.md
│   ├── stream-2-progress.md
│   ├── stream-3-progress.md
│   └── coordinator-status.md
├── sources/
│   ├── stream-1-sources.md
│   ├── stream-2-sources.md
│   └── validated-sources.md
├── analysis/
│   └── findings.md
└── report/
    └── final-report.md
```

## Example

```bash
/research:deep-research "What are the latest advances in quantum computing error correction?" --streams=4 --depth=deep
```

This will:
1. Launch 4 parallel research streams exploring:
   - Theoretical advances
   - Hardware implementations
   - Software/algorithm developments
   - Industry applications
2. Validate all sources for accuracy
3. Analyze patterns and breakthroughs
4. Generate comprehensive report

## Delegation Instructions

When spawning agents, use these Task tool invocations:

### Discovery Agents (Parallel)
```
@source-discovery-agent Research [specific angle] for stream [N]
Write findings to research-output/sources/stream-[N]-sources.md
Update progress in research-output/progress/stream-[N]-progress.md
```

### Validation Agent
```
@fact-checker-agent Validate all sources in research-output/sources/
Cross-reference claims and check credibility
Output to research-output/sources/validated-sources.md
```

### Analysis Agent
```
@analysis-agent Analyze validated sources from research-output/sources/validated-sources.md
Identify patterns, insights, and connections
Output findings to research-output/analysis/findings.md
```

### Synthesis Agent
```
@report-synthesizer Create comprehensive report from all research artifacts
Include executive summary and detailed findings
Output to research-output/report/final-report.md
```

## Coordination Points

- **Synchronization**: Wait for all discovery streams before validation
- **Checkpoints**: Validate each phase completion before proceeding
- **Conflict Resolution**: Escalate to human for major discrepancies
- **Quality Gates**: Minimum source requirements per stream

## Human Oversight Points

1. Initial research angle approval (optional)
2. Conflict resolution for contradictory sources
3. Final report review before publication
4. Low-confidence findings validation

## Success Metrics

- Minimum 10 quality sources per research question
- Source diversity across streams
- Validation pass rate > 80%
- Clear traceability from sources to conclusions