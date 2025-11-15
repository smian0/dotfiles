# Deep Research Proof of Concept - Test Plan

## What We're Testing

Can the scraper successfully navigate Perplexity's Deep Research mode and extract comprehensive multi-source analysis?

## Test Command

```bash
cd /Users/smian/dotfiles/tools/scraper/tools/scraper/tools/scraper/agno_workflows/politician_trades_workflow
./workflow.py deep-research "Donald S. Beyer Jr." "GDXJ"
```

## What Should Happen

### Step 1: Navigation (0-30s)
```
🔬 Starting Deep Research analysis...
Politician: Donald S. Beyer Jr.
Ticker: GDXJ

🔬 Initiating Deep Research mode...
⏱️  This may take 5-10 minutes for comprehensive analysis...
```

### Step 2: Scraper Actions (30s-5min)
The scraper should:
1. Navigate to https://www.perplexity.ai
2. Find and click "Deep Research" button/mode
3. Enter the comprehensive research query
4. Wait for multi-step research to complete
5. Extract the synthesized report

### Step 3: Success Output (5-10min)
```
✅ Deep Research analysis completed!

================================================================================
[Comprehensive multi-source report with:]
- Politician background and committee assignments
- Trade timing and sector analysis
- Pending legislation correlation
- Historical trading patterns
- Sector catalysts and outlook
- Risk assessment
- Recommended action
[With citations and sources]
================================================================================

📄 Full report saved to: /tmp/donald_s._beyer_jr._gdxj_deep_research.json
```

## What Could Go Wrong

### Failure Scenario 1: Deep Research UI Not Found
```
❌ Deep Research failed: Could not find "Deep Research" button or mode
```

**Diagnosis**: Perplexity UI may have changed, or Deep Research requires Pro subscription

**Next Steps**:
- Manually check https://www.perplexity.ai for Deep Research availability
- Try alternative approaches (regular search with detailed prompts)

### Failure Scenario 2: Timeout
```
❌ Deep Research timed out after 10 minutes

This might indicate:
  - Deep Research mode is taking longer than expected
  - The scraper couldn't find Deep Research UI elements
  - Network or browser issues
```

**Diagnosis**: Research query too complex or network issues

**Next Steps**:
- Increase timeout to 15-20 minutes
- Simplify research query
- Check if Deep Research mode activated successfully

### Failure Scenario 3: Incomplete Extraction
```
✅ Deep Research analysis completed!
[But output is truncated or missing sections]
```

**Diagnosis**: Report extraction incomplete

**Next Steps**:
- Check if full report needs scrolling to view
- Verify extraction prompt captures all content
- May need iterative extraction for long reports

### Failure Scenario 4: Ollama Crash
```
⚠️ Ollama crash detected (attempt 1/3), retrying in 10s...
```

**Expected**: Retry logic should handle this automatically

## Success Criteria

### Minimum Viable (PoC Passes)
- ✅ Successfully navigates to Deep Research mode
- ✅ Submits research query
- ✅ Extracts some form of multi-source analysis
- ✅ Output is more comprehensive than basic Q&A

### Ideal (Ready for Phase 1)
- ✅ Full structured report with all 5 research sections
- ✅ Proper citations and source attribution
- ✅ Execution time under 10 minutes
- ✅ Consistent success rate (3/3 test runs)

## What We'll Learn

### If Successful
1. **Deep Research works** → Proceed to Phase 1 implementation
2. **Execution time** → Determine if 30-45min full workflow is acceptable
3. **Output quality** → Validate if Deep Research adds value vs. basic Q&A
4. **Reliability** → Check Ollama crash frequency, timeout issues

### If Fails
1. **Why it failed** → UI incompatibility, timeout, extraction issues?
2. **Can we fix it?** → UI changes needed, longer timeout, different approach?
3. **Alternative approaches** → Use multiple basic queries instead of Deep Research?

## Test Case: Beyer + GDXJ

### Why This Test Case?

**Known Information** (from earlier tests):
- Beyer is on Ways & Means Committee (Trade subcommittee)
- He purchased GDXJ (gold miners ETF)
- Committee has jurisdiction over trade policy
- Potential correlation with critical minerals legislation

**What Deep Research Should Add**:
- Specific pending bills and hearing dates
- Historical context of Beyer's trading patterns
- Sector outlook for gold miners
- Risk assessment and timing considerations
- Citations for all claims

### Comparison Baseline

**Basic Committee Lookup** (current system):
```
Committees: Ways & Means, Joint Economic
Subcommittees: Trade, Tax
Simple correlation: Trade jurisdiction → gold miners
```

**Deep Research** (target output):
```
Full Background: Beyer's committee power, recent activity, voting record
Trade Context: When purchased, market sentiment, timing significance
Legislation: H.R. 2345 (Critical Minerals Act) in committee, hearing Nov 18
Historical: Past trades in commodities, 75% success rate
Catalysts: Fed policy, China trade restrictions, EPA regulations
Risk: Legislation could stall, gold macro weakness
Action: BUY at $31.50-$32.00, target $36-$38.50 (60-90 days)
Citations: 15-30 sources
```

**Value Add**: 10x more actionable intelligence

## Next Steps After PoC

### If PoC Succeeds
1. **Refine the research query** - Optimize for best output
2. **Test additional cases** - MTG + COIN, McClain Delaney + ESCO
3. **Build Phase 1** - Integrate Deep Research into main workflow
4. **Optimize performance** - Parallel research, caching, etc.

### If PoC Needs Iteration
1. **Diagnose failure mode** - UI, timeout, extraction?
2. **Adjust approach** - Different prompts, longer timeout, fallback strategy
3. **Retest** - Validate fixes work
4. **Document workarounds** - Known issues and solutions

### If PoC Fails Completely
1. **Document why** - Technical limitations, subscription requirements, etc.
2. **Alternative approach** - Multiple targeted queries instead of Deep Research
3. **Re-evaluate design** - Can we achieve similar quality without Deep Research?

## Expected Timeline

**Best Case**: 10 minutes execution, immediate success
**Likely Case**: 10-15 minutes execution, 1-2 iterations to fix issues
**Worst Case**: Multiple failures, need to redesign approach (1-2 hours debugging)

---

**Status**: Ready to test
**Next Action**: Run `./workflow.py deep-research "Donald S. Beyer Jr." "GDXJ"`
