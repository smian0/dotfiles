# Why OllamaWebTools Returns Massive Responses

**Question:** Why is the returned data massive? Is it because the full article is being fetched?

**Answer:** YES - essentially the full article (or large excerpts) are included in each citation's `text` field.

---

## Real Test Data

### Query: "S&P 500 October 13 2025"

**Configuration:**
- `max_results=3`
- `strict=False`

**Response Size:**
```
Total size: 2,359,357 characters (2.3 MB!)
Total sources: 3
Total grounded facts: 122
Number of results: 3
```

### Breakdown by Result

**Result #1:** CNBC article
- URL: `https://www.cnbc.com/2025/10/13/stock-market-today-live-updates.html`
- Grounded facts: 64
- **First citation text: 16,513 characters** (16 KB for ONE citation)

**Result #2:** Investopedia article
- URL: `https://www.investopedia.com/dow-jones-today-10132025-11828817`
- Grounded facts: 56
- **First citation text: 20,077 characters** (20 KB for ONE citation)

---

## What's Inside the Citation Text?

The `text` field in each citation contains **large excerpts from the source web page**, including:

### 1. Article Content
- Full paragraphs and sections
- Related information beyond the specific fact
- Context around the answer

### 2. Page Structure (in some cases)
- Navigation menus
- Sidebar content
- Related articles
- Ads and sponsored content
- Footer information

### 3. Metadata & Context
- Methodology descriptions
- Data source explanations
- Timestamp and author info
- Related links and references

### Example from CNBC Citation (16,513 chars)

**First 300 characters:**
```
Traders work at the New York Stock Exchange on Oct. 1, 2025. NYSE The Dow Jones
Industrial Average and S&P 500 staged a big comeback on Tuesday, clawing back major
losses from earlier in the day, as investors tried to look past the latest worries
around U.S.-China trade. The Dow was last up 391...
```

The citation continues for **16,513 characters** with:
- Full market analysis
- Multiple paragraphs about trading activity
- Sector performance details
- Analyst quotes
- Related market news
- Company-specific updates

---

## Why This Causes Problems

### Size Explosion with Multiple Facts

For a query with `max_results=10` (default):

```
10 results × ~50 grounded facts per result × ~15,000 chars per citation
= 7,500,000 characters (7.5 MB)
```

This exceeds the LLM's input token limit, causing "request body too large" errors.

### Example Progression

| max_results | Facts | Est. Size | Agno Result |
|-------------|-------|-----------|-------------|
| 1 | 20-40 | 300-600 KB | ⚠️ May work |
| 3 | 60-120 | 900 KB - 1.8 MB | ⚠️ May work |
| 5 | 100-200 | 1.5-3 MB | ❌ Likely fails |
| 10 | 200-400 | 3-6 MB | ❌ Definitely fails |

---

## Why OllamaWebTools Does This

### Purpose: Grounding with Context

OllamaWebTools provides **grounded facts** - factual claims backed by source citations. The extensive citation text is meant to:

1. **Provide context** for the fact
2. **Allow verification** of the claim
3. **Enable the LLM to understand** the surrounding information
4. **Support follow-up queries** without additional web requests

### Trade-off: Context vs. Size

The design prioritizes **rich context** over **compact responses**:

- ✅ **Benefit:** More information for the LLM to reason about
- ✅ **Benefit:** Can answer follow-up questions from cached data
- ❌ **Problem:** Massive token consumption
- ❌ **Problem:** Exceeds LLM input limits
- ❌ **Problem:** Most context is irrelevant to the specific query

---

## How CompactOllamaWeb Solves This

### Aggressive Truncation Strategy

```python
# Original response
citation_text: 16,513 characters

# After CompactOllamaWeb truncation (max_citation_chars=150)
citation_text: 150 characters + "[truncated 16,363 chars]"
```

### Size Reduction Results

**Query:** "NASDAQ Composite 2025-10-14"

```
Before: 876,874 chars (876 KB)
After:  1,530 chars (1.5 KB)
Reduction: 99.83%
```

**Query:** "S&P 500 October 13 2025"

```
Before: 645,844 chars (645 KB)
After:  1,356 chars (1.4 KB)
Reduction: 99.79%
```

### Multi-Level Truncation

1. **Limit results:** 10 → 1 result
2. **Limit facts:** 50+ → 2 facts per result
3. **Limit citations:** Multiple → 1 citation per fact
4. **Truncate text:** 15,000+ → 150 chars per citation

---

## Is This a Bug or Feature?

### It's a Design Choice

**OllamaWebTools design:**
- Optimized for **comprehensive context**
- Assumes LLMs have **large context windows**
- Designed for **research and deep analysis**

**Real-world reality:**
- LLM input limits are **hard constraints**
- Most context is **not needed** for specific queries
- Financial queries need **specific numbers**, not full articles

### Not Unique to OllamaWebTools

Other web search APIs have similar issues:
- **Google Custom Search:** Returns full snippets and descriptions
- **Bing Web Search:** Includes extensive metadata and context
- **Perplexity:** Provides detailed citations

The difference is that OllamaWebTools is particularly **generous with context**, leading to larger responses.

---

## Alternative Approaches

### 1. Use fetch() Instead of search()

```python
web_tools.fetch(urls=["https://www.example.com"])
```

**Pros:**
- Returns structured data from specific URLs
- Can be more targeted

**Cons:**
- Requires knowing the URL in advance
- Currently has bugs in OllamaWebTools implementation

### 2. Reduce max_results Drastically

```python
web_tools.search(query="...", max_results=1)
```

**Pros:**
- Simple parameter change
- Still gets too much data per result

**Cons:**
- Still returns 300-600 KB for 1 result
- May miss relevant sources

### 3. CompactOllamaWeb Subclass (Our Solution)

```python
CompactOllamaWeb(
    max_results=1,
    max_citation_chars=150
)
```

**Pros:**
- **99%+ size reduction**
- Prevents token overflow
- Preserves Agno tool registration
- Works across all queries

**Cons:**
- May lose specific data in truncation
- Requires more iterations to extract numbers

---

## Comparison: With vs. Without Truncation

### Without Truncation

```
Query: "S&P 500 October 13 2025"
max_results: 3

Response: 2,359,357 chars (2.3 MB)
Result: HTTP 400 "request body too large"
Agent behavior: Fails or hallucinates
```

### With CompactOllamaWeb

```
Query: "S&P 500 October 13 2025"
max_results: 1
max_citation_chars: 150

Response: 1,356 chars (1.4 KB)
Result: Success, no errors
Agent behavior: Real data, no hallucinations
```

---

## Recommendations

### For Financial Data Queries

Use **adaptive truncation** based on query type:

```python
# For price/number queries - slightly more generous
CompactOllamaWeb(
    max_results=1,
    max_citation_chars=250  # Enough to capture prices
)

# For general research - very compact
CompactOllamaWeb(
    max_results=1,
    max_citation_chars=100  # Just basic context
)
```

### For Future Improvements

1. **Smart truncation:** Preserve numerical data and dates
2. **Semantic chunking:** Keep relevant paragraphs, drop navigation
3. **Progressive truncation:** Try larger chunks first, truncate if needed
4. **Structured extraction:** Parse specific data patterns (prices, dates)

---

## Summary

**Q: Why is the returned data massive?**

**A: Yes, because each citation includes large excerpts (15-20 KB) from the source web page, not just relevant snippets.**

**For a typical search:**
- 3 results × 60 facts × 15 KB per citation = **2.3 MB**
- 10 results × 200 facts × 15 KB per citation = **30+ MB**

**Solution:** CompactOllamaWeb truncates citations to 150-250 chars, achieving **99%+ size reduction** while maintaining source authenticity and preventing hallucinations.

**Trade-off:** Agent may need multiple search iterations to extract specific numbers, but this is an **efficiency issue, not a hallucination risk**.

---

**Last Updated:** October 14, 2025
**Verified with:** Real OllamaWebTools.search() responses
