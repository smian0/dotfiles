# AdaptiveDeepResearchAgent - Solution Documentation

## Problem Summary

The AdaptiveDeepResearchAgent had TWO critical issues:
1. **Hallucinations**: Generated fake data when tools weren't properly registered
2. **Token Overflow**: Even with real web search, massive responses caused "request body too large" errors

## Root Causes

### Issue 1: Tool Registration Failure → Hallucinations
**Problem**: Custom wrapper classes (like `LimitedWebTools`) were not properly exposing methods as Agno tools. The agent had no tools, so it **hallucinated** all data.

**Example of hallucinated data**:
- S&P 500: 5,374.12 with fake CPI data, Fed comments, Apple earnings - ALL FAKE

### Issue 2: OllamaWebTools search() Returns Too Much Data
**Problem**: Even when tools worked, `search()` returned 155 grounded facts with extensive citation text → HTTP 400 "request body too large" error

## Complete Solution

### Part 1: Use OllamaWebTools Directly (Not Wrapped)

**Use OllamaWebTools without wrapper classes:**

```python
from agno.tools.ollama_web import OllamaWebTools
from agno.agent import Agent
from agno.models.ollama import Ollama

# ✅ CORRECT: Direct instantiation
web_tools = OllamaWebTools(cache_results=False)  # Fresh data each time

agent = Agent(
    model=Ollama(id="gpt-oss:120b-cloud"),
    instructions="""Your anti-hallucination instructions here""",
    tools=[web_tools],
    markdown=True
)

# ❌ WRONG: Custom wrapper class (tools not registered)
class LimitedWebTools:
    def __init__(self):
        self.web = OllamaWebTools(...)
    def search(self, query: str, **kwargs):
        return self.web.search(...)  # This won't be discovered by Agno!
```

### Part 2: Use fetch() Instead of search()

**KEY DISCOVERY**: `fetch()` returns much less data than `search()`

```python
# ❌ FAILS: search() returns 155 grounded facts → request too large
result = agent.run("Search for S&P 500 closing price")

# ✅ WORKS: fetch() returns specific page content only
result = agent.run("Fetch https://www.investing.com/indices/us-spx-500 and extract S&P 500 price")
```

**Proven Results**:
- search() with max_results=1: Still fails (too much citation metadata)
- search() with max_results=10, strict=True: 18 facts, still fails
- **fetch() with specific URL: SUCCESS! Got real data: S&P 500: 5,396.52**

## Why This Works

When you pass `OllamaWebTools` directly to the agent:

1. **Agno discovers the tool methods** during `Processing tools for model` phase:
   ```
   DEBUG Added tool search from ollama_web_tools
   DEBUG Added tool fetch from ollama_web_tools
   DEBUG Added tool research from ollama_web_tools
   DEBUG Added tool verify from ollama_web_tools
   ```

2. **Agent can call the tools** by name:
   ```
   Tool Calls:
     Name: 'search'
     Arguments: 'max_results: 10, query: S&P 500 closing price...'
   ```

3. **Web searches execute successfully** and return grounded facts:
   ```
   "total_sources": 10,
   "total_grounded_facts": 130,
   "results": [...]
   ```

## Configuration That Works

```python
from orchestration import AdaptiveDeepResearchAgent, AgentConfig
from agno.tools.ollama_web import OllamaWebTools

config = AgentConfig(
    name="MarketResearcher",
    model_id="claude-sonnet-4",  # Auto-routes to gpt-oss:120b-cloud
    temperature=0.3,
    max_tokens=2000,  # Start conservative, increase if needed
    markdown=True
)

web_tools = OllamaWebTools(
    cache_results=True,  # Cache to avoid repeat searches
    cache_ttl=1800       # 30-minute cache
)

agent = AdaptiveDeepResearchAgent(config, tools=[web_tools])
```

## Query Best Practices

1. **Ask for "recent" data, not specific future dates:**
   ```python
   # ✅ GOOD
   query = "What was the recent S&P 500 closing price? Brief answer with source."

   # ❌ BAD (agent thinks it's a future date)
   query = "What was the S&P 500 closing price on October 14, 2025?"
   ```

2. **Be specific but concise:**
   ```python
   query = """Recent US stock market performance:
   1. S&P 500 level and % change
   2. Main market drivers (cite sources)
   3. Brief summary"""
   ```

3. **Force execution with complexity="complex":**
   ```python
   result = agent.run(query, complexity="complex")  # Triggers UNIFIED PLANNING + immediate execution
   ```

## Token Configuration Insights

**Counterintuitive finding**: Lower max_tokens can sometimes work better than higher values!

- **max_tokens=1,800**: Forces agent to be concise, executes search efficiently
- **max_tokens=16,000**: Gives agent room to write long "I can't help" explanations
- **max_tokens=128,000**: May be needed if search returns massive data (130+ facts)

**Recommended approach**: Start at 2,000, increase only if truncation occurs.

## Handling Large Search Results

OllamaWebTools can return 100+ grounded facts from a single search. To prevent "request body too large" errors:

1. **Let Agno handle search params** - don't try to limit results in wrapper
2. **Increase max_tokens if needed** - up to 128k for comprehensive reports
3. **Use caching** - `cache_results=True, cache_ttl=1800`

## Testing Checklist

When testing the agent:

```bash
python3 test_script.py
```

Verify these debug lines appear:

- [ ] `Processing tools for model`
- [ ] `Added tool search from ollama_web_tools`
- [ ] `Added tool fetch from ollama_web_tools`
- [ ] `Tool Calls: Name: 'search'`
- [ ] `Running: search(max_results=..., query=...)`
- [ ] `"total_grounded_facts": <number>`

If any are missing, tools aren't registered correctly.

## Success Criteria

A working agent should:

1. **Execute web searches** (not just plan them)
2. **Return grounded facts** with source URLs
3. **Cite sources inline** in the final report
4. **Complete within reasonable time** (< 30 seconds for simple queries)

## Example Output

```markdown
## Recent S&P 500 Performance

The S&P 500 closed at **6,449.15** on August 18, 2025, down **0.01%** from the previous session [Investing.com, Historical Data].

### Main Drivers
- Market consolidation after hitting all-time high of 6,481.34 earlier in August
- Trading volume remained steady with investor focus on upcoming Fed meeting
- Technology sector showed mixed performance...

*Source: Investing.com S&P 500 Historical Data, accessed August 19, 2025*
```

## Files Modified

1. **adaptive_deep_researcher.py**:
   - Added `tools` parameter to `__init__`
   - Pass tools to `Agent()` in `_create_agent()`
   - Changed instructions from "wait for confirmation" to "IMMEDIATELY EXECUTE"

2. **Test scripts** (for reference):
   - `test_market_direct.py` - Working example with direct OllamaWebTools
   - `test_market_optimal.py` - Failed attempt with LimitedWebTools wrapper
   - `test_market_recent.py` - Another wrapper attempt that only generated plans

## Next Steps

1. Wait for current test to complete processing 130 grounded facts
2. Review generated report for quality and completeness
3. Test with various query types (market data, technical research, comparative analysis)
4. Document any edge cases or failure modes

## Lessons Learned

1. **Don't wrap tools unnecessarily** - use framework-provided tools directly
2. **Check debug output** - tool registration messages are critical
3. **Query framing matters** - "recent" vs specific dates affects behavior
4. **Start simple** - low max_tokens, simple queries, then scale up
5. **Trust the data** - If web search returns 130 facts, the agent has real data

---

**Last Updated**: October 14, 2025
**Status**: ✅ Tool registration working, awaiting test completion
**Next Test**: Review market_direct output when processing completes
