# Parallel Worker Template

Template for agents that execute tasks in parallel without conflicts.

## Worker Configuration

```yaml
worker_id: {stream_number}
worker_type: {discovery|validation|analysis}
isolation_mode: strict
workspace: ./stream-{N}/
max_runtime: 15_minutes
retry_policy: exponential_backoff
```

## Initialization Checklist

```markdown
- [ ] Receive unique worker ID
- [ ] Create isolated workspace directory
- [ ] Verify no file conflicts possible
- [ ] Initialize progress tracking file
- [ ] Set up error handling
- [ ] Configure timeouts
- [ ] Start heartbeat reporting
```

## File Isolation Protocol

### Workspace Structure
```markdown
stream-{N}/
├── input/
│   └── config.yaml         # Worker configuration
├── working/
│   ├── temp_*.md          # Temporary files
│   └── cache/             # Local cache
├── output/
│   ├── results.md         # Main output
│   ├── progress.md        # Progress tracking
│   └── metadata.json      # Result metadata
└── logs/
    └── worker.log         # Worker-specific log
```

### Safe File Operations
```python
# Always use worker-specific paths
def get_output_path(worker_id, filename):
    return f"./stream-{worker_id}/output/{filename}"

# Atomic writes to prevent corruption
def write_atomic(filepath, content):
    temp_file = f"{filepath}.tmp"
    write_file(temp_file, content)
    rename_file(temp_file, filepath)

# Never read other workers' files
def is_allowed_path(worker_id, filepath):
    return f"stream-{worker_id}" in filepath
```

## Progress Reporting

### Heartbeat Pattern
```markdown
Every 30 seconds:
1. Update progress.md with current status
2. Report metrics (items processed, etc.)
3. Update estimated completion time
4. Check for termination signal
```

### Progress Update Format
```markdown
[{timestamp}] Worker {ID} Heartbeat
Status: {Active|Paused|Completing}
Progress: {current}/{total} or {percentage}%
Rate: {items}/minute
ETA: {minutes} remaining
Health: {Green|Yellow|Red}
```

## Parallel Coordination

### Non-Blocking Operations
```python
# Good: Independent operation
async def process_stream(stream_id):
    sources = await discover_sources(stream_id)
    write_to_stream_dir(stream_id, sources)
    return stream_id, len(sources)

# Bad: Shared resource access
async def bad_process_stream(stream_id):
    global shared_sources  # Never do this!
    sources = await discover_sources(stream_id)
    shared_sources.extend(sources)  # Race condition!
```

### Synchronization Points
```markdown
Workers DON'T synchronize during execution.
Synchronization happens ONLY at phase boundaries:

1. All workers complete independently
2. Coordinator waits for all/timeout
3. Coordinator consolidates results
4. Next phase begins
```

## Error Handling

### Failure Isolation
```python
try:
    # Worker-specific operation
    result = process_data(worker_id, data)
except Exception as e:
    # Log to worker-specific log
    log_error(f"stream-{worker_id}/logs/worker.log", e)

    # Update worker status
    update_status(worker_id, "FAILED", str(e))

    # Don't affect other workers!
    exit_gracefully(worker_id)
```

### Recovery Strategies
```markdown
Transient Failures (network, timeout):
- Retry with exponential backoff
- Maximum 3 retries
- Log each attempt

Resource Failures (memory, disk):
- Reduce batch size
- Clear local cache
- Graceful degradation

Logic Failures (parsing, validation):
- Skip problematic item
- Log for debugging
- Continue with rest
```

## Performance Optimization

### Resource Management
```python
# Memory limits per worker
MAX_MEMORY_MB = 512

# Check before large operations
def check_memory():
    if get_memory_usage() > MAX_MEMORY_MB * 0.8:
        cleanup_cache()
        gc.collect()

# CPU throttling
def throttle_if_needed():
    if get_cpu_usage() > 80:
        time.sleep(0.1)
```

### Batch Processing
```markdown
Process in batches to:
- Enable progress reporting
- Allow graceful interruption
- Prevent memory bloat
- Maintain responsiveness

Batch size: 10 items
Report after each batch
Check signals between batches
```

## Communication Protocol

### Status Messages
```python
class WorkerStatus:
    INITIALIZING = "Initializing"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETING = "Completing"
    COMPLETE = "Complete"
    FAILED = "Failed"
    TIMEOUT = "Timeout"
```

### Result Reporting
```markdown
## Worker {N} Results

### Summary
- Items Processed: {count}
- Success Rate: {percentage}%
- Duration: {minutes}
- Quality Score: {score}

### Outputs
- Primary: ./stream-{N}/output/results.md
- Metadata: ./stream-{N}/output/metadata.json
- Logs: ./stream-{N}/logs/worker.log

### Handoff Ready
- Status: COMPLETE
- Validation: Passed
- Next Phase: Ready
```

## Timeout Handling

### Soft Timeout (Warning)
```markdown
At 80% of max runtime:
1. Log warning
2. Start wrapping up
3. Prioritize critical tasks
4. Prepare partial results
```

### Hard Timeout (Termination)
```markdown
At 100% of max runtime:
1. Stop accepting new work
2. Finish current item only
3. Write partial results
4. Mark as TIMEOUT
5. Exit gracefully
```

## Quality Assurance

### Self-Validation
```python
def validate_output(worker_id):
    checks = {
        "output_exists": check_file_exists(output_path),
        "valid_format": validate_markdown(output_path),
        "minimum_content": len(content) > min_size,
        "progress_complete": status == "COMPLETE",
        "no_corruption": verify_checksum(output_path)
    }
    return all(checks.values())
```

### Metrics Collection
```markdown
Track and report:
- Processing rate (items/minute)
- Error rate (errors/total)
- Quality score (0-100)
- Resource usage (CPU/memory)
- Network requests (count/minute)
```

## Template Usage

### For Discovery Workers
```python
class DiscoveryWorker(ParallelWorker):
    def __init__(self, stream_id, research_angle):
        super().__init__(stream_id)
        self.angle = research_angle

    def execute(self):
        sources = self.discover_sources()
        self.write_results(sources)
        return len(sources)
```

### For Validation Workers
```python
class ValidationWorker(ParallelWorker):
    def __init__(self, worker_id, source_batch):
        super().__init__(worker_id)
        self.sources = source_batch

    def execute(self):
        validated = self.validate_sources()
        self.write_results(validated)
        return validation_stats
```

## Best Practices

### DO
- Use unique worker IDs everywhere
- Write to isolated directories only
- Report progress regularly
- Handle errors gracefully
- Clean up on exit
- Use atomic file operations

### DON'T
- Access shared global state
- Read other workers' files
- Use file locking
- Wait for other workers
- Throw unhandled exceptions
- Leave temporary files