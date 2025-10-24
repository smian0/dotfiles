# /research:parallel-discover - Parallel Source Discovery

Command to manage parallel execution of multiple source discovery agents.

## Usage

```bash
/research:parallel-discover <research-question> --streams=<number> --output=<directory>
```

## Purpose

This command specifically handles the parallel execution of discovery agents, ensuring:
- Safe concurrent file writes (no conflicts)
- Progress monitoring across all streams
- Consolidation of results
- Failure handling without blocking other streams

## Parallel Execution Strategy

```markdown
1. Parse research question into N distinct angles
2. Create isolated workspace for each stream
3. Spawn agents simultaneously with:
   - Stream-specific output files
   - Non-overlapping research angles
   - Independent progress tracking
4. Monitor all streams concurrently
5. Consolidate results when all complete
```

## Research Angle Assignment

For a given research question, automatically generates angles:

### Example: "AI Safety Research"
- Stream 1: Technical approaches and algorithms
- Stream 2: Policy and governance frameworks
- Stream 3: Industry implementations and case studies
- Stream 4: Academic research and theory
- Stream 5: Risks and mitigation strategies

## File Isolation Pattern

Each stream writes to isolated files:
```
research-output/
├── stream-1/
│   ├── sources.md
│   ├── progress.md
│   └── notes.md
├── stream-2/
│   ├── sources.md
│   ├── progress.md
│   └── notes.md
└── stream-N/...
```

## Delegation Script

```markdown
# Spawn discovery agents in parallel
@source-discovery-agent --stream=1 --angle="technical" --output="stream-1/"
@source-discovery-agent --stream=2 --angle="policy" --output="stream-2/"
@source-discovery-agent --stream=3 --angle="industry" --output="stream-3/"

# Each agent works independently
# No file conflicts possible due to isolation
# Progress tracked separately
```

## Monitoring Logic

```python
# Pseudo-code for monitoring
streams_status = {
    1: "running",
    2: "running",
    3: "running"
}

while not all_complete(streams_status):
    for stream_id in streams_status:
        check_progress_file(f"stream-{stream_id}/progress.md")
        update_status(stream_id)

    if any_failed(streams_status):
        handle_failure(stream_id)

    sleep(5)  # Check every 5 seconds

consolidate_results()
```

## Failure Handling

- **Single Stream Failure**: Continue with remaining streams
- **Multiple Failures**: Require minimum 2 successful streams
- **All Streams Fail**: Escalate to human, suggest retry
- **Timeout**: 15 minutes per stream max

## Result Consolidation

After all streams complete:
1. Merge sources from all successful streams
2. Remove duplicates (by URL/title)
3. Organize by relevance and credibility
4. Create unified source list
5. Generate discovery summary

## Performance Optimization

- Maximum 5 parallel streams (resource constraints)
- Staggered starts if system load high
- Progressive result writing (not all at end)
- Efficient deduplication algorithm

## Example Execution

```bash
/research:parallel-discover "Renewable energy storage solutions" --streams=4
```

Output:
```
[Stream 1] Researching: Battery technology advances
[Stream 2] Researching: Grid-scale storage systems
[Stream 3] Researching: Policy and economics
[Stream 4] Researching: Alternative storage methods

[Progress] Stream 1: 5 sources found
[Progress] Stream 3: 7 sources found
[Progress] Stream 2: 4 sources found
[Progress] Stream 4: 6 sources found

[Complete] All streams finished
[Consolidating] Total unique sources: 22
[Output] Results saved to research-output/sources/
```
