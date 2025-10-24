# Raw Data Directory - Audit Trail Documentation

This directory contains the raw, unprocessed data from Perplexity queries used to create daily stock updates. The purpose is to maintain full auditability and transparency between what Perplexity provides and what Claude Code synthesizes.

## Directory Structure

```
raw-data/
├── YYYY-MM-DD/                          # Date-specific folder for each research session
│   ├── 01-query.md                      # Exact query sent to Perplexity
│   ├── 02-perplexity-response.md        # Raw response from Perplexity (unmodified)
│   ├── 03-snapshot-pre.json             # (Optional) Page snapshot before query
│   ├── 04-snapshot-post.json            # (Optional) Page snapshot after response
│   └── metadata.json                    # Session metadata (timestamps, UIDs, tools used)
└── README.md                            # This file
```

## File Descriptions

### 01-query.md
**Purpose:** Preserve the exact query sent to Perplexity AI.

**Contents:**
- Full query text with all parameters filled in
- Entry zone parameters used
- Earnings dates referenced
- Template structure used
- Timestamp when query was submitted

**Why Important:** Allows reproduction of the exact same query if needed. Shows what specific information was requested.

### 02-perplexity-response.md
**Purpose:** Store Perplexity's complete, unmodified response.

**Contents:**
- Full response text extracted from Perplexity page
- Summary section (if Perplexity provides one)
- List of sources cited by Perplexity
- Extraction metadata (how the response was captured)

**Why Important:** This is the **source of truth**. Compare this against the daily-update file to see what Claude synthesized vs what Perplexity actually said. Critical for debugging misinterpretations.

### 03-snapshot-pre.json (Optional)
**Purpose:** Capture page state before submitting query.

**Contents:**
- Full JSON snapshot from MCP comet-devtools
- All UIDs, element types, text content
- Page structure at time of query

**Why Important:** Useful for debugging if queries fail or UIDs change unexpectedly. Can be omitted to save space.

### 04-snapshot-post.json (Optional)
**Purpose:** Capture page state after Perplexity responds.

**Contents:**
- Full JSON snapshot including Perplexity's response
- All response elements with UIDs
- Complete page structure

**Why Important:** Can be used to re-extract data if initial extraction was incomplete. Can be omitted to save space.

### metadata.json
**Purpose:** Record all session metadata for reproducibility.

**Contents:**
- Session timestamp and ID
- Stock information (ticker, entry zone, earnings date)
- Perplexity session details (URL, UIDs used)
- MCP tools invoked
- Data sources cited
- Processing timestamps
- File references

**Why Important:** Provides complete context for the research session. Links all files together. Enables debugging of workflow issues.

## Workflow Integration

### When Raw Data is Created
Raw data is generated during **Step 8** of the daily update workflow (after Step 7: Take snapshot after response).

### Standard Process
1. **Query Perplexity** (Steps 1-7 in CLAUDE.md)
2. **Save Raw Data** (Step 8 - NEW)
   - Create `raw-data/YYYY-MM-DD/` folder
   - Save query as `01-query.md`
   - Extract and save Perplexity response as `02-perplexity-response.md`
   - Generate `metadata.json` with session info
   - (Optional) Save snapshots as JSON
3. **Create Daily Update** (Step 9)
   - Synthesize raw response into structured daily-update.md
   - Add audit trail section linking to raw data

## Auditability Benefits

### Transparency
- **Clear Separation:** Raw Perplexity data vs Claude's analysis
- **Verifiable Claims:** Check if Claude correctly interpreted data
- **Human Review:** Anyone can read raw response without re-running queries

### Reproducibility
- **Query Preservation:** Can re-run exact same query
- **Response Archive:** Raw response preserved even if Perplexity changes
- **Timestamp Trail:** Know exactly when data was collected

### Debugging
- **Error Isolation:** Identify if issue is:
  - (a) Bad query
  - (b) Perplexity error/incomplete response
  - (c) Claude misinterpretation
- **Diff Tracking:** Compare responses over time
- **Source Verification:** Trace claims back to Perplexity sources

## File Size Guidelines

### Storage Estimates
- **01-query.md:** ~1-2 KB (text)
- **02-perplexity-response.md:** ~5-20 KB (depends on response length)
- **metadata.json:** ~1-2 KB (JSON)
- **Snapshots (optional):** ~50-200 KB each (JSON)

**Total per session:**
- Without snapshots: ~10-25 KB
- With snapshots: ~100-400 KB

### Annual Storage (4 stocks × 250 trading days)
- Without snapshots: ~10-25 MB per year
- With snapshots: ~100-400 MB per year

**Recommendation:** Skip snapshots (03/04) unless debugging specific issues. Keep query + response + metadata only.

## Git Best Practices

### What to Commit
- ✅ `01-query.md` (small, valuable)
- ✅ `02-perplexity-response.md` (source of truth)
- ✅ `metadata.json` (session context)
- ⚠️ Snapshots (large, consider .gitignore)

### .gitignore Pattern (Optional)
If snapshots become too large:
```gitignore
# Ignore large snapshot files
research/stocks/**/raw-data/**/03-snapshot-pre.json
research/stocks/**/raw-data/**/04-snapshot-post.json
```

## Example: Comparing Raw vs Synthesis

### Scenario
Daily update says: "RSI is 64.66, neutral leaning bullish"

### Audit Process
1. Open `02-perplexity-response.md`
2. Search for "RSI" in Perplexity's response
3. Verify Perplexity actually said "64.66"
4. Check if "neutral leaning bullish" interpretation is justified
5. If mismatch found, file can be updated or issue noted

## Maintenance

### Retention Policy
- **Keep:** All raw data for current month + previous 2 months (active trading)
- **Archive:** Data older than 3 months can be compressed or moved to backup
- **Delete:** No automatic deletion - data is valuable for backtesting strategies

### Directory Cleanup
```bash
# Example: Archive old raw data (older than 90 days)
find ~/dotfiles/research/stocks/**/raw-data -type d -mtime +90 -exec tar -czf {}.tar.gz {} \;
```

## Future Enhancements

### Potential Additions
1. **Diff Tool:** Script to compare daily responses over time
2. **Query Templates:** Library of proven query structures
3. **Source Validation:** Cross-check Perplexity sources against original data
4. **Automated Backfill:** Script to recreate raw data from existing daily updates (if conversation history available)

---

**Last Updated:** October 6, 2025
**Maintained By:** Claude Code (automated workflow)
**Questions?** See main [CLAUDE.md](../../CLAUDE.md) for workflow details
