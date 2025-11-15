# Performance Tips

Optimization strategies for large-scale markdown processing.

## Caching Strategy

The skill uses intelligent multi-layer caching:

### Content Cache
- **What**: Raw file contents
- **Invalidation**: File modification time tracking
- **TTL**: Automatic expiration after inactivity

### Result Cache
- **What**: Query results (parameter-aware)
- **Invalidation**: When underlying file changes
- **Hit ratio target**: >50% for repeated operations

### Bulk Cache
- **What**: Large multi-file operation results
- **Invalidation**: Explicit or size-based eviction
- **Best for**: Vault-wide analyses

## Performance by Dataset Size

### Small Vaults (<100 files)

Direct queries work efficiently:

```python
# No special optimization needed
query("note.md", ".h1")
analyze_docs("/small-vault")
```

**Expected**: <50ms per operation

### Medium Vaults (100-500 files)

Use bulk operations with caching:

```python
# Bulk query with automatic caching
bulk_query("/medium-vault", ".h2")

# Or explicit batching
files = list(Path("/vault").rglob("*.md"))
bulk_query(files[:200], ".code")
```

**Expected**: 2-5 seconds for full vault scan

### Large Vaults (500+ files)

Enable optimization and limit scope:

```python
# Clear old cache first
clear_cache("all")

# Limit files processed
bulk_analyze("/large-vault", max_files=500)

# Check cache performance
stats = get_performance_stats()
print(f"Cache hit ratio: {stats['cache_performance']['hit_ratio']}")
```

**Expected**: 5-15 seconds with caching

## Benchmark Results

Performance vs external MQ command-line tool:

| Dataset | Files | Size | Skill | External MQ | Speedup |
|---------|-------|------|-------|-------------|---------|
| Small   | 26    | 1MB  | 15ms  | 222ms       | 14.8x   |
| Medium  | 100   | 5MB  | 45ms  | 2.1s        | 46.7x   |
| Large   | 358   | 15MB | 120ms | 8.4s        | 70.0x   |

*Measured on M-series Mac with header extraction*

## Memory Management

### Automatic Limits
- **Max batch size**: Auto-adjusted based on dataset size
- **Cache eviction**: LRU policy when memory pressure detected
- **Streaming**: Large files processed in chunks

### Manual Control

```python
# Clear specific cache type
clear_cache("content")   # File contents only
clear_cache("results")   # Query results only
clear_cache("bulk")      # Large operation results
clear_cache("all")       # Everything

# Monitor memory usage
stats = get_performance_stats()
memory = stats["memory_info"]
print(f"Current: {memory['current_mb']}MB / {memory['limit_mb']}MB")
```

## Optimization Patterns

### Pattern 1: Repeated Queries on Static Vault

```python
# First run: populates cache
bulk_query("/vault", ".h1")  # ~5s

# Subsequent runs: cache hits
bulk_query("/vault", ".h2")  # ~100ms (cached file contents)
bulk_query("/vault", ".h1")  # ~50ms (cached results)
```

### Pattern 2: Large Vault Initial Scan

```python
# Start fresh
clear_cache("all")

# Process in batches
from pathlib import Path
all_files = list(Path("/vault").rglob("*.md"))

for batch_start in range(0, len(all_files), 100):
    batch = all_files[batch_start:batch_start+100]
    bulk_query(batch, ".h2")
    
    # Monitor performance
    stats = get_performance_stats()
    print(f"Batch {batch_start//100}: {stats['cache_performance']['hit_ratio']*100:.1f}% cache hits")
```

### Pattern 3: Real-time File Monitoring

```python
# For file watchers / live updates
def on_file_change(file_path):
    # Cache automatically invalidates on modification
    result = query(file_path, ".h1")
    return result
```

## Cache Locality

Files are sorted by modification time for better cache locality:
- Recently modified files cached first
- Frequently accessed files stay in cache longer
- Bulk operations process files in mtime order

## Timeout Protection

All regex operations have 5-second timeout:
- Prevents infinite loops on pathological input
- Returns empty results on timeout
- Configurable via `MCP_REGEX_TIMEOUT` environment variable

## When to Clear Cache

**Clear cache when**:
- Starting fresh analysis of large vault
- Memory usage approaching limits
- File timestamps unreliable (network drives)
- Testing performance changes

**Don't clear cache when**:
- Doing iterative queries on stable vault
- Running multiple different selectors
- Analyzing unchanged subset of files

## Performance Monitoring

```python
stats = get_performance_stats()

# Key metrics
print(f"Cache hit ratio: {stats['cache_performance']['hit_ratio']}")
print(f"Total operations: {stats['cache_performance']['total_hits'] + stats['cache_performance']['total_misses']}")
print(f"Memory usage: {stats['memory_info']['current_mb']}MB")

# Optimization targets
assert stats['cache_performance']['hit_ratio'] > 0.5, "Cache underperforming"
```

## Hardware Recommendations

**Optimal**: M-series Mac, 16GB+ RAM
**Minimum**: Any modern CPU, 8GB RAM
**Storage**: SSD recommended for large vaults (1000+ files)

## Best Practices Summary

1. **Use bulk operations** for multiple files
2. **Let caching warm up** - first run is slowest
3. **Limit scope** on initial large vault scans
4. **Monitor cache hit ratios** - target >50%
5. **Clear cache strategically** - not after every operation
6. **Process in batches** for 1000+ file vaults

