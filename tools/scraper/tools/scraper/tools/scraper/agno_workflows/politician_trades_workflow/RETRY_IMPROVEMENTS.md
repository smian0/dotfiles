# Retry Logic Improvements

## Problem

Ollama Internal Server Error 500 causing workflow failures:
```
ollama._types.ResponseError: mismatched arg_key and arg_value counts: 1 keys, 2 values (status code: 500)
```

## Solution

Added `run_scraper_with_retry()` function with exponential backoff to both workflows:
- `politician_trades_workflow/workflow.py`
- `stock_research_workflow/workflow.py`

## Retry Configuration

```python
def run_scraper_with_retry(
    command: list,
    max_retries: int = 3,        # Up to 3 attempts
    initial_delay: int = 10,     # Start with 10s delay
    timeout: int = 120           # 2 minutes per attempt
) -> subprocess.CompletedProcess:
```

### Retry Behavior

**On Ollama 500 Error:**
- Attempt 1: Immediate execution
- Attempt 2: 10s delay (if first fails)
- Attempt 3: 20s delay (if second fails)
- Total wait time: up to 30s across retries

**On Timeout:**
- Same exponential backoff (10s → 20s)
- Raises exception after 3 attempts

**On Success:**
- Returns immediately (no unnecessary retries)

## What Gets Retried

### Politician Trades Workflow

1. ✅ `extract_politician_trades()` - Trade extraction from politicians page
2. ✅ `lookup_committee_assignments()` - Committee lookup for each politician
3. ✅ `committee` CLI command - Single politician committee lookup

### Stock Research Workflow

1. ✅ `query_perplexity_analysis()` - Each analytical question (3 questions per stock)

## User Experience

### Before Retry Logic

```bash
./workflow.py committee "Donald S. Beyer Jr."

🔍 Looking up committees for Donald S. Beyer Jr....

❌ Scrape failed: ollama._types.ResponseError: ... (status code: 500)
# IMMEDIATE FAILURE - No JSON file created
```

### After Retry Logic

```bash
./workflow.py committee "Donald S. Beyer Jr."

🔍 Looking up committees for Donald S. Beyer Jr....

⚠️ Ollama crash detected (attempt 1/3), retrying in 10s...
# Waits 10 seconds

⚠️ Ollama crash detected (attempt 2/3), retrying in 20s...
# Waits 20 seconds

✅ Committee assignments retrieved:
# SUCCESS on attempt 3
```

## Code Changes

### `run_scraper_with_retry()` Function

**Location**: Lines 44-101 in both workflow files

**Key Features**:
- Detects Ollama 500 errors in stderr
- Exponential backoff (10s → 20s → fail)
- Preserves original result even on final failure
- Clear console feedback for each retry attempt

### Updated Function Calls

**Politician Trades Workflow:**

```python
# extract_politician_trades() - Line 127
result = run_scraper_with_retry(
    command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
    max_retries=3,
    initial_delay=10,
    timeout=120,
)

# lookup_committee_assignments() - Line 200
result = run_scraper_with_retry(
    command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
    max_retries=3,
    initial_delay=10,
    timeout=120,
)

# committee CLI command - Line 364
result = run_scraper_with_retry(
    command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
    max_retries=3,
    initial_delay=10,
    timeout=120,
)
```

**Stock Research Workflow:**

```python
# query_perplexity_analysis() - Line 187
result = run_scraper_with_retry(
    command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
    max_retries=3,
    initial_delay=10,
    timeout=120,
)
```

## Testing

### Test Command

```bash
cd /Users/smian/dotfiles/tools/scraper/tools/scraper/tools/scraper/agno_workflows/politician_trades_workflow
./workflow.py committee "Donald S. Beyer Jr." --output /tmp/beyer_retry_test.json
```

### Expected Outcomes

**Scenario 1: Ollama Stable**
- Success on first attempt
- No retries needed
- JSON file created immediately

**Scenario 2: Transient Ollama Crash**
- First attempt fails with 500 error
- Retry after 10s succeeds
- JSON file created
- User sees retry feedback

**Scenario 3: Persistent Ollama Crash**
- All 3 attempts fail
- Total wait: 30s (10s + 20s)
- Clear error message
- Workflow exits gracefully

## Limitations

**Does NOT fix:**
- Persistent Ollama backend failures (needs Ollama restart)
- Network connectivity issues
- Browser/Comet crashes

**DOES help with:**
- Transient Ollama 500 errors
- Temporary backend overload
- Race conditions in async tool handling

## Performance Impact

**Best case** (no errors): No overhead
**Average case** (1 retry): +10s per scraper call
**Worst case** (3 retries): +30s per scraper call

**Trade-off**: Slightly slower on retries, but much higher success rate

## Monitoring

Watch for these console messages:

```
⚠️ Ollama crash detected (attempt 1/3), retrying in 10s...
⚠️ Ollama crash detected (attempt 2/3), retrying in 20s...
❌ Ollama crash persists after 3 attempts
⚠️ Timeout (attempt 1/3), retrying in 10s...
```

## Future Improvements

Potential enhancements:

1. **Configurable retry params** - CLI flags for `--max-retries` and `--initial-delay`
2. **Jitter** - Add randomness to delays to prevent thundering herd
3. **Circuit breaker** - Skip retries if Ollama is down for extended period
4. **Retry metrics** - Log success rate and retry count to file
5. **Ollama health check** - Ping Ollama endpoint before retrying

---

**Created**: 2025-11-11
**Applied to**: politician_trades_workflow, stock_research_workflow
**Status**: ✅ Implemented and ready for testing
