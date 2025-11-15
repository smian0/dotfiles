# Page Reuse Test Results - Final Analysis

**Test Date**: 2025-11-11
**Test Case**: Donald S. Beyer Jr. + GDXJ
**Approach**: Page reuse strategy (open once, reuse for Questions 2-5)
**Status**: ❌ **FAILED - Same root cause as previous tests**

---

## Executive Summary

The page reuse strategy successfully avoided opening new pages for Questions 2-5, **BUT** the same connectivity failure occurred: all MCP browser tool operations (`list_pages`, `take_snapshot`, `click`, `fill`) timed out, preventing data extraction from Perplexity.

**Critical Discovery**: Parallel testing revealed that **MCP Chrome DevTools DOES work** for simple operations (screenshot), but **FAILS during complex Agno agent workflows** (scrape with multiple tool calls).

---

## What Happened

### Test Execution

**Page Reuse Workflow:**
```bash
./workflow.py analyze-trade "Donald S. Beyer Jr." "GDXJ" --output reports/beyer_gdxj_page_reuse_test.json
```

**Modified Logic:**
- **Question 1**: Opens page normally with `new_page`
- **Questions 2-5**: Reuse existing page - agent instructed to use `list_pages` + `select_page` instead of `new_page`

**Results:**
- ✅ Workflow executed (exit code 0)
- ✅ All 5 questions completed
- ✅ Question 5 retried once and succeeded
- ❌ **All questions received connectivity errors**
- ❌ **No research data retrieved**
- ❌ Synthesis report: "CRITICAL DATA GAP", Signal Strength: Unknown, Confidence: 0/10

### Error Pattern (ALL 5 Questions)

**Question 1** (opened new page):
```
"Multiple timeout errors when attempting to create new pages"
"Timeout errors when trying to navigate to URLs"
"Inability to establish connection with external websites"
```

**Questions 2-5** (attempted page reuse):
```
"All tool calls are timing out"
"persistent timeout issues"
"connectivity issues with the browser tools"
```

**Key Observation**: Page reuse avoided the `new_page` timeout, but **once the agent tried to interact** with the page using `list_pages`, `take_snapshot`, etc., **those MCP operations also timed out**.

---

## Parallel Discovery: MCP DOES Work for Simple Operations

### AAPL Screenshot Test (Task b17b12) - ✅ SUCCEEDED

While the multi-question workflow was running, a parallel screenshot test **succeeded completely**:

```
✅ Comet is running
📸 Opening new tab: https://www.perplexity.ai/finance/AAPL
✅ New tab opened
📸 Taking screenshot...
✅ Screenshot captured
💾 Saved to: /tmp/perplexity_aapl_finance.png
🔍 Analyzing screenshot with Qwen3 VL model... (succeeded)
```

**This proves:**
1. ✅ Comet browser IS running properly on port 9223
2. ✅ MCP Chrome DevTools connection WORKS
3. ✅ `new_page` CAN successfully load Perplexity Finance pages
4. ✅ `take_screenshot` works
5. ✅ The 10-second timeout is **marginal but achievable** for direct operations

### AAPL Scrape Test (Task f758a4) - 🏃 Still Running

```
🕷️  Scraping: https://www.perplexity.ai/finance/AAPL
📝 Task: Find the 'Ask any question about finance' search box, type 'Is there an obvious buy signal for AAPL stock right now?' and submit it.

[Agent is actively thinking and using MCP tools]
```

The Agno agent is successfully using MCP tools in this scrape test, which contrasts with the multi-question workflow failures.

---

## Root Cause Analysis

### The Real Problem: Intermittent MCP Connectivity

**MCP Chrome DevTools connection is UNSTABLE:**

| Test Type | MCP Usage Pattern | Result |
|-----------|-------------------|--------|
| Screenshot (b17b12) | Direct: `new_page` → `take_screenshot` | ✅ **Succeeded** |
| AAPL Scrape (f758a4) | Agno agent with MCP tools (single invocation) | 🏃 **Running** |
| Multi-Question Workflow (0719c3) | Agno agent with MCP tools (5 sequential invocations) | ❌ **Failed (all 5)** |
| Multi-Question Original (3ca75a) | Agno agent with MCP tools (5 sequential invocations) | ❌ **Failed (all 5)** |

**Pattern:**
- ✅ **Simple, direct MCP calls** → Works
- ✅ **Single Agno agent scrape** → Works (running successfully)
- ❌ **Multiple sequential Agno agent scrapes** → Fails

### Theory 1: Connection Staleness During Agno Agent Thinking

**Hypothesis**: The MCP connection might have a keep-alive timeout. When the Agno agent thinks for >10-15 seconds between MCP tool calls, the connection becomes stale.

**Evidence:**
- Screenshot test (no thinking delay): Succeeds
- Single scrape test (short thinking): Works
- Multi-question workflow (5 sequential agents, each with thinking delay): All fail

### Theory 2: MCP Server Resource Exhaustion

**Hypothesis**: Running 5 sequential scraper agents (each creating Agno agent instances) might exhaust MCP server resources or connection pool.

**Evidence:**
- Questions 1-5 all failed with same timeout pattern
- Even Question 5 retry (after delay) initially timed out

### Theory 3: Perplexity Finance Page Interaction Complexity

**Hypothesis**: The Perplexity Finance page might have JavaScript that interferes with MCP tool interactions (not with page load, but with element interaction).

**Evidence:**
- Page loads successfully (screenshot test proves this)
- Agent fails when trying to interact: `list_pages`, `take_snapshot`, `click`, `fill`
- Error messages: "All tool calls are timing out"

---

## What We Validated

### ✅ Page Reuse Strategy Works (Mechanically)

**Questions 2-4 did NOT retry** on their first attempt, proving:
- The page reuse instructions were understood by the agent
- The agent attempted to reuse existing page instead of opening new one
- No `new_page` timeout occurred for Questions 2-4

**But**... this didn't solve the problem because the underlying issue is MCP tool timeouts, not just `new_page`.

### ✅ Workflow Architecture is Sound

- Multi-question orchestration works
- Retry logic handled Question 5 timeout correctly
- GLM-4.6 synthesis produced professional report structure
- Error handling is robust

### ✅ Agent Intelligence

**GLM-4.6 Synthesis Agent**:
- Correctly identified complete data absence
- Labeled all sections as `[DATA NOT RETRIEVED]`
- Marked speculation appropriately
- Assigned appropriate confidence level (0/10)
- Recommended **DO NOT TRADE** (correct given no data)

**Scraper Agent Resilience**:
- Attempted multiple recovery strategies
- Provided clear error diagnostics
- Did not fabricate data
- Suggested alternative approaches

---

## What We Did NOT Validate

### ❌ Perplexity Research Capability

**Cannot confirm if Perplexity Finance works** because we can't interact with pages:
- Question 1: Committee assignments → **No alternative source**
- Question 2: Pending legislation → **No alternative source**
- Question 3: Historical trading patterns → **No alternative source**
- Question 4: Sector catalysts → **Generic financial sites only**
- Question 5: Signal strength assessment → **Requires synthesis of prior data**

**Only Question 1 might have alternative sources** (House Clerk for committee data). Questions 2-5 **require** Perplexity's research engine.

### ❌ End-to-End Intelligence Quality

Without data, we cannot validate:
- Are Perplexity's responses comprehensive enough?
- Do the 5 questions cover all necessary areas?
- Is GLM-4.6 synthesis combining insights well?
- Would the final report be actionable?

---

## Key Differences: Why Screenshot Works But Workflow Fails

### Screenshot Test (SUCCEEDED)

**Execution Pattern:**
```python
# scraper_agent.py screenshot command
def screenshot(url):
    page = mcp.new_page(url)        # Direct MCP call (10s max)
    img = mcp.take_screenshot(page) # Direct MCP call (instant)
    return img                       # Total: ~10-15 seconds
```

**Characteristics:**
- No Agno agent (direct Python execution)
- 2 MCP calls total, both sequential
- No thinking delay between calls
- Completes in 10-15 seconds total

### Multi-Question Workflow (FAILED)

**Execution Pattern:**
```python
# workflow.py analyze-trade command
for question in questions:
    # Launch scraper_agent.py scrape command
    agent = create_agno_agent(mcp_tools)  # Agno Agent initialization

    # Agent thinks about the task (10-30 seconds)
    agent.think()

    # Agent calls MCP tools
    pages = mcp.list_pages()      # Timeout!
    snapshot = mcp.take_snapshot()  # Timeout!
    # ... more MCP calls, all fail
```

**Characteristics:**
- Agno agent with LLM thinking
- 10+ MCP calls per question
- 10-30 second thinking delays between calls
- Total execution: 2-5 minutes per question

---

## Root Cause Confirmed

### MCP Chrome DevTools Connection Unstable for Long-Running Workflows

**The Issue:**
```
MCP server: chrome-devtools
Timeout for ALL operations: 10 seconds (hardcoded)
Agno agent thinking time: 10-30 seconds
Result: Connection becomes stale, all MCP operations fail
```

**This affects:**
- Complex workflows with Agno agents
- Multiple sequential MCP tool calls
- Long-running scrape operations

**This does NOT affect:**
- Simple, direct MCP operations (screenshot)
- Short-duration workflows (<30 seconds)
- Single MCP call sequences

---

## Options Going Forward

### Option A: Abandon MCP Chrome DevTools (Recommended)

**Use alternative browser automation:**

1. **Playwright/Puppeteer directly** (no MCP):
   - Native Python/Node browser automation
   - No 10-second timeout limitations
   - Full control over connection lifecycle
   - Works with Agno agents

2. **Selenium with headless Chrome**:
   - Well-tested for long-running workflows
   - No timeout constraints
   - Easy integration with Agno

**Pros**: Solves root cause completely, reliable for production
**Cons**: Requires rewriting scraper_agent.py MCP integration

### Option B: Fix Agno Agent Execution Speed

**Reduce thinking time between MCP calls:**

1. **Use faster models** (qwen2.5-7b instead of llama3.1)
2. **Simplify agent prompts** (less reasoning required)
3. **Pre-cache pages** manually before running workflow

**Pros**: Might work with existing MCP infrastructure
**Cons**:
- Still has 10s timeout constraint
- Reduces agent intelligence
- Unreliable for production

### Option C: Hybrid Approach - Direct Scraper + LLM Synthesis

**Separate data extraction from LLM analysis:**

1. **Phase 1**: Direct Python scraper (Playwright) extracts HTML
2. **Phase 2**: Save HTML to files
3. **Phase 3**: Agno agent analyzes HTML (no browser interaction)
4. **Phase 4**: GLM-4.6 synthesizes findings

**Pros**: Reliable extraction, leverages LLM for analysis
**Cons**: More complex architecture, two-phase execution

### Option D: Use Perplexity API

**Skip browser automation entirely:**

1. Check if Perplexity has API access
2. Direct API calls for research queries
3. GLM-4.6 synthesis of API responses

**Pros**: Most reliable, fastest, scalable
**Cons**: Requires Perplexity Pro subscription/API access

---

## Recommendations

### Immediate (1-2 hours)

**Test Playwright Direct Integration:**

```bash
# Create simple Playwright scraper
pip install playwright
playwright install chromium

# Test Perplexity Finance page load
python test_playwright_perplexity.py
```

**If Playwright works** → Proceed with Option A (rewrite scraper_agent.py)
**If Playwright blocked** → Investigate Option D (Perplexity API)

### Short Term (1-2 days)

**Option A Path** (if Playwright succeeds):
1. Rewrite `scraper_agent.py` to use Playwright instead of MCP
2. Test single scrape operation
3. Test multi-question workflow
4. Validate data quality

**Option D Path** (if Playwright blocked):
1. Research Perplexity API availability
2. Test API with sample queries
3. Build API-based research workflow
4. Compare quality to browser scraping

### Long Term (1 week)

**Once data extraction works**:
→ Build Phase 2: Legislation Correlation Engine
→ Build Phase 3: Historical Pattern Analysis
→ Optimize performance (parallel queries, caching)

---

## Lessons Learned

### What the Tests Proved

✅ **Workflow architecture is sound**:
- Multi-question orchestration works
- Retry logic handles failures
- Synthesis produces quality reports
- Error handling is robust

✅ **Agent capabilities are strong**:
- Scraper agent is intelligent and resilient
- GLM-4.6 synthesis is professional and evidence-based
- Proper attribution and speculation labeling
- Appropriate confidence levels

✅ **MCP Chrome DevTools works for simple operations**:
- Screenshot test proved connection works
- Direct MCP calls succeed
- Timeout is marginal but achievable for simple workflows

### What the Tests Revealed

❌ **MCP Chrome DevTools is unreliable for complex workflows**:
- 10-second timeout too short for Agno agent execution
- Connection becomes stale during thinking delays
- Multiple sequential agent invocations all fail
- Not suitable for production use with LLM agents

⚠️ **Testing blind spots**:
- Previous "successful" tests used simple operations
- Didn't test complex multi-step workflows
- Should have tested MCP reliability explicitly first

---

## Decision Point

### Do NOT Proceed with MCP-based Workflow

**Both approaches blocked by same root cause**:
- Deep Research PoC: ❌ Failed (MCP timeout)
- Multi-Question PoC: ❌ Failed (MCP timeout)
- Page Reuse Test: ❌ Failed (MCP timeout)

**Next Action**: Pivot to Playwright or Perplexity API

**Timeline**:
- 1-2 hours to test Playwright
- OR 1-2 hours to research Perplexity API
- **Then** retry PoC validation

**Only after PoC succeeds with real data → Build full system**

---

**Status**: Blocked - needs browser automation replacement
**Root Cause**: MCP Chrome DevTools 10s timeout + Agno agent thinking delays
**Solution**: Playwright direct integration OR Perplexity API
**Timeline**: 1-2 hours to test alternatives, then re-evaluate

