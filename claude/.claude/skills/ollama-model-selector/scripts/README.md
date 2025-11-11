# Benchmark Scripts

## benchmark_models.py

Performance testing tool for Ollama cloud models.

### Quick Start

```bash
# Test all models
python3 benchmark_models.py

# Test specific models
python3 benchmark_models.py --models "glm-4.6:cloud" "qwen3-coder:480b-cloud"

# Run multiple times for accuracy
python3 benchmark_models.py --runs 3

# Update performance_data.json
python3 benchmark_models.py --update
```

### Example Output

```
================================================================================
Ollama Cloud Model Benchmark
================================================================================
Test prompt: Write a Python function that calculates the factorial of a...
Models to test: 8
Runs per model: 1
================================================================================

Testing gpt-oss:120b-cloud... ✅ 58.3 tok/s (127 tokens in 2.2s)
Testing glm-4.6:cloud... ✅ 71.2 tok/s (142 tokens in 2.0s)
Testing deepseek-v3.1:671b-cloud... ✅ 49.1 tok/s (98 tokens in 2.0s)
Testing kimi-k2:1t-cloud... ✅ 37.8 tok/s (151 tokens in 4.0s)
Testing kimi-k2-thinking:cloud... ✅ 21.5 tok/s (86 tokens in 4.0s)
Testing qwen3-coder:480b-cloud... ✅ 35.2 tok/s (105 tokens in 3.0s)
Testing minimax-m2:cloud... ✅ 26.1 tok/s (78 tokens in 3.0s)
Testing qwen3-vl:235b-cloud... ✅ 13.7 tok/s (55 tokens in 4.0s)

================================================================================
Benchmark Results
================================================================================
Model                          Current      Measured     Difference
--------------------------------------------------------------------------------
gpt-oss:120b-cloud             60 tok/s     58 tok/s     -2 (-3%)
glm-4.6:cloud                  69 tok/s     71 tok/s     +2 (+3%)
deepseek-v3.1:671b-cloud       50 tok/s     49 tok/s     -1 (-2%)
kimi-k2:1t-cloud               39 tok/s     38 tok/s     -1 (-3%)
kimi-k2-thinking:cloud         22 tok/s     22 tok/s     +0 (+0%)
qwen3-coder:480b-cloud         34 tok/s     35 tok/s     +1 (+3%)
minimax-m2:cloud               25 tok/s     26 tok/s     +1 (+4%)
qwen3-vl:235b-cloud            14 tok/s     14 tok/s     +0 (+0%)
--------------------------------------------------------------------------------

💡 To update performance_data.json, run with --update flag

✅ Benchmark complete!
```

### Requirements

- Python 3.7+
- `requests` library: `pip install requests`
- Ollama running at `localhost:11434`
- Cloud models available

### How It Works

1. **Connection Check**: Verifies Ollama is running
2. **Load Data**: Reads current `performance_data.json`
3. **Test Each Model**: Sends consistent prompt, measures response time
4. **Calculate Speed**: tokens_generated / duration_seconds
5. **Compare**: Shows current vs measured speeds
6. **Update**: Optionally writes new values to `performance_data.json`

### When to Run

- **After Ollama updates**: Cloud model performance may improve
- **Performance feels different**: Verify with actual measurements
- **New models added**: Establish baseline performance
- **Monthly maintenance**: Keep data fresh

### Test Prompt

The benchmark uses a balanced coding prompt:
```
Write a Python function that calculates the factorial of a number using recursion.
Include error handling for negative numbers.
```

This prompt:
- Generates ~100-150 tokens (sufficient sample)
- Tests coding capability (relevant for most use cases)
- Completes in 2-5 seconds per model
- Provides consistent results across runs

### Accuracy Tips

**For more accurate measurements**:
1. Use `--runs 3` for average of 3 tests
2. Close other Ollama sessions (reduce system load)
3. Run during low system activity
4. Test same time of day (cloud performance varies)

**Variation is normal**:
- ±5% typical variation between runs
- ±10% variation due to system load
- Cloud providers may throttle during peak times
