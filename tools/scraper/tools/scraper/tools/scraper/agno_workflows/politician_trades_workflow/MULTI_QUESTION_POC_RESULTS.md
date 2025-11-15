# Multi-Question Alternative Approach - PoC Results

**Test Date**: 2025-11-11
**Test Case**: Donald S. Beyer Jr. + GDXJ
**Approach**: 5 targeted questions on Finance page + GLM-4.6 synthesis
**Status**: ❌ Failed - Same root cause as Deep Research PoC

---

## What Happened

### Execution
- ✅ Workflow executed successfully (exit code 0)
- ✅ All 5 questions ran
- ✅ Retry logic handled Question 4 timeout
- ✅ GLM-4.6 synthesis produced professional report
- ❌ **All questions failed to retrieve data from Perplexity**

### Error Pattern

**Every question encountered the same timeout**:
```
"Timed out while waiting for response to ClientRequest. Waited 10.0 seconds."
```

**Agent responses across all 5 questions**:
- "I'm experiencing network connectivity issues"
- "All browser tool calls are timing out"
- "Cannot create new pages or navigate to URLs due to timeout errors"

### Synthesis Output

GLM-4.6 successfully synthesized a professional intelligence report, but correctly identified the data gap:

**Key sections**:
- ✅ Proper structure (8 sections as designed)
- ✅ Professional formatting and tone
- ✅ **Honest acknowledgment**: `[DATA NOT RETRIEVED]` throughout
- ✅ Signal Strength: **INCONCLUSIVE** (1/10 confidence)
- ✅ Recommendation: **DO NOT TRADE**

---

## Root Cause Analysis

### The Real Problem: MCP Timeout

**MCP chrome-devtools `new_page` has 10-second timeout**:
- Perplexity pages take >10 seconds to load
- **Every** page load attempt times out
- This affects BOTH main page AND Finance subdomain

### Evidence Comparison

**Deep Research PoC** (failed):
- ❌ Timed out loading https://www.perplexity.ai main page

**Multi-Question Approach** (failed):
- ❌ Timed out loading https://www.perplexity.ai/finance/politicians (all 5 attempts)

**Committee Lookup** (appeared to succeed):
- ❌ Timed out on Perplexity
- ✅ Pivoted to House Clerk website (clerk.house.gov)
- ✅ Extracted committee data from alternative source

### Pattern

**Previous "successful" tests**:
- AAPL screenshot test
- NVDA Q&A test
- Committee lookup test

**All of these likely either**:
1. Had pages already open from previous sessions, OR
2. Successfully pivoted to alternative sources (like House Clerk)

**They did NOT prove Perplexity works** - they proved the scraper agent is resilient and finds workarounds!

---

## What We Validated

### ✅ Workflow Design

**Multi-Question Architecture Works**:
- 5 questions executed sequentially
- Retry logic handled timeouts correctly
- Phase 1 → Phase 2 transition worked
- GLM-4.6 synthesis produced quality output

**Report Quality**:
- Professional 8-section structure
- Clear data attribution (or lack thereof)
- Appropriate risk assessment
- Evidence-based recommendations
- No hallucination or speculation without labeling

### ✅ Agent Intelligence

**GLM-4.6 Synthesis Agent**:
- Correctly identified complete data absence
- Labeled all sections as `[DATA NOT RETRIEVED]`
- Marked speculation as `[SPECULATION]`
- Assigned appropriate confidence level (1/10)
- Recommended DO NOT TRADE (correct given no data)

**Scraper Agent Resilience**:
- Attempted multiple recovery strategies
- Provided clear error diagnostics
- Suggested alternative approaches
- Did not fabricate data

---

## What We Did NOT Validate

### ❌ Perplexity Research Capability

**Cannot confirm if Perplexity Finance works** because we can't load pages:
- Question 1: Committee assignments (House Clerk works, but not Perplexity)
- Question 2: Pending legislation (NO alternative source)
- Question 3: Historical trading patterns (NO alternative source)
- Question 4: Sector catalysts (generic financial sites, not politician-specific)
- Question 5: Signal strength assessment (requires synthesis of prior data)

**Only Question 1 has an alternative source**. Questions 2-5 **require** Perplexity's research engine.

### ❌ End-to-End Intelligence Quality

Without data, we cannot validate:
- Are Perplexity's responses comprehensive enough?
- Do the 5 questions cover all necessary areas?
- Is GLM-4.6 synthesis combining insights well?
- Would the final report be actionable?

---

## Root Cause Confirmed

### MCP Chrome DevTools Timeout Too Short

**The Issue**:
```python
# MCP server: chrome-devtools
# Default timeout for new_page: 10 seconds
# Perplexity page load time: >10 seconds
# Result: All page loads fail
```

**This affects**:
- Deep Research approach (main page)
- Multi-Question approach (Finance page)
- ANY Perplexity page navigation

**This does NOT affect**:
- Pages already open in Comet browser
- Fast-loading sites (e.g., House Clerk)
- Sites that load in <10 seconds

---

## Comparison: Deep Research vs Multi-Question

### Both Approaches Failed for Same Reason

| Aspect | Deep Research PoC | Multi-Question PoC |
|--------|------------------|-------------------|
| **Page to Load** | perplexity.ai | perplexity.ai/finance/politicians |
| **Timeout Error** | ✅ Yes (main page) | ✅ Yes (all 5 questions) |
| **Root Cause** | MCP 10s timeout | MCP 10s timeout |
| **Workaround Found** | ❌ No | ❌ No |
| **Alternative Approach** | ❌ None available | ⚠️ Partial (Q1 only) |

**Conclusion**: Neither approach works until MCP timeout is fixed.

---

## Options Going Forward

### Option A: Fix MCP Timeout (Recommended)

**Increase `new_page` timeout in chrome-devtools MCP server**:

1. Locate MCP server config (likely in `~/Library/Application Support/Claude/` or similar)
2. Find chrome-devtools server settings
3. Increase `timeout` parameter from 10s → 60s
4. Restart Claude Code
5. Retest both approaches

**Expected Result**:
- ✅ Perplexity pages load successfully
- ✅ Both Deep Research and Multi-Question work
- ✅ Can validate actual research quality

**Pros**: Solves root cause, unblocks both approaches
**Cons**: Requires MCP server configuration knowledge

### Option B: Use Alternative Research Sources

**Abandon Perplexity, use alternative sites**:

**For each question**:
1. Committee assignments → clerk.house.gov ✅
2. Pending legislation → congress.gov ⚠️ (generic, not analyzed)
3. Historical trades → quiverquant.com ⚠️ (may require subscription)
4. Sector outlook → finviz.com, seeking alpha ⚠️ (not politician-aware)
5. Signal strength → **Cannot assess without 2-4**

**Pros**: Works with existing infrastructure
**Cons**:
- Lose Perplexity's multi-source synthesis
- Questions 2-5 hard to answer without Perplexity
- Quality downgrade

### Option C: Manual Perplexity + Automated Synthesis

**Hybrid approach**:
1. User manually runs Perplexity queries
2. Copies responses to files
3. Workflow runs GLM-4.6 synthesis on manual data

**Pros**: Validates synthesis quality, unblocked immediately
**Cons**: Not fully automated, defeats purpose

### Option D: Build Perplexity API Integration

**Use Perplexity's API directly** (if available):
- Skip browser automation entirely
- Direct API calls for research
- Much faster, no timeout issues

**Pros**: More reliable, faster, scalable
**Cons**: Requires Perplexity API access (may need Pro subscription)

---

## Recommendations

### Immediate (1 hour)

**Investigate MCP timeout configuration**:
1. Find chrome-devtools MCP server config file
2. Check if timeout is configurable
3. Test increasing timeout to 60s
4. If successful → Retest Multi-Question PoC

**Command to find MCP configs**:
```bash
find ~/Library -name "*mcp*" -o -name "*chrome*" 2>/dev/null | grep -i config
```

### Short Term (1-2 days)

**If MCP fix succeeds**:
→ Retest Multi-Question PoC with working Perplexity
→ Validate research quality
→ Compare Deep Research vs Multi-Question outputs
→ Choose best approach and proceed

**If MCP fix blocked**:
→ Investigate Option D (Perplexity API)
→ OR build Option B (alternative sources)
→ OR abandon Perplexity-based approaches

### Long Term (1 week)

**Once research quality validated**:
→ Build Phase 2: Legislation Correlation Engine
→ Build Phase 3: Historical Pattern Analysis
→ Optimize performance (parallel queries, caching)

---

## Lessons Learned

### What the PoCs Proved

✅ **Workflow architecture is sound**:
- Multi-question orchestration works
- Retry logic handles transient failures
- Synthesis produces quality reports
- Error handling is robust

✅ **Agent capabilities are strong**:
- Scraper agent is intelligent and resilient
- GLM-4.6 synthesis is professional and evidence-based
- Proper attribution and speculation labeling
- Appropriate confidence levels

### What the PoCs Revealed

❌ **Infrastructure limitation**:
- MCP timeout is the blocker
- Not a design flaw, a configuration issue
- Fixable, but blocks both approaches

⚠️ **Testing blind spots**:
- Previous "successful" tests used workarounds
- Did not validate Perplexity actually works
- Should have tested page load explicitly first

---

## Decision Point

### Do NOT Proceed to Full Implementation

**Both approaches blocked by same root cause**:
- Deep Research PoC: ❌ Failed (timeout)
- Multi-Question PoC: ❌ Failed (timeout)

**Next Action**: Fix MCP timeout OR pivot to API approach

**Timeline**:
- 1-2 hours to investigate MCP fix
- OR 1-2 days to build API integration
- **Then** retry PoC validation

**Only after PoC succeeds with real data → Build full system**

---

**Status**: Blocked - needs MCP timeout fix
**Root Cause**: MCP `new_page` 10s timeout < Perplexity load time
**Solution**: Increase timeout to 60s OR use Perplexity API
**Timeline**: 1-2 hours to unblock, then re-evaluate
